"""The routing decision and its reason vocabulary — single source of truth.

Every rejection carries a reason CODE, not prose. An unexplained "no" is a log line, not
observability, and the first-class operational question here is *why nothing was proposed*
— so the negative path is more structured than the positive one, not less.

These codes are consumed by:
  * classifier/traced_classifier.py  (Python, traced to LangSmith)
  * n8n/build_workflow.py            (generates the JS guard in the n8n Code node)

so the n8n POC and the monitoring cannot describe the same rejection differently.
"""
from dataclasses import dataclass, asdict

# code -> what a handler is told when it fires
REASONS = {
    "OK_PROPOSED": "passed all checks",
    "REJECT_MALFORMED_OUTPUT": "model did not return valid JSON",
    "REJECT_QUEUE_NOT_IN_PRODUCT": "model proposed a queue that does not exist for this product",
    "REJECT_OUT_OF_TAXONOMY": "no queue on this product matches the complaint",
    "REJECT_LOW_CONFIDENCE": "confidence below the routing threshold",
    "REJECT_EVIDENCE_NOT_VERBATIM": "evidence quote is not verbatim from the complaint",
    "ERROR_MODEL_CALL": "the model call itself failed",
}

PROPOSE = "PROPOSE_TO_HANDLER"
HUMAN = "HUMAN_REVIEW"


@dataclass
class Decision:
    decision: str
    reason_code: str
    reason: str
    proposed_queue: str | None
    proposed_team: str
    confidence: float
    evidence: str
    evidence_is_verbatim: bool

    def as_dict(self) -> dict:
        return asdict(self)


def decide(*, narrative: str, product: str, queue: str, confidence: float, evidence: str,
           valid_queues: list[str], queue_to_team: dict, threshold: float,
           malformed: bool = False, call_failed: bool = False) -> Decision:
    """Apply the guards in a fixed, declared order. Order is part of the contract:
    a complaint rejected for two reasons is reported under the first one, always, so the
    reason-code distribution is stable and comparable across runs."""
    verbatim = bool(evidence) and evidence[:60].lower() in narrative.lower()
    queue_valid = queue in valid_queues
    team = queue_to_team.get(queue, HUMAN) if queue_valid else HUMAN

    if call_failed:
        code = "ERROR_MODEL_CALL"
    elif malformed:
        code = "REJECT_MALFORMED_OUTPUT"
    elif not queue_valid:
        code = "REJECT_QUEUE_NOT_IN_PRODUCT"
    elif queue == "OTHER":
        code = "REJECT_OUT_OF_TAXONOMY"
    elif confidence < threshold:
        code = "REJECT_LOW_CONFIDENCE"
    elif not verbatim:
        code = "REJECT_EVIDENCE_NOT_VERBATIM"
    else:
        code = "OK_PROPOSED"

    return Decision(
        decision=PROPOSE if code == "OK_PROPOSED" else HUMAN,
        reason_code=code, reason=REASONS[code],
        proposed_queue=queue if queue_valid else None,
        proposed_team=team if code == "OK_PROPOSED" else HUMAN,
        confidence=confidence, evidence=evidence, evidence_is_verbatim=verbatim)


# The guard order above, declared rather than inferred from observed behaviour.
GUARD_ORDER = ["ERROR_MODEL_CALL", "REJECT_MALFORMED_OUTPUT", "REJECT_QUEUE_NOT_IN_PRODUCT",
               "REJECT_OUT_OF_TAXONOMY", "REJECT_LOW_CONFIDENCE",
               "REJECT_EVIDENCE_NOT_VERBATIM", "OK_PROPOSED"]
