"""Cost, saving and timeline model for the complaint triage engagement.

Every figure in cost_analysis.md is computed here. Nothing is typed into the document by
hand, so the numbers in the pitch and the numbers in the model cannot diverge.

Assumptions are declared in ASSUMPTIONS with a source for each. Anything without a source
is a judgement, and is labelled as one.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GBP_EUR = 1.17          # judgement: rounded mid-market rate, stated rather than hidden

ASSUMPTIONS = {
    # --- client shape (judgement, stated in research/sector_research.md) ---
    "current_accounts":        (250_000, "assumption: mid-size firm, ~250k retail customers"),
    "credit_cards":            (80_000,  "assumption: ~32% card cross-hold"),

    # --- external benchmarks (sourced) ---
    "ca_complaints_per_1000_half":  (3.7,   "FCA aggregate complaints data 2025 H2, current accounts"),
    "cc_complaints_per_1000_half":  (3.6,   "FCA aggregate complaints data 2025 H2, credit cards"),
    "uphold_rate_pct":              (55.54, "FCA aggregate complaints data 2025 H2"),
    "avg_redress_gbp":              (215,   "FCA aggregate complaints data 2025 H2"),
    "ombudsman_case_fee_gbp":       (650,   "Financial Ombudsman Service case fee, frozen for 2025/26"),
    "ombudsman_free_cases":         (3,     "FOS: most businesses receive 3 free cases a year"),
    "handler_salary_eur":           (45_000, "midpoint of NL banking CS ~EUR39.5k and IE complaints investigator ~EUR52k"),

    # --- measured on this project ---
    "input_tokens":            (684, "measured, n=12, classifier/prompt.py"),
    "output_tokens":           (49,  "measured, n=12"),
    "price_in_per_1m_usd":     (0.15, "OpenAI list price, gpt-4o-mini input: https://developers.openai.com/api/docs/models/gpt-4o-mini"),
    "price_out_per_1m_usd":    (0.60, "OpenAI list price, gpt-4o-mini output: https://developers.openai.com/api/docs/models/gpt-4o-mini"),
    "gpt4o_price_in_per_1m_usd":  (2.50, "OpenAI list price, gpt-4o input: https://developers.openai.com/api/docs/models/gpt-4o"),
    "gpt4o_price_out_per_1m_usd": (10.00, "OpenAI list price, gpt-4o output: https://developers.openai.com/api/docs/models/gpt-4o"),

    # --- operating judgements (no source; these are the soft numbers) ---
    "triage_minutes_now":      (6,    "judgement: read, categorise and route one complaint"),
    "triage_minutes_assisted": (3,    "judgement: confirm or override a proposal, still reading it"),
    "employer_oncost_pct":     (30,   "judgement: employer social costs on gross salary"),
    "productive_hours_year":   (1_550, "judgement: FTE hours net of leave, training, admin"),
    "platform_eur_month":      (150,  "judgement: n8n hosting + LangSmith + logging"),
    "review_days_per_quarter": (2,    "judgement: quarterly accuracy review and prompt maintenance"),
    "day_rate_eur":            (700,  "set by the consultant"),
}
A = {k: v[0] for k, v in ASSUMPTIONS.items()}

# --- volume ---------------------------------------------------------------------
ca = A["current_accounts"] / 1000 * A["ca_complaints_per_1000_half"] * 2
cc = A["credit_cards"] / 1000 * A["cc_complaints_per_1000_half"] * 2
complaints_year = round(ca + cc)

# --- labour ---------------------------------------------------------------------
loaded_salary = A["handler_salary_eur"] * (1 + A["employer_oncost_pct"] / 100)
hourly = loaded_salary / A["productive_hours_year"]
hours_now = complaints_year * A["triage_minutes_now"] / 60
hours_assisted = complaints_year * A["triage_minutes_assisted"] / 60
labour_now = hours_now * hourly
labour_saving = (hours_now - hours_assisted) * hourly

# --- running cost ---------------------------------------------------------------
per_complaint_usd = (A["input_tokens"] / 1e6 * A["price_in_per_1m_usd"]
                     + A["output_tokens"] / 1e6 * A["price_out_per_1m_usd"])
per_complaint_gpt4o_usd = (
    A["input_tokens"] / 1e6 * A["gpt4o_price_in_per_1m_usd"]
    + A["output_tokens"] / 1e6 * A["gpt4o_price_out_per_1m_usd"]
)
api_year_eur = per_complaint_usd * complaints_year * 0.92        # USD->EUR, judgement
gpt4o_api_year_eur = per_complaint_gpt4o_usd * complaints_year * 0.92
gpt4o_to_mini_cost_ratio = per_complaint_gpt4o_usd / per_complaint_usd
platform_year = A["platform_eur_month"] * 12
review_year = A["review_days_per_quarter"] * 4 * A["day_rate_eur"]
ongoing_year = api_year_eur + platform_year + review_year
net_year = ongoing_year - labour_saving

# --- upfront, fixed fee per phase -----------------------------------------------
PHASES = [
    ("Phase 0 — Discovery and expert labelling", 8,
     "Scope, data access, and 300 complaints labelled by two of the firm's own handlers. "
     "Produces the ground truth that does not currently exist."),
    ("Phase 1 — Pilot build and 60-day shadow run", 12,
     "Shadow triage running alongside the existing process; handlers do not act on suggestions. "
     "Measures accuracy against "
     "the firm's labels, not the public proxy."),
    ("Phase 2 — Deployment, if the pilot passes", 15,
     "Integration with the case system, handler training, monitoring and handover."),
]
phase_costs = [(n, d, d * A["day_rate_eur"], why) for n, d, why in PHASES]
to_pilot = sum(c for _, _, c, _ in phase_costs[:2])
full = sum(c for _, _, c, _ in phase_costs)

# --- break-even -----------------------------------------------------------------
fos_fee_eur = A["ombudsman_case_fee_gbp"] * GBP_EUR
redress_eur = A["avg_redress_gbp"] * GBP_EUR
cases_to_break_even = net_year / fos_fee_eur if net_year > 0 else 0
payback_full_years = full / (fos_fee_eur * max(cases_to_break_even, 1e-9)) if net_year > 0 else None

# volume at which labour saving alone covers the running cost
saving_per_complaint = (A["triage_minutes_now"] - A["triage_minutes_assisted"]) / 60 * hourly
complaints_break_even = (platform_year + review_year) / saving_per_complaint
accounts_break_even = complaints_break_even / (A["ca_complaints_per_1000_half"] * 2 / 1000)

out = {
    "volume": {"complaints_per_year": complaints_year,
               "current_account_complaints": round(ca), "credit_card_complaints": round(cc)},
    "labour": {"loaded_hourly_eur": round(hourly, 2),
               "hours_now": round(hours_now), "hours_assisted": round(hours_assisted),
               "current_triage_cost_eur": round(labour_now),
               "annual_labour_saving_eur": round(labour_saving)},
    "running_cost": {"api_per_complaint_eur": round(per_complaint_usd * 0.92, 6),
                     "api_per_year_eur": round(api_year_eur, 2),
                     "gpt4o_api_per_year_eur": round(gpt4o_api_year_eur, 2),
                     "gpt4o_to_mini_cost_ratio": round(gpt4o_to_mini_cost_ratio, 1),
                     "platform_per_year_eur": platform_year,
                     "model_review_per_year_eur": review_year,
                     "total_per_year_eur": round(ongoing_year),
                     "net_per_year_eur": round(net_year)},
    "upfront_fixed_fee": {n: {"days": d, "fee_eur": c} for n, d, c, _ in phase_costs},
    "upfront_to_end_of_pilot_eur": to_pilot, "upfront_full_eur": full,
    "break_even": {
        "net_annual_cost_eur": round(net_year),
        "ombudsman_case_fee_eur": round(fos_fee_eur),
        "avoided_ombudsman_cases_to_cover_running_cost": round(cases_to_break_even, 1),
        "complaints_per_year_for_labour_alone_to_cover": round(complaints_break_even),
        "current_accounts_needed_for_labour_alone_to_cover": round(accounts_break_even),
    },
    "assumption_sources": {k: v[1] for k, v in ASSUMPTIONS.items()},
    "gbp_eur": GBP_EUR,
}
(HERE / "cost_model.json").write_text(json.dumps(out, indent=2))

# The deliverables page asks for an "explicit assumptions table" by name, so it is emitted
# as its own artifact rather than left scattered through the analysis. Generated, so it
# cannot drift from the model that uses these values.
SOURCED = ("FCA", "Financial Ombudsman", "OpenAI", "measured", "midpoint")
rows = []
for k, (v, why) in ASSUMPTIONS.items():
    kind = "sourced" if any(s in why for s in SOURCED) else (
        "set by consultant" if "consultant" in why else
        "assumption" if why.startswith("assumption") else "judgement")
    val = f"{v:,}" if isinstance(v, (int, float)) and v >= 1000 else str(v)
    rows.append(f"| `{k}` | {val} | {kind} | {why} |")
(HERE / "assumptions.md").write_text(
    "# Assumptions Table — Complaint Triage Cost Model\n\n"
    "Author: Ugo Ahukannah\nCapstone Round 1 · Companion to `cost_analysis.md`\n\n"
    "**Generated by `cost_model.py`. Do not hand-edit.** Every figure in the cost analysis\n"
    "derives from a row below, so an assumption cannot say one thing here and another there.\n\n"
    "Each row is classified. **sourced** means a published external figure. **measured**\n"
    "means measured on this project. **assumption** means a stated property of the client\n"
    "scenario. **judgement** means my estimate with no citation — these are the soft numbers\n"
    "and the ones to challenge first.\n\n"
    "| Input | Value | Kind | Basis |\n|---|---:|---|---|\n" + "\n".join(rows) +
    f"\n\nGBP converted to EUR at {GBP_EUR}, a judgement, stated rather than hidden.\n\n"
    "## The four that move the answer most\n\n"
    "| Input | Why it dominates |\n|---|---|\n"
    "| `ca_complaints_per_1000_half` | Drives total volume, and every euro figure scales off it |\n"
    "| `triage_minutes_assisted` | The softest number here. At 1 minute saved rather than 3, the labour saving falls to about a third |\n"
    "| `review_days_per_quarter` | 76% of the running cost. Cutting oversight is the only way to make this cheap, and it is the wrong saving |\n"
    "| `ombudsman_case_fee_gbp` | The entire ROI case rests on avoided escalations, priced at this figure |\n")
print("wrote cost_estimation/assumptions.md")

print(f"complaints/year            {complaints_year:>10,}")
print(f"loaded hourly cost         EUR {hourly:>8.2f}")
print(f"current triage labour      EUR {labour_now:>8,.0f}/yr  ({hours_now:.0f} hours)")
print(f"labour saving (assist)     EUR {labour_saving:>8,.0f}/yr")
print()
print(f"API cost per complaint     EUR {per_complaint_usd*0.92:>8.6f}")
print(f"API cost per year          EUR {api_year_eur:>8.2f}")
print(f"gpt-4o API cost per year   EUR {gpt4o_api_year_eur:>8.2f}  ({gpt4o_to_mini_cost_ratio:.1f}x mini)")
print(f"platform per year          EUR {platform_year:>8,.0f}")
print(f"model review per year      EUR {review_year:>8,.0f}")
print(f"TOTAL running              EUR {ongoing_year:>8,.0f}/yr")
print(f"NET of labour saving       EUR {net_year:>8,.0f}/yr  <-- {'COST' if net_year>0 else 'SAVING'}")
print()
for n, d, c, _ in phase_costs:
    print(f"  {n:<48} {d:>3}d  EUR {c:>7,.0f}")
print(f"  {'to end of pilot':<48}       EUR {to_pilot:>7,.0f}")
print(f"  {'full programme':<48}       EUR {full:>7,.0f}")
print()
print(f"avoided ombudsman cases to cover running cost: {cases_to_break_even:.1f}/yr "
      f"(fee EUR {fos_fee_eur:.0f})")
print(f"labour saving alone covers running cost at {complaints_break_even:,.0f} complaints/yr "
      f"= ~{accounts_break_even:,.0f} current accounts")
