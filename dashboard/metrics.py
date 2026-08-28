"""Single source of truth for every number shown to a stakeholder.

The dashboard, the research docs and the cost model all read their figures from
here, so a number cannot say one thing on a slide and another in a document.
"""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "complaints_dashboard.csv"

# The corpus is cut at the last date with complete published data. See data_prep.py.
WINDOW_START, WINDOW_END = "2026-05-01", "2026-06-27"
# 2026-W18 opens mid-week (window starts on a Friday), so it is not a complete week.
PARTIAL_WEEKS = {"2026-W18"}
TOP_N_ISSUES = 5


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["Date received"])
    df["monetary_relief"] = df["Company response to consumer"].eq("Closed with monetary relief")
    df["any_relief"] = df["Company response to consumer"].isin(
        ["Closed with monetary relief", "Closed with non-monetary relief"])
    df["untimely"] = df["Timely response?"].eq("No")
    return df


def headline(df: pd.DataFrame) -> dict:
    top = df["Issue"].value_counts().head(TOP_N_ISSUES)
    return {
        "complaints": len(df),
        "firms": df["Company"].nunique(),
        "issue_classes": df["Issue"].nunique(),
        "timely_pct": 100 * (1 - df["untimely"].mean()),
        "untimely_n": int(df["untimely"].sum()),
        "any_relief_pct": 100 * df["any_relief"].mean(),
        "monetary_pct": 100 * df["monetary_relief"].mean(),
        "top5_share_pct": 100 * top.sum() / len(df),
        "no_resolution_n": int(df["Company response to consumer"].eq("Untimely response").sum()),
        "median_chars": df["narrative_chars"].median(),
        "p90_chars": df["narrative_chars"].quantile(0.90),
    }


def weekly_volume(df: pd.DataFrame) -> pd.DataFrame:
    w = df[~df["week"].isin(PARTIAL_WEEKS)].groupby("week").size().reset_index(name="complaints")
    return w.sort_values("week")


def by_product(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("Product").agg(
        complaints=("Complaint ID", "size"),
        monetary_pct=("monetary_relief", lambda s: 100 * s.mean()),
    ).reset_index()
    g["short"] = g["Product"].replace({
        "Checking or savings account": "Checking / savings",
        "Money transfer, virtual currency, or money service": "Money transfer",
        "Payday loan, title loan, personal loan, or advance loan": "Personal loan",
        "Vehicle loan or lease": "Vehicle loan",
        "Credit card": "Credit card",
        "Prepaid card": "Prepaid card",
    })
    return g.sort_values("complaints", ascending=False)


def top_issues(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    t = df["Issue"].value_counts().head(n).reset_index()
    t.columns = ["Issue", "complaints"]
    t["share_pct"] = 100 * t["complaints"] / len(df)
    t["in_top5"] = t.index < TOP_N_ISSUES
    return t


# "Untimely response" is the CFPB's *outcome* field, not its timeliness flag. It marks
# cases where no resolution was ever recorded. It is a different measure from
# "Timely response? = No" (335 here, of which 214 still closed with an explanation), so
# it is relabelled to what it actually means and never shown as a timeliness figure.
OUTCOME_LABELS = {
    "Closed with explanation": "Resolved with an explanation",
    "Closed with monetary relief": "Resolved, money paid back",
    "Closed with non-monetary relief": "Resolved, put right another way",
    "Untimely response": "No resolution recorded",
    "In progress": "Still open",
}


def resolution_mix(df: pd.DataFrame) -> pd.DataFrame:
    r = df["Company response to consumer"].value_counts().reset_index()
    r.columns = ["outcome", "complaints"]
    r["share_pct"] = 100 * r["complaints"] / len(df)
    r["outcome"] = r["outcome"].map(OUTCOME_LABELS).fillna(r["outcome"])
    return r


if __name__ == "__main__":
    import json
    d = load()
    print(json.dumps({k: (round(v, 1) if isinstance(v, float) else v)
                      for k, v in headline(d).items()}, indent=2))
