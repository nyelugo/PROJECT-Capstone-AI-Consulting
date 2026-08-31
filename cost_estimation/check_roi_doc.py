"""Verify every figure in roi_risk_assessment.md still matches the generated model.

A document and a model that drift apart is the single most likely defect here — it already
happened once in Round 1, where a price ratio said 6x in one file and 17x in another and the
wrong one reached a slide. So this reads the DOCUMENT and looks for the MODEL's numbers,
rather than trusting that they were copied correctly.

Run:  python cost_estimation/check_roi_doc.py     (exit 0 = every figure found)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE.parent / "roi_risk_assessment.md"
M = json.loads((HERE / "roi_model.json").read_text())

text = DOC.read_text()
norm = text.replace(",", "").replace("−", "-")     # strip separators and unicode minus


def money(v) -> str:
    return f"{round(v):,}".replace(",", "")


CHECKS: list[tuple[str, str]] = []
for k, v in M["annual_value_eur"].items():
    CHECKS.append((f"value: {k}", money(v)))
for k, v in M["annual_running_cost_eur"].items():
    if v >= 1:
        CHECKS.append((f"running cost: {k}", money(v)))
CHECKS += [
    ("running cost total", money(M["annual_running_cost_total_eur"])),
    ("upfront to end of pilot", money(M["upfront_to_end_of_pilot_eur"])),
    ("upfront full", money(M["upfront_full_eur"])),
    ("round 1 upfront", money(M["round1_upfront_full_eur"])),
    ("scope multiple", str(M["scope_multiple_for_3x_capabilities"])),
    ("break-even volume", money(M["break_even_volume"]["complaints_per_year_for_36m_payback"])),
    ("accounts implied", money(M["break_even_volume"]["retail_accounts_implied"])),
    ("client volume", money(M["break_even_volume"]["this_client_complaints_per_year"])),
    ("per-client build", money(M["productised"]["per_client_build_eur"])),
    ("break-even month, central", str(M["scenarios"]["central"]["break_even_month"])),
]
for name, sc in M["scenarios"].items():
    CHECKS.append((f"{name}: annual value", money(sc["annual_value_eur"])))
    for h in ("roi_12m", "roi_36m"):
        r = sc[h]
        CHECKS += [(f"{name} {h}: benefit", money(r["total_benefit_eur"])),
                   (f"{name} {h}: cost", money(r["total_cost_eur"])),
                   (f"{name} {h}: net", money(abs(r["net_benefit_eur"]))),
                   (f"{name} {h}: ROI", f"{abs(r['roi_pct'])}")]
for k, v in M["levers_36m_central_roi_pct"].items():
    CHECKS.append((f"lever: {k}", f"{abs(v)}"))
for k, v in M["sensitivity_36m_central_roi_pct"].items():
    CHECKS.append((f"sensitivity: {k}", f"{abs(v)}"))

missing = [(n, s) for n, s in CHECKS if not re.search(rf"(?<![\d.]){re.escape(s)}(?![\d])", norm)]

print(f"{len(CHECKS)} figures checked against {DOC.name}")
if missing:
    print(f"\n{len(missing)} NOT FOUND in the document:")
    for n, s in missing:
        print(f"  {s:>12}   {n}")
    sys.exit(1)
print("every model figure appears in the document")
