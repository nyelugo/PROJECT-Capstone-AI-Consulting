"""Curate the public CFPB complaint corpus into the working slice for this capstone.

Source : CFPB Consumer Complaint Database public API (no auth; no personal data -
         the CFPB scrubs narratives before publication).
Pulled : 2026-05-01 .. 2026-08-01, narrative-bearing complaints only (36,022 records).

Two data-quality corrections applied here, both verified before use:

1. PUBLICATION LAG. The CFPB publishes a complaint only after the company responds or
   15 days elapse, so the most recent weeks are incomplete. Weekday volume holds at
   1,700-2,270/week through 2026-06-28 and then falls to 607 -> 430 -> 555 -> 418 -> 244.
   That cliff is publication lag, not a fall in complaints. The ANALYSIS WINDOW is
   therefore cut at 2026-06-28; later records are kept in the raw pull but excluded
   from every rate and trend.

2. DEAD METRIC. 'days to company' is 0 for 96% of records - it measures CFPB routing
   latency, not the firm's handling speed, and cannot support an ops SLA metric.
   It is dropped rather than shown.

Scope  : products a mid-size consumer bank / lender actually operates. Debt collection,
         mortgage, student loan and credit-reporting complaints are excluded - they are
         overwhelmingly filed against third-party collectors, mortgage specialists and
         the credit bureaus, not against a firm of Chleo's shape.
"""
import pandas as pd

RAW = "data/raw/cfpb_2026Q2.csv"
WINDOW_END = "2026-06-28"          # last date with complete published data
IN_SCOPE = [
    "Checking or savings account",
    "Credit card",
    "Money transfer, virtual currency, or money service",
    "Vehicle loan or lease",
    "Payday loan, title loan, personal loan, or advance loan",
    "Prepaid card",
]

df = pd.read_csv(RAW, low_memory=False)
df["Date received"] = pd.to_datetime(df["Date received"], format="mixed", utc=True)

cur = df[df["Product"].isin(IN_SCOPE)].copy()
cur = cur[cur["Date received"] <= pd.Timestamp(WINDOW_END, tz="UTC")]
cur["month"] = cur["Date received"].dt.strftime("%Y-%m")
cur["week"] = cur["Date received"].dt.strftime("%G-W%V")
cur["narrative_chars"] = cur["Consumer complaint narrative"].fillna("").str.len()
cur["monetary_relief"] = cur["Company response to consumer"].eq("Closed with monetary relief")
cur["any_relief"] = cur["Company response to consumer"].isin(
    ["Closed with monetary relief", "Closed with non-monetary relief"])
cur["untimely"] = cur["Timely response?"].eq("No")

print(f"analysis window : {cur['Date received'].min().date()} -> {cur['Date received'].max().date()}")
print(f"in-scope records: {len(cur)}")
print(f"distinct firms  : {cur['Company'].nunique()} | distinct issues: {cur['Issue'].nunique()}")
print(f"timely response : {100*(1-cur['untimely'].mean()):.1f}%   (untimely n={cur['untimely'].sum()})")
print(f"any relief      : {100*cur['any_relief'].mean():.1f}%")
print(f"monetary relief : {100*cur['monetary_relief'].mean():.1f}%")
print(f"narrative chars : median {cur['narrative_chars'].median():.0f}, 90th pct {cur['narrative_chars'].quantile(.9):.0f}")

print("\n--- volume + monetary relief rate by product ---")
agg = cur.groupby("Product").agg(n=("Complaint ID", "size"),
                                 monetary_pct=("monetary_relief", lambda s: round(100*s.mean(), 1)))
print(agg.sort_values("n", ascending=False).to_string())
print("\n--- top 12 issues (triage classes) ---")
print(cur["Issue"].value_counts().head(12).to_string())
print("\n--- weekly volume (complete weeks only) ---")
print(cur["week"].value_counts().sort_index().to_string())
print("\n--- top 8 states ---")
print(cur["State"].value_counts().head(8).to_string())

dash_cols = ["Date received", "month", "week", "Product", "Sub-product", "Issue", "Sub-issue",
             "Company", "State", "Company response to consumer", "Timely response?",
             "narrative_chars", "Complaint ID"]
cur[dash_cols].to_csv("data/complaints_dashboard.csv", index=False)
cur[["Complaint ID", "Date received", "Product", "Sub-product", "Issue", "Sub-issue",
     "Consumer complaint narrative", "Company response to consumer",
     "Timely response?"]].to_csv("data/complaints_triage.csv.gz", index=False, compression="gzip")
print("\nwrote data/complaints_dashboard.csv + data/complaints_triage.csv.gz")
