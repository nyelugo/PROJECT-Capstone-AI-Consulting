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



def _no_new_failures(n0: int) -> None:
    """Assert nothing was recorded since n0.

    Without this each test function recorded its failures into FAILURES and returned None,
    so pytest saw a passing test while `python -m mvp.test_spine` exited 1 on the same run —
    a green that measured nothing.
    """
    assert len(FAILURES) == n0, "\n".join(FAILURES[n0:])


def test_triage():
    _n0 = len(FAILURES)
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
    _no_new_failures(_n0)


def test_reporting():
    _n0 = len(FAILURES)
    from .capabilities.reporting import Reporting, fact_sheet
    cap = Reporting()
    sheet = fact_sheet()
    good = {"section": "Timeliness", "audience": "the board risk committee"}
    print("\nreporting")
    check("input: unknown section", cap, {**good, "section": "Vibes"},
          {}, "REJECT_INVALID_INPUT", "input")
    check("input: no audience", cap, {**good, "audience": ""},
          {}, "REJECT_INVALID_INPUT", "input")
    check("call: model raises", cap, good, TimeoutError("read timeout"),
          "ERROR_MODEL_CALL", "call")
    check("parse: not JSON", cap, good, "Here is your section.",
          "REJECT_MALFORMED_OUTPUT", "parse")
    check("scope: metric not in this section", cap, good,
          {"narrative": "Nothing to report.", "figures_used": ["monetary_pct"], "confidence": 0.9},
          "REJECT_METRIC_NOT_PUBLISHED", "scope")
    check("confidence: below threshold", cap, good,
          {"narrative": "Nothing to report.", "figures_used": ["complaints"], "confidence": 0.2},
          "REJECT_LOW_CONFIDENCE", "confidence")
    # An invented figure: 88.0% is not the timeliness rate, and no sheet entry is near it.
    check("grounding: invented percentage", cap, good,
          {"narrative": "Firms responded on time in 88.0% of cases this window.",
           "figures_used": ["timely_pct"], "confidence": 0.95},
          "REJECT_FIGURE_NOT_COMPUTED", "grounding")
    # The same sentence with the figure this repo actually computed.
    real = (f"Firms responded on time in {sheet['timely_pct']['v']:.1f}% of cases, with "
            f"{sheet['untimely_n']['v']} complaints missing the deadline.")
    d = check("clean draft, every figure real", cap, good,
              {"narrative": real, "figures_used": ["timely_pct", "untimely_n"], "confidence": 0.9},
              "OK_PROPOSED", None)
    assert "trace to the fact sheet" in d.grounding_detail
    # Rounding must be allowed, or the guard is unusable in practice.
    rounded = f"Firms responded on time in {sheet['timely_pct']['v']:.0f}% of cases."
    check("clean draft, figure rounded to 0dp", cap, good,
          {"narrative": rounded, "figures_used": ["timely_pct"], "confidence": 0.9},
          "OK_PROPOSED", None)
    _no_new_failures(_n0)


def test_anomaly():
    _n0 = len(FAILURES)
    from .capabilities.anomaly import Anomaly, detect
    cap = Anomaly()
    cand = detect()[0]
    good = {"candidate": cand}
    ok = {"explanation": f"Five transactions totalling EUR {cand['amount_eur']} were seen.",
          "next_check": "Call the customer.", "confidence": 0.9}
    print("\nanomaly")
    check("input: no candidate (model may not select)", cap, {},
          {}, "REJECT_INVALID_INPUT", "input")
    check("input: unknown rule", cap, {"candidate": {**cand, "rule": "hunch"}},
          {}, "REJECT_INVALID_INPUT", "input")
    check("call: model raises", cap, good, ConnectionError("dns failure"),
          "ERROR_MODEL_CALL", "call")
    check("parse: not JSON", cap, good, "Looks dodgy to me.",
          "REJECT_MALFORMED_OUTPUT", "parse")
    check("scope: transaction not in the batch", cap,
          {"candidate": {**cand, "txn_ids": ["t999999"]}}, ok,
          "REJECT_ACCOUNT_NOT_IN_LEDGER", "scope")
    check("confidence: below threshold", cap, good, {**ok, "confidence": 0.3},
          "REJECT_LOW_CONFIDENCE", "confidence")
    check("grounding: invented amount", cap, good,
          {**ok, "explanation": "A single payment of EUR 12345.67 was made."},
          "REJECT_VALUE_MISMATCH", "grounding")
    d = check("clean case note", cap, good, ok, "OK_PROPOSED", None)
    assert d.ref.startswith("cx_"), "account reference must be pseudonymous"
    assert cand["account_ref"] not in json.dumps(d.as_dict()), "raw account ref leaked"
    _no_new_failures(_n0)


def test_confidence_rendering():
    _n0 = len(FAILURES)
    """A malformed response has no confidence, and the page must still render.

    This crashed once: the Checks panel formatted confidence with :.2f, so the UI died
    precisely when it had REJECT_MALFORMED_OUTPUT to report. The guard ladder's whole job
    is to turn a bad response into an observable outcome rather than a crash.

    Imported inside the function so the rest of this file stays free of Streamlit.
    """
    from .ui import conf_txt
    print("\nconfidence rendering")
    cases = [(None, "—"), (float("nan"), "—"), ("high", "—"), (0.9, "90%"), (1, "100%")]
    for value, expect in cases:
        got = conf_txt(value)
        ok = got == expect
        print(f"  {'PASS' if ok else 'FAIL'}  conf_txt({value!r:<12}) -> {got!r}")
        if not ok:
            FAILURES.append(f"conf_txt({value!r}) gave {got!r}, expected {expect!r}")
    _no_new_failures(_n0)


def main() -> int:
    print("Guard ladder, declared order:")
    for c in GUARD_ORDER:
        print(f"  {c:<32} {REASONS[c]}")
    test_triage()
    test_confidence_rendering()
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
