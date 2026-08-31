"""Exercise every guard in the ladder, for every capability, with no network and no keys.

Each case asserts the reason code AND the stage it failed at. A test that only checked
"went to human review" would pass for the wrong reason — and the whole claim of this
system is that a rejection says *why*.

Run:  python -m mvp.test_spine
"""
from __future__ import annotations

import json
import sys

from .spine import run, GUARD_ORDER, REASONS, PROPOSE, HUMAN

NARRATIVE = ("I was charged twice for the same purchase on my credit card statement and "
             "the bank has not refunded the duplicate charge after three phone calls.")
PRODUCT = "Credit card"

CASES: list[tuple] = []
FAILURES: list[str] = []


def stub(reply):
    """A model that always returns `reply` — or raises it, if it is an exception."""
    def _call(messages, model):
        if isinstance(reply, Exception):
            raise reply
        return reply if isinstance(reply, str) else json.dumps(reply)
    return _call


def check(label, cap, request, reply, expect_code, expect_stage):
    d = run(cap, request, call=stub(reply))
    ok = d.reason_code == expect_code and d.failed_stage == expect_stage
    exp_dec = PROPOSE if expect_code == "OK_PROPOSED" else HUMAN
    ok = ok and d.decision == exp_dec
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<46} -> {d.reason_code} @ {d.failed_stage}")
    if not ok:
        FAILURES.append(f"{label}: got {d.reason_code}@{d.failed_stage}/{d.decision}, "
                        f"expected {expect_code}@{expect_stage}/{exp_dec}")
    return d


def test_triage():
    from .capabilities.triage import Triage
    cap = Triage()
    good = {"complaint_id": "1234", "product": PRODUCT, "narrative": NARRATIVE}
    q = "Problem with a purchase shown on your statement"
    print("\ntriage")
    check("input: unknown product", cap, {**good, "product": "Spaceship loan"},
          {}, "REJECT_INVALID_INPUT", "input")
    check("input: narrative too short", cap, {**good, "narrative": "bad"},
          {}, "REJECT_INVALID_INPUT", "input")
    check("call: model raises", cap, good, RuntimeError("connection reset"),
          "ERROR_MODEL_CALL", "call")
    check("parse: not JSON", cap, good, "I think it's a card dispute.",
          "REJECT_MALFORMED_OUTPUT", "parse")
    check("scope: invented queue", cap, good,
          {"queue": "Complaints about the weather", "confidence": 0.9, "evidence": "charged twice"},
          "REJECT_QUEUE_NOT_IN_PRODUCT", "scope")
    check("scope: abstained (OTHER)", cap, good,
          {"queue": "OTHER", "confidence": 0.9, "evidence": "charged twice"},
          "REJECT_OUT_OF_TAXONOMY", "scope")
    check("confidence: below threshold", cap, good,
          {"queue": q, "confidence": 0.4, "evidence": "charged twice"},
          "REJECT_LOW_CONFIDENCE", "confidence")
    check("confidence: not a number", cap, good,
          {"queue": q, "confidence": "high", "evidence": "charged twice"},
          "REJECT_MALFORMED_OUTPUT", "parse")
    check("grounding: fabricated quote", cap, good,
          {"queue": q, "confidence": 0.9, "evidence": "the ATM ate my card"},
          "REJECT_EVIDENCE_NOT_VERBATIM", "grounding")
    d = check("clean proposal", cap, good,
              {"queue": q, "confidence": 0.91, "evidence": "charged twice for the same purchase"},
              "OK_PROPOSED", None)
    assert d.ref.startswith("cx_"), "subject reference must be pseudonymous"
    assert "1234" not in json.dumps(d.as_dict()), "raw identifier leaked into the record"


def main() -> int:
    print("Guard ladder, declared order:")
    for c in GUARD_ORDER:
        print(f"  {c:<32} {REASONS[c]}")
    test_triage()
    try:
        from .capabilities.reporting import Reporting  # noqa: F401
        test_reporting()
    except ImportError:
        print("\nreporting: not built yet")
    try:
        from .capabilities.anomaly import Anomaly  # noqa: F401
        test_anomaly()
    except ImportError:
        print("\nanomaly: not built yet")

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED:")
        for f in FAILURES:
            print("  " + f)
        return 1
    print("all guard cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
