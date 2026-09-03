"""Round 2 ROI model — three capabilities, 12 and 36 months. Generated, never hand-edited.

Extends the Round 1 model rather than replacing it: the Round 1 figures are read from
`cost_model.json`, so a number cannot say one thing in the Round 1 cost analysis and
another in the Round 2 ROI. Run `python cost_estimation/cost_model.py` first if that file
is missing.

Two scenarios are reported, deliberately:

  CONSERVATIVE  counts only labour that is measurably displaced — hours a person no longer
                spends. Nothing avoided, nothing prevented.
  CENTRAL       adds losses avoided by catching unauthorised transactions earlier, and
                ombudsman escalations avoided by routing correctly first time.

The conservative case is the one to look at first, because it contains no claim that the
pilot has not yet tested. That it comes out NEGATIVE is the finding, not an embarrassment:
this system does not pay for itself on saved minutes, and any model that says otherwise is
hiding its oversight cost. The case rests on avoided losses — which is precisely what the
60-day pilot is designed to measure.

ROI = (Net Benefit / Total Cost) x 100, as specified in the deliverables brief.

Run:  python cost_estimation/roi_model.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
R1 = json.loads((HERE / "cost_model.json").read_text())

GBP_EUR = R1["gbp_eur"]
HOURLY = R1["labour"]["loaded_hourly_eur"]
DAY_HOURS = 7.5
COMPLAINTS_YEAR = R1["volume"]["complaints_per_year"]
DAY_RATE = 700

# --------------------------------------------------------------- Round 2 assumptions
# Same discipline as Round 1: every row carries its kind. "judgement" means my estimate
# with no citation. Those are the rows to challenge first, and they are named as such in
# roi_risk_assessment.md rather than buried.
A2 = {
    # -- UC-3 reporting assistance
    "report_days_per_quarter_now": (5, "judgement",
        "person-days assembling the quarterly complaints report by hand"),
    "report_time_reduction_pct": (50, "judgement",
        "share of drafting time displaced; the review still happens in full"),
    # -- UC-2 anomaly flagging
    "fraud_unauth_share_pct": (7.4, "measured",
        "share of the reference corpus that is fraud or unauthorised transactions "
        "(810 + 437 of 16,839)"),
    "earlier_detection_rate_pct": (15, "judgement",
        "share of those cases caught by monitoring before the customer complains. "
        "THE SOFTEST NUMBER IN THIS MODEL"),
    "avg_redress_gbp": (215, "sourced", "FCA aggregate complaints data 2025 H2"),
    # -- UC-1 escalation avoidance
    "avoided_ombudsman_cases": (4, "judgement",
        "escalations avoided per year by routing correctly first time. Explicitly NOT "
        "claimed as a benefit today; the pilot exists to test it"),
    "ombudsman_case_fee_gbp": (650, "sourced",
        "Financial Ombudsman Service case fee, frozen for 2025/26"),
    # -- running cost of three capabilities rather than one
    "platform_eur_month": (150, "judgement", "n8n hosting + LangSmith + logging, unchanged"),
    "review_days_per_quarter": (3, "judgement",
        "quarterly review of three capabilities rather than one. Round 1 assumed 2 for a "
        "single capability; this is the cost of the widened scope"),
    "reports_per_year": (4, "assumption", "one complaints report per quarter, 4 sections each"),
    "anomaly_batches_per_year": (12, "assumption", "monthly batch review"),
    "anomaly_candidates_per_batch": (56, "assumption",
        "candidates in ONE capped monthly review batch. The 56 was raised by the detector on "
        "the 40-account, 90-day synthetic fixture, so it sizes a bounded analyst queue rather "
        "than the client's transaction book. detect() applies no cap, so at the same 2.71% "
        "flag rate the full book would raise ~154,000 a month. UC-2 is costed as a reviewed "
        "batch on purpose; the unbounded version is R9, and it is arithmetic, not a worry"),
    # -- token costs for the two new capabilities
    "report_tokens_in": (900, "estimate",
        "sized from the prompt in mvp/capabilities/reporting.py, not counted from an API "
        "response. Measured across all four sections 2026-09-03: 408 in / 144 out mean. The "
        "costed figure is deliberately left at the higher estimate"),
    "report_tokens_out": (180, "estimate", "as above; measured mean 144"),
    "anomaly_tokens_in": (420, "estimate",
        "sized from the prompt in mvp/capabilities/anomaly.py, not counted from an API "
        "response. Measured over six candidates 2026-09-03: 314 in / 94 out mean. The costed "
        "figure is deliberately left at the higher estimate"),
    "anomaly_tokens_out": (120, "estimate", "as above; measured mean 94"),
    "price_in_per_1m_usd": (0.15, "sourced", "OpenAI list price, gpt-4o-mini input"),
    "price_out_per_1m_usd": (0.60, "sourced", "OpenAI list price, gpt-4o-mini output"),
    "usd_eur": (0.92, "judgement", "rounded mid-market rate, stated rather than hidden"),
    # -- delivery
    "value_starts_month": (7, "judgement",
        "Phase 0 + 1 + 2 run about six months end to end, so benefits accrue from month 7. "
        "This is why the 12-month ROI is negative and the 36-month is not"),
}
V = {k: v[0] for k, v in A2.items()}

# ------------------------------------------------------------------------ annual value
triage_labour = R1["labour"]["annual_labour_saving_eur"]

report_days_saved = (V["report_days_per_quarter_now"] * 4
                     * V["report_time_reduction_pct"] / 100)
report_labour = report_days_saved * DAY_HOURS * HOURLY

unauth_cases = COMPLAINTS_YEAR * V["fraud_unauth_share_pct"] / 100
caught_early = unauth_cases * V["earlier_detection_rate_pct"] / 100
redress_eur = V["avg_redress_gbp"] * GBP_EUR
handling_eur = 6 / 60 * HOURLY                      # the complaint never has to be handled
anomaly_value = caught_early * (redress_eur + handling_eur)

fos_fee_eur = V["ombudsman_case_fee_gbp"] * GBP_EUR
ombudsman_value = V["avoided_ombudsman_cases"] * fos_fee_eur

VALUE = {
    "UC-1 triage — handler time displaced": (triage_labour, "conservative"),
    "UC-3 reporting — drafting time displaced": (report_labour, "conservative"),
    "UC-2 anomaly — losses avoided by earlier detection": (anomaly_value, "central"),
    "UC-1 triage — ombudsman escalations avoided": (ombudsman_value, "central"),
}
value_conservative = sum(v for v, s in VALUE.values() if s == "conservative")
value_central = sum(v for v, _ in VALUE.values())

# ------------------------------------------------------------------------ annual cost
def _api(n_calls, tin, tout):
    usd = n_calls * (tin / 1e6 * V["price_in_per_1m_usd"] + tout / 1e6 * V["price_out_per_1m_usd"])
    return usd * V["usd_eur"]

api_triage = R1["running_cost"]["api_per_year_eur"]
api_report = _api(V["reports_per_year"] * 4, V["report_tokens_in"], V["report_tokens_out"])
api_anomaly = _api(V["anomaly_batches_per_year"] * V["anomaly_candidates_per_batch"],
                   V["anomaly_tokens_in"], V["anomaly_tokens_out"])
platform = V["platform_eur_month"] * 12
oversight = V["review_days_per_quarter"] * 4 * DAY_RATE

COST_RUN = {
    "Model calls — triage": api_triage,
    "Model calls — reporting": api_report,
    "Model calls — anomaly": api_anomaly,
    "Platform (hosting, monitoring, logging)": platform,
    "Human oversight (quarterly review of three capabilities)": oversight,
}
cost_run_year = sum(COST_RUN.values())
ai_share_pct = 100 * (api_triage + api_report + api_anomaly) / cost_run_year

# --------------------------------------------------------------------------- upfront
# Three capabilities cost far less than three builds, because the decision spine, the
# guards, the reason codes, the error handling and the trace record are built once. That
# ratio is the commercial argument for the architecture, so it is computed, not asserted.
PHASES = [
    ("Phase 0 — Discovery and expert labelling", 8,
     "Scope, data access, and 300 complaints labelled by two of the firm's own handlers. "
     "Unchanged from Round 1: labelling is triage-specific, discovery covers all three."),
    ("Phase 1 — Pilot build and 60-day shadow run", 18,
     "All three capabilities on the shared spine, running alongside the existing process. "
     "Round 1 costed 12 days for triage alone."),
    ("Phase 2 — Deployment, if the pilot passes", 20,
     "Case-system integration, handler and analyst training, monitoring handover. "
     "Round 1 costed 15 days for one capability."),
]
phase_costs = [(n, d, d * DAY_RATE, why) for n, d, why in PHASES]
upfront_full = sum(c for _, _, c, _ in phase_costs)
upfront_to_pilot = sum(c for _, _, c, _ in phase_costs[:2])
r1_full = R1["upfront_full_eur"]
scope_multiple = upfront_full / r1_full

# ------------------------------------------------------------------------------- ROI
def roi(months: int, annual_value: float) -> dict:
    """ROI = (Net Benefit / Total Cost) x 100, with benefits ramped from month 7."""
    earning = max(0, months - (V["value_starts_month"] - 1))
    benefit = annual_value * earning / 12
    cost = upfront_full + cost_run_year * months / 12
    net = benefit - cost
    return {"months": months, "earning_months": earning,
            "total_benefit_eur": round(benefit), "total_cost_eur": round(cost),
            "net_benefit_eur": round(net), "roi_pct": round(100 * net / cost, 1)}


def break_even_month(annual_value: float) -> int | None:
    for m in range(1, 121):
        earning = max(0, m - (V["value_starts_month"] - 1))
        if annual_value * earning / 12 >= upfront_full + cost_run_year * m / 12:
            return m
    return None


SCENARIOS = {
    "conservative": {"annual_value_eur": round(value_conservative),
                     "roi_12m": roi(12, value_conservative),
                     "roi_36m": roi(36, value_conservative),
                     "break_even_month": break_even_month(value_conservative)},
    "central": {"annual_value_eur": round(value_central),
                "roi_12m": roi(12, value_central),
                "roi_36m": roi(36, value_central),
                "break_even_month": break_even_month(value_central)},
}

# ------------------------------------------------------------------------ sensitivity
# One row per soft assumption, showing what the 36-month central ROI becomes if it is
# wrong in the unfavourable direction. A model that cannot say which input matters is
# not a model, it is a number.
def _with(**over):
    global V, report_labour, anomaly_value, cost_run_year
    saved = dict(V)
    V = {**V, **over}
    rl = (V["report_days_per_quarter_now"] * 4 * V["report_time_reduction_pct"] / 100
          ) * DAY_HOURS * HOURLY
    av = (COMPLAINTS_YEAR * V["fraud_unauth_share_pct"] / 100
          * V["earlier_detection_rate_pct"] / 100) * (redress_eur + handling_eur)
    ov = V["review_days_per_quarter"] * 4 * DAY_RATE
    val = triage_labour + rl + av + ombudsman_value
    run = api_triage + api_report + api_anomaly + platform + ov
    earning = 36 - (V["value_starts_month"] - 1)
    benefit, cost = val * earning / 12, upfront_full + run * 3
    V = saved
    return round(100 * (benefit - cost) / cost, 1)

base36 = SCENARIOS["central"]["roi_36m"]["roi_pct"]
SENSITIVITY = {
    "earlier_detection_rate_pct 15 -> 5": _with(earlier_detection_rate_pct=5),
    "report_time_reduction_pct 50 -> 20": _with(report_time_reduction_pct=20),
    "review_days_per_quarter 3 -> 6": _with(review_days_per_quarter=6),
    "value_starts_month 7 -> 10": _with(value_starts_month=10),
}

# ------------------------------------------------- what would have to be true instead
# A negative ROI is only useful if it says what would change it. Two things do: the firm
# being bigger, or the build not being paid for once by one firm. Both are computed rather
# than asserted, and both feed the go-to-market section of strategic_plan.md.

def _value_at_volume(complaints: int) -> float:
    """Annual central value scales with complaint volume; oversight and platform do not."""
    scale = complaints / COMPLAINTS_YEAR
    return (triage_labour + anomaly_value + ombudsman_value) * scale + report_labour


def break_even_volume(months: int = 36) -> int | None:
    """Complaint volume at which the central case clears its costs within `months`."""
    earning = months - (V["value_starts_month"] - 1)
    cost = upfront_full + cost_run_year * months / 12
    for n in range(500, 200_001, 100):
        if _value_at_volume(n) * earning / 12 >= cost:
            return n
    return None


be_vol = break_even_volume(36)
be_customers = round(be_vol / (A2["report_days_per_quarter_now"][0] * 0 + 1)
                     ) if be_vol else None
# customers implied, using the same complaint rate per 1,000 accounts as Round 1
complaints_per_account = COMPLAINTS_YEAR / 250_000
be_accounts = round(be_vol / complaints_per_account) if be_vol else None

# Productised: the build is paid for once and sold many times. This is the consultant's
# commercialisation model, and it is the only route on these numbers by which a firm of
# Chleo's size ever sees a positive return.
CLIENTS = 5
per_client_build = upfront_full / CLIENTS
prod_cost_36 = per_client_build + cost_run_year * 3
prod_benefit_36 = value_central * (36 - (V["value_starts_month"] - 1)) / 12
productised = {
    "clients_sharing_the_build": CLIENTS,
    "per_client_build_eur": round(per_client_build),
    "total_cost_36m_eur": round(prod_cost_36),
    "total_benefit_36m_eur": round(prod_benefit_36),
    "net_benefit_36m_eur": round(prod_benefit_36 - prod_cost_36),
    "roi_36m_pct": round(100 * (prod_benefit_36 - prod_cost_36) / prod_cost_36, 1),
    "note": ("The build is bespoke today. Amortising it across five mid-size firms is what "
             "turns the same capability from a loss into a return for a client this size. "
             "It is a commercial decision, not a technical one."),
}

# The three levers, priced. Each is a decision someone can actually take.
inhouse_day = DAY_HOURS * HOURLY                      # the firm's own loaded day cost
oversight_inhouse = V["review_days_per_quarter"] * 4 * inhouse_day


def _roi36(cost_upfront: float, cost_run: float) -> float:
    benefit = value_central * (36 - (V["value_starts_month"] - 1)) / 12
    cost = cost_upfront + cost_run * 3
    return round(100 * (benefit - cost) / cost, 1)


LEVERS = {
    "as proposed — bespoke build, consultant-run oversight":
        _roi36(upfront_full, cost_run_year),
    "oversight moved in-house after handover":
        _roi36(upfront_full, cost_run_year - oversight + oversight_inhouse),
    "build amortised across 5 clients":
        _roi36(per_client_build, cost_run_year),
    "both — productised build AND in-house oversight":
        _roi36(per_client_build, cost_run_year - oversight + oversight_inhouse),
}

out = {
    "annual_value_eur": {k: round(v) for k, (v, _) in VALUE.items()},
    "value_scenario": {k: s for k, (_, s) in VALUE.items()},
    "annual_running_cost_eur": {k: round(v, 2) for k, v in COST_RUN.items()},
    "annual_running_cost_total_eur": round(cost_run_year),
    "ai_share_of_running_cost_pct": round(ai_share_pct, 2),
    "upfront_fixed_fee": {n: {"days": d, "fee_eur": c, "why": w} for n, d, c, w in phase_costs},
    "upfront_to_end_of_pilot_eur": upfront_to_pilot,
    "upfront_full_eur": upfront_full,
    "round1_upfront_full_eur": r1_full,
    "scope_multiple_for_3x_capabilities": round(scope_multiple, 2),
    "scenarios": SCENARIOS,
    "sensitivity_36m_central_roi_pct": {"base": base36, **SENSITIVITY},
    "break_even_volume": {
        "complaints_per_year_for_36m_payback": be_vol,
        "retail_accounts_implied": be_accounts,
        "this_client_complaints_per_year": COMPLAINTS_YEAR,
        "note": ("At this client's volume the bespoke build does not pay back inside 36 "
                 "months. This is the volume at which it would."),
    },
    "productised": productised,
    "oversight_inhouse_day_eur": round(inhouse_day, 2),
    "levers_36m_central_roi_pct": LEVERS,
    "assumptions": {k: {"value": v[0], "kind": v[1], "basis": v[2]} for k, v in A2.items()},
}
(HERE / "roi_model.json").write_text(json.dumps(out, indent=2))

if __name__ == "__main__":
    print(json.dumps(out, indent=2))
