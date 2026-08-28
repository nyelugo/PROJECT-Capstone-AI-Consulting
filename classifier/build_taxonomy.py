"""Derive the routing taxonomy from the corpus, once, into taxonomy.json.

A complaint always arrives attached to a product, and the CFPB issue list is
product-scoped - 'Managing an account' exists only under checking/savings, 'Problem with
a purchase shown on your statement' only under credit card. So the routing decision is
always 'which of THIS product's queues', never 'which of all 64'.

Issues below MIN_SHARE of their product are folded into OTHER rather than given a queue
of their own: too rare to route reliably, and a wrong confident answer costs more than
an honest handover.
"""
import json
from pathlib import Path

import pandas as pd

MIN_SHARE = 0.01
ROOT = Path(__file__).resolve().parents[1]

df = pd.read_csv(ROOT / "data" / "complaints_dashboard.csv")
tax, coverage = {}, {}
for product, g in df.groupby("Product"):
    vc = g["Issue"].value_counts()
    keep = vc[vc / len(g) >= MIN_SHARE]
    tax[product] = sorted(keep.index.tolist()) + ["OTHER"]
    coverage[product] = {"n": int(len(g)), "queues": int(len(keep)),
                         "covered_pct": round(100 * keep.sum() / len(g), 1)}

out = {"min_share": MIN_SHARE, "products": tax, "coverage": coverage}
(Path(__file__).parent / "taxonomy.json").write_text(json.dumps(out, indent=2))

for p, c in sorted(coverage.items(), key=lambda kv: -kv[1]["n"]):
    print(f"{c['n']:>5} complaints | {c['queues']:>2} queues | {c['covered_pct']:>5.1f}% covered | {p}")
print(f"\ntotal routable coverage: "
      f"{100 * sum(c['n'] * c['covered_pct'] / 100 for c in coverage.values()) / len(df):.1f}%")
