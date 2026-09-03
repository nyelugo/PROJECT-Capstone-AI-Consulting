"""Generate the synthetic transaction batch UC-2 runs on. Deterministic.

Why synthetic. The CFPB corpus is complaints, not transactions — there is no public
transaction ledger with the fields anomaly detection needs, and using real customer
transactions is out of the question. The brief permits it explicitly: "Public or synthetic
data only — no real personal data from live clients."

What makes it honest rather than convenient: **every anomaly is planted with its type
recorded**, so the detector can be scored against ground truth instead of demonstrated on
cases chosen to make it look good. `planted_type` is the label; the detector never sees it.
This is the ground truth that UC-1 conspicuously lacks — and saying so out loud is the
point. A synthetic dataset can be measured against truth precisely because the truth was
manufactured. That is also its limit: it proves the detector finds the anomalies *we*
planted, not the ones a real fraudster would invent.

Account references are pseudonymous from the moment of creation. There is no real
identifier to strip because none is ever generated.

Run:  python -m mvp.synth.make_transactions
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parent / "transactions.csv"
SEED = 20260831
N_ACCOUNTS = 200
DAYS = 90
START = date(2026, 4, 1)

CATEGORIES = ["groceries", "fuel", "restaurants", "utilities", "online retail",
              "travel", "electronics", "pharmacy", "transfer"]
CHANNELS = ["card_present", "card_not_present", "mobile_app", "online_banking"]
HOME = "IE"
FOREIGN = ["RO", "TR", "BR", "NG", "UA", "PH"]

# The four planted patterns. Each is a shape a real monitoring team would want raised.
PLANTED = ["amount_spike", "rapid_burst", "new_country_new_device", "threshold_structuring"]


def _accounts(rng: random.Random) -> list[dict]:
    accs = []
    for i in range(N_ACCOUNTS):
        accs.append({
            "account_ref": f"acc_{i:04d}",
            # each account has its own spending scale — the whole point of the detector is
            # that "large" is relative to the account, not to the population
            "typical": rng.choice([18.0, 32.0, 55.0, 90.0, 140.0, 220.0]),
            "per_day": rng.choice([0.4, 0.8, 1.4, 2.2]),
        })
    return accs


def build() -> pd.DataFrame:
    rng = random.Random(SEED)
    accs = _accounts(rng)
    rows: list[dict] = []
    tid = 0

    def add(acc, day, amount, *, category=None, channel=None, country=HOME,
            device_new=False, planted=""):
        nonlocal tid
        tid += 1
        rows.append({
            "txn_id": f"t{tid:06d}",
            "account_ref": acc["account_ref"],
            "date": (START + timedelta(days=day)).isoformat(),
            "amount_eur": round(amount, 2),
            "category": category or rng.choice(CATEGORIES),
            "channel": channel or rng.choice(CHANNELS),
            "country": country,
            "device_new": device_new,
            "planted_type": planted,
        })

    # -- ordinary activity
    for acc in accs:
        for day in range(DAYS):
            for _ in range(rng.poisson(acc["per_day"]) if hasattr(rng, "poisson")
                           else (1 if rng.random() < acc["per_day"] / 2 else 0)):
                add(acc, day, max(1.0, rng.lognormvariate(0, 0.55) * acc["typical"]))

    # -- planted anomalies, one kind per handful of accounts, on known days
    for n, acc in enumerate(accs):
        kind = PLANTED[n % len(PLANTED)]
        if n % 4 != 0 and rng.random() < 0.45:
            continue                                   # not every account gets one
        day = rng.randrange(20, DAYS - 3)
        if kind == "amount_spike":
            add(acc, day, acc["typical"] * rng.uniform(14, 30),
                category="electronics", channel="card_not_present", planted=kind)
        elif kind == "rapid_burst":
            for _ in range(rng.randrange(7, 12)):
                add(acc, day, acc["typical"] * rng.uniform(0.7, 1.3),
                    category="online retail", channel="card_not_present", planted=kind)
        elif kind == "new_country_new_device":
            for _ in range(rng.randrange(2, 5)):
                add(acc, day, acc["typical"] * rng.uniform(1.5, 4.0),
                    category="travel", channel="card_present",
                    country=rng.choice(FOREIGN), device_new=True, planted=kind)
        elif kind == "threshold_structuring":
            for k in range(rng.randrange(3, 6)):
                add(acc, day + (k // 2), rng.choice([980.0, 985.0, 990.0, 995.0]),
                    category="transfer", channel="online_banking", planted=kind)

    df = pd.DataFrame(rows).sort_values(["date", "txn_id"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = build()
    df.to_csv(OUT, index=False)
    planted = df[df["planted_type"] != ""]
    print(f"wrote {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}")
    print(f"  {len(df):,} transactions · {df['account_ref'].nunique()} accounts · "
          f"{df['date'].min()} to {df['date'].max()}")
    print(f"  {len(planted):,} planted anomalous transactions across "
          f"{planted['account_ref'].nunique()} accounts")
    print(planted["planted_type"].value_counts().to_string())
