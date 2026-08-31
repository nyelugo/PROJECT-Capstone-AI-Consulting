"""The decision spine — one control structure, three capabilities.

Round 1 shipped a single capability: complaint triage. After the staff presentation the
scope widened to all three proposed use cases. The temptation was to build three
applications. This is the alternative, and it is the architectural claim the Round 2
presentation makes:

    validate input -> model proposes -> guards verify it is grounded -> a human confirms

Every capability is that shape. What differs between them is only what "grounded" means:

    triage     a routing queue,  grounded in a verbatim quote from the complaint
    reporting  a report sentence, grounded in figures this repo actually computed
    anomaly    an escalation,     grounded in the transaction record's own values

So adding a capability costs a prompt and a grounding check, not a new system. The input
contract, the guard order, the reason-code vocabulary, the error handling and the trace
record are written once, here, and cannot drift between capabilities.

The guard ORDER is part of the contract, not an implementation detail: a proposal that
fails two guards is always reported under the first one, so reason-code distributions stay
comparable across runs and across capabilities. This extends the vocabulary established in
`classifier/decide.py` for Round 1 rather than replacing it — the Round 1 codes still mean
what they meant, so Round 1 monitoring data and Round 2 monitoring data are comparable.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Protocol

PROPOSE = "PROPOSE_TO_HANDLER"
HUMAN = "HUMAN_REVIEW"

# One vocabulary. A rejection carries a CODE, never prose — an unexplained "no" is a log
# line, not observability. Codes marked (R1) are unchanged from classifier/decide.py.
REASONS: dict[str, str] = {
    "OK_PROPOSED": "passed all checks",
    # -- stage 1: the input contract, checked before a single token is spent
    "REJECT_INVALID_INPUT": "the request did not meet the input contract",
    # -- stage 2: the call
    "ERROR_MODEL_CALL": "the model call itself failed",                       # (R1)
    # -- stage 3: the shape of what came back
    "REJECT_MALFORMED_OUTPUT": "model did not return valid JSON",             # (R1)
    # -- stage 4: is the proposal even a thing that exists?
    "REJECT_QUEUE_NOT_IN_PRODUCT": "model proposed a queue that does not exist for this product",  # (R1)
    "REJECT_OUT_OF_TAXONOMY": "no queue on this product matches the complaint",  # (R1)
    "REJECT_METRIC_NOT_PUBLISHED": "model cited a metric this system does not compute",
    "REJECT_ACCOUNT_NOT_IN_LEDGER": "model referred to a transaction that is not in the batch",
    # -- stage 5: does the model itself think it knows?
    "REJECT_LOW_CONFIDENCE": "confidence below the routing threshold",        # (R1)
    # -- stage 6: is the proposal grounded in evidence that actually exists?
    "REJECT_EVIDENCE_NOT_VERBATIM": "evidence quote is not verbatim from the complaint",  # (R1)
    "REJECT_FIGURE_NOT_COMPUTED": "a figure in the narrative was not computed from the data",
    "REJECT_VALUE_MISMATCH": "a value cited does not match the transaction record",
}

# Declared, not inferred from observed behaviour. Read top to bottom.
GUARD_ORDER = [
    "REJECT_INVALID_INPUT",
    "ERROR_MODEL_CALL",
    "REJECT_MALFORMED_OUTPUT",
    "REJECT_QUEUE_NOT_IN_PRODUCT", "REJECT_OUT_OF_TAXONOMY",
    "REJECT_METRIC_NOT_PUBLISHED", "REJECT_ACCOUNT_NOT_IN_LEDGER",
    "REJECT_LOW_CONFIDENCE",
    "REJECT_EVIDENCE_NOT_VERBATIM", "REJECT_FIGURE_NOT_COMPUTED", "REJECT_VALUE_MISMATCH",
    "OK_PROPOSED",
]

STAGES = ["input", "call", "parse", "scope", "confidence", "grounding"]


@dataclass
class Decision:
    """What the system did, and why — the same record shape for all three capabilities.

    `decision` is deliberately only ever PROPOSE_TO_HANDLER or HUMAN_REVIEW. The system
    proposes; a person decides. There is no third value, in any capability, by design.
    """
    capability: str
    decision: str
    reason_code: str
    reason: str
    summary: str                      # what was proposed, in one line, for a human
    confidence: float | None
    citations: list[str] = field(default_factory=list)
    grounding_detail: str = ""
    payload: dict = field(default_factory=dict)
    failed_stage: str | None = None
    latency_ms: int = 0
    model: str = ""
    ref: str = ""                     # pseudonymous subject reference, never an identifier

    @property
    def proposed(self) -> bool:
        return self.decision == PROPOSE

    def as_dict(self) -> dict:
        return asdict(self)


class Capability(Protocol):
    """What a capability must supply. Everything else is the spine's job."""
    name: str
    title: str
    threshold: float
    model: str

    def validate(self, request: dict) -> str | None: ...
    def messages(self, request: dict) -> list[dict]: ...
    def parse(self, text: str) -> dict: ...
    def scope_check(self, parsed: dict, request: dict) -> str | None: ...
    def grounding_check(self, parsed: dict, request: dict) -> tuple[str | None, str]: ...
    def summarise(self, parsed: dict, request: dict) -> str: ...
    def citations(self, parsed: dict) -> list[str]: ...
    def ref(self, request: dict) -> str: ...


