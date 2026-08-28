"""The triage classifier, instrumented for LangSmith.

Observability design (see langsmith/monitoring_notes.md for the reasoning):

* **Every decision is traced, including the ones where nothing happened.** The operational
  question is "why was this not routed?", so each run records a reason CODE from
  decide.py — never free prose, never a bare False.
* **Environment is part of identity, not a label.** Every run is tagged demo / eval /
  pilot / live, so an evaluation result can never be read as production behaviour.
* **No raw identifiers reach the trace.** The complaint id is pseudonymised with a salted
  hash *before* the run is created — not after, because by then it would already be sent.
* **Observing cannot affect the observed.** If LangSmith is unreachable or unconfigured,
  classification still returns normally. Tracing is best-effort and failures are swallowed.
* **Prompt provenance is recorded.** Each run carries a short hash of the exact system
  prompt, so a change in behaviour can be tied to a change in the prompt.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from openai import OpenAI

import decide as D
import prompt as P
import teams as T

ENV_FILE = Path.home() / ".config/ironhack/.env.local"
PROMPT_VERSION = hashlib.sha256(P.SYSTEM_PROMPT.encode()).hexdigest()[:12]
# Salt keeps the alias un-brute-forceable; the id space is small and public here, but the
# production equivalent is a customer reference, so the habit is built in from the start.
_SALT = os.environ.get("PSEUDONYM_SALT", "capstone-round1")


def _env(key: str) -> str | None:
    m = re.search(rf"^{key}=(.*)$", ENV_FILE.read_text(), re.M) if ENV_FILE.exists() else None
    return m.group(1).strip().strip('"').strip("'") if m else None


def configure_langsmith(project: str = "capstone-complaint-triage") -> bool:
    """Point the SDK at the EU workspace. Returns whether tracing is configured.

    Ugo's LangSmith workspace is EU-hosted: a key from it authenticates against the default
    US endpoint and then 403s on every call, which reads as a bad key rather than a wrong
    region. The endpoint is set explicitly for that reason.
    """
    key = _env("LANGSMITH_API_KEY")
    if not key:
        return False
    os.environ["LANGSMITH_API_KEY"] = key
    os.environ["LANGSMITH_ENDPOINT"] = _env("LANGSMITH_ENDPOINT") or "https://eu.api.smith.langchain.com"
    os.environ["LANGSMITH_PROJECT"] = project
    os.environ["LANGSMITH_TRACING"] = "true"
    return True


PSEUDONYM_PREFIX = "cx_"


def pseudonymise(complaint_id) -> str:
    """Salted alias for a complaint/customer identifier. IDEMPOTENT ON PURPOSE.

    Pseudonymisation happens once, at the boundary. Hashing an already-hashed reference
    produces a second, different alias that still looks perfectly valid — non-empty,
    right prefix, right length — while silently failing to join to the first. That is
    exactly what happened here: the evaluation harness passed an already-pseudonymised ref
    back in as the id, and the trace recorded input cx_9fecc0a5a610bad6 against output
    cx_7748cc2ad163b705 for the same complaint. Every presence check passed; the key was
    useless. Re-aliasing is now a no-op.
    """
    s = str(complaint_id)
    if s.startswith(PSEUDONYM_PREFIX):
        return s
    return PSEUDONYM_PREFIX + hashlib.sha256(f"{_SALT}:{s}".encode()).hexdigest()[:16]


def _openai() -> OpenAI:
    return OpenAI(api_key=_env("OPENAI_API_KEY"))


def _call_model(client: OpenAI, product: str, narrative: str, model: str) -> tuple[dict, bool, bool]:
    """Returns (parsed, malformed, call_failed). Never raises."""
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": P.SYSTEM_PROMPT},
                      {"role": "user", "content": P.build_user_message(product, narrative)}],
            response_format={"type": "json_object"}, temperature=0)
        raw = r.choices[0].message.content
    except Exception:                                        # noqa: BLE001
        return {}, False, True
    try:
        return json.loads(raw), False, False
    except json.JSONDecodeError:
        return {}, True, False


def classify(complaint_id, product: str, narrative: str, *,
             environment: str = "eval", model: str | None = None, client: OpenAI | None = None) -> dict:
    """Classify one complaint and return the full decision record.

    The record is the trace payload: everything a reviewer needs to answer "why this
    outcome" without reading code.
    """
    model = model or P.MODEL
    client = client or _openai()
    parsed, malformed, call_failed = _call_model(client, product, narrative, model)

    d = D.decide(
        narrative=narrative, product=product,
        queue=str(parsed.get("queue", "")),
        confidence=float(parsed.get("confidence", 0.0) or 0.0),
        evidence=str(parsed.get("evidence", "")),
        valid_queues=P.PRODUCT_QUEUES.get(product, ["OTHER"]),
        queue_to_team=T.QUEUE_TO_TEAM, threshold=P.CONFIDENCE_THRESHOLD,
        malformed=malformed, call_failed=call_failed)

    return {**d.as_dict(),
            "customer_ref": pseudonymise(complaint_id),
            "environment": environment,
            "product": product,
            "model": model,
            "prompt_version": PROMPT_VERSION,
            "narrative_chars": len(narrative)}


def traced_classify(complaint_id, product: str, narrative: str, *,
                    environment: str = "eval", model: str | None = None,
                    client: OpenAI | None = None) -> dict:
    """classify(), wrapped in a LangSmith run. Tracing failure never breaks the decision."""
    try:
        from langsmith import traceable
    except Exception:                                        # noqa: BLE001
        return classify(complaint_id, product, narrative,
                        environment=environment, model=model, client=client)

    @traceable(run_type="chain", name="complaint_triage",
               metadata={"environment": environment, "prompt_version": PROMPT_VERSION,
                         "model": model or P.MODEL})
    def _run(customer_ref: str, product: str, narrative_chars: int, narrative: str) -> dict:
        return classify(complaint_id, product, narrative,
                        environment=environment, model=model, client=client)

    try:
        return _run(pseudonymise(complaint_id), product, len(narrative), narrative)
    except Exception:                                        # noqa: BLE001
        # Telemetry is fire-and-forget. The observed system does not depend on it.
        return classify(complaint_id, product, narrative,
                        environment=environment, model=model, client=client)


if __name__ == "__main__":
    print("prompt_version:", PROMPT_VERSION)
    print("langsmith configured:", configure_langsmith())
    print("pseudonym example:", pseudonymise(1234567))
