"""UC-1 — Complaint triage. Proposes a routing queue, grounded in a verbatim quote.

This is the capability Round 1 built and the one that must run. It reads its prompt and
its taxonomy from `classifier/prompt.py`, unchanged, so the MVP and the n8n POC classify
identically — a difference between them would make the demo evidence for nothing.
"""
from __future__ import annotations

from . import _shared  # noqa: F401  (path setup)

import prompt as P
import teams as T

from ..runtime import pseudonymise
from ..spine import parse_json_object

MIN_NARRATIVE_CHARS = 20
MAX_NARRATIVE_CHARS = 6000


class Triage:
    name = "triage"
    title = "Complaint triage"
    threshold = P.CONFIDENCE_THRESHOLD          # 0.70
    model = P.MODEL                             # gpt-4o-mini

    def ref(self, request: dict) -> str:
        return pseudonymise(request.get("complaint_id", "unknown"))

    def validate(self, request: dict) -> str | None:
        product = (request.get("product") or "").strip()
        narrative = (request.get("narrative") or "").strip()
        if product not in P.PRODUCT_QUEUES:
            return f"'{product}' is not a product this system handles"
        if len(narrative) < MIN_NARRATIVE_CHARS:
            return f"complaint text is too short to triage ({len(narrative)} chars, need {MIN_NARRATIVE_CHARS})"
        return None

    def messages(self, request: dict) -> list[dict]:
        return [
            {"role": "system", "content": P.SYSTEM_PROMPT},
            {"role": "user", "content": P.build_user_message(
                request["product"], request["narrative"].strip()[:MAX_NARRATIVE_CHARS])},
        ]

    def parse(self, text: str) -> dict:
        o = parse_json_object(text)
        return {"queue": str(o.get("queue", "")).strip(),
                "confidence": o.get("confidence"),
                "evidence": str(o.get("evidence", "")).strip()}

    def scope_check(self, parsed: dict, request: dict) -> str | None:
        valid = P.PRODUCT_QUEUES.get(request["product"], [])
        if parsed["queue"] not in valid:
            return "REJECT_QUEUE_NOT_IN_PRODUCT"
        if parsed["queue"] == "OTHER":
            return "REJECT_OUT_OF_TAXONOMY"
        return None

    def grounding_check(self, parsed: dict, request: dict) -> tuple[str | None, str]:
        """The quote must actually be in the complaint.

        Matched on the first 60 characters, case-insensitively — identical to the Round 1
        check, so reason-code rates are comparable between the POC and the MVP. It caught
        four fabricated quotations in the Round 1 sample of sixty.
        """
        ev = parsed.get("evidence") or ""
        if ev and ev[:60].lower() in request["narrative"].lower():
            return None, "quote found verbatim in the complaint"
        return "REJECT_EVIDENCE_NOT_VERBATIM", f"quote not found in the complaint: {ev[:80]!r}"

    def summarise(self, parsed: dict, request: dict) -> str:
        team = T.team_for(parsed["queue"]) if parsed["queue"] else "—"
        return f"Route to {team} — {parsed['queue'] or 'no queue proposed'}"

    def citations(self, parsed: dict) -> list[str]:
        ev = parsed.get("evidence")
        return [ev] if ev else []

    def team(self, parsed: dict) -> str:
        return T.team_for(parsed.get("queue", ""))