def _reject(cap: Capability, code: str, stage: str, *, t0: float,
            summary: str = "", confidence: float | None = None,
            payload: dict | None = None, detail: str = "", ref: str = "") -> Decision:
    return Decision(
        capability=cap.name, decision=HUMAN, reason_code=code, reason=REASONS[code],
        summary=summary or REASONS[code], confidence=confidence,
        grounding_detail=detail, payload=payload or {}, failed_stage=stage,
        latency_ms=int((time.monotonic() - t0) * 1000), model=cap.model, ref=ref)


def run(cap: Capability, request: dict, *, call) -> Decision:
    """Apply the six guards in order and return one Decision. Never raises.

    `call(messages, model) -> str` is injected rather than imported so the spine can be
    tested without a network, and so a capability cannot quietly use a different client.

    Every exit from this function is a Decision with a reason code. A capability that
    crashed and a capability that abstained are both *observable outcomes*, not gaps in the
    record — 'cannot tell' is not the same as 'nothing happened', and it must never look
    the same in monitoring.
    """
    t0 = time.monotonic()
    ref = ""

    # -- stage 1: input contract. Checked first, so a malformed request costs nothing.
    try:
        ref = cap.ref(request)
        invalid = cap.validate(request)
    except Exception as exc:                                    # a broken request, not a bug
        return _reject(cap, "REJECT_INVALID_INPUT", "input", t0=t0, detail=str(exc)[:300])
    if invalid:
        return _reject(cap, "REJECT_INVALID_INPUT", "input", t0=t0, detail=invalid,
                       summary=f"Not accepted: {invalid}", ref=ref)

    # -- stage 2: the call
    try:
        raw = call(cap.messages(request), cap.model)
    except Exception as exc:
        return _reject(cap, "ERROR_MODEL_CALL", "call", t0=t0,
                       detail=f"{type(exc).__name__}: {exc}"[:300], ref=ref)

    # -- stage 3: the shape of what came back
    try:
        parsed = cap.parse(raw)
    except Exception as exc:
        return _reject(cap, "REJECT_MALFORMED_OUTPUT", "parse", t0=t0,
                       detail=f"{type(exc).__name__}: {exc}"[:300],
                       payload={"raw": raw[:500]}, ref=ref)

    confidence = parsed.get("confidence")
    summary = cap.summarise(parsed, request)
    cites = cap.citations(parsed)

    def rej(code: str, stage: str, detail: str = "") -> Decision:
        d = _reject(cap, code, stage, t0=t0, summary=summary, confidence=confidence,
                    payload=parsed, detail=detail, ref=ref)
        d.citations = cites
        return d

    # -- stage 4: is the proposal a thing that exists?
    if (code := cap.scope_check(parsed, request)):
        return rej(code, "scope")

    # -- stage 5: does the model think it knows?
    if not isinstance(confidence, (int, float)):
        return rej("REJECT_MALFORMED_OUTPUT", "parse", "confidence was not a number")
    if confidence < cap.threshold:
        return rej("REJECT_LOW_CONFIDENCE", "confidence",
                   f"{confidence:.2f} < {cap.threshold:.2f}")

    # -- stage 6: is it grounded in evidence that actually exists?
    code, detail = cap.grounding_check(parsed, request)
    if code:
        return rej(code, "grounding", detail)

    return Decision(
        capability=cap.name, decision=PROPOSE, reason_code="OK_PROPOSED",
        reason=REASONS["OK_PROPOSED"], summary=summary, confidence=float(confidence),
        citations=cites, grounding_detail=detail, payload=parsed, failed_stage=None,
        latency_ms=int((time.monotonic() - t0) * 1000), model=cap.model, ref=ref)


def parse_json_object(text: str) -> dict:
    """Shared JSON parsing. Tolerates a fenced code block, nothing more.

    Deliberately strict beyond that: a model that wraps its answer in prose has not
    followed the contract, and papering over that with a regex hunt would hide a real
    failure mode from the reason-code distribution.
    """
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    obj = json.loads(t)
    if not isinstance(obj, dict):
        raise ValueError(f"expected a JSON object, got {type(obj).__name__}")
    return obj
