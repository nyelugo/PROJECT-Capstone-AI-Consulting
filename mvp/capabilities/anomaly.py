"""UC-2 — Anomaly flagging. Explains why a transaction pattern was raised.

The division of labour here is the whole design, and it is deliberately not "the LLM finds
the fraud":

    a deterministic detector decides WHAT is unusual        (arithmetic, reproducible)
    the model explains WHY, in language an analyst can act on (fluent, checkable)
    a human decides WHETHER to escalate                      (as in every capability)

A language model is a poor detector — it cannot compute a baseline, it is not reproducible,
and its mistakes are unauditable. It is a good explainer. So the model never selects a
candidate and never scores one; it is handed a candidate the detector already found, with
that candidate's actual figures, and asked to write the case note. Its output is then
checked back against those figures.

Grounding rule: every number in the explanation must match the candidate record.

The standing guardrail from Round 1 carries over unchanged: **a predicted payout never
orders the queue.** Candidates are ranked by how far the pattern departs from the account's
OWN baseline, never by the money involved, so a large-but-normal transaction on a
high-spending account does not outrank a small-but-impossible one on a modest account.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from ..runtime import pseudonymise
from ..spine import parse_json_object

DATA = Path(__file__).resolve().parents[1] / "synth" / "transactions.csv"
MODEL = "gpt-4o-mini"
THRESHOLD = 0.70

HOME_COUNTRY = "IE"
SPIKE_RATIO = 8.0          # times the account's own median
BURST_MIN = 6              # transactions by one account in one day
STRUCT_LO, STRUCT_HI = 900.0, 1000.0
STRUCT_MIN = 3             # transactions just under the threshold within the window
STRUCT_DAYS = 3

# RULES describes each pattern; RULE_LABEL names it. The key itself is storage vocabulary and
# must reach neither a column nor the model — a prompt that is handed "amount_spike" gets it
# quoted back inside the case note an analyst reads.
RULE_LABEL = {
    "amount_spike": "Amount spike",
    "rapid_burst": "Rapid burst",
    "new_country_new_device": "New country, new device",
    "threshold_structuring": "Threshold structuring",
}
CHANNEL_LABEL = {
    "card_present": "Card present", "card_not_present": "Card not present",
    "mobile_app": "Mobile app", "online_banking": "Online banking",
}

def channel_label(value) -> str:
    """Channel names for the eye. A candidate spans several transactions, so this field can
    hold a comma-separated set — the same shape `country` already takes."""
    return ", ".join(CHANNEL_LABEL.get(p.strip(), p.strip()) for p in str(value).split(","))


RULES = {
    "amount_spike": "a single amount far above this account's own normal",
    "rapid_burst": "many transactions from one account in one day",
    "new_country_new_device": "spending abroad on a device never seen before",
    "threshold_structuring": "repeated amounts sitting just under a round threshold",
}


@lru_cache(maxsize=1)
def load() -> pd.DataFrame:
    df = pd.read_csv(DATA, parse_dates=["date"])
    df["planted_type"] = df["planted_type"].fillna("")
    return df


@lru_cache(maxsize=1)
def detect() -> list[dict]:
    """Find candidates. Deterministic, no model, no randomness — the same batch in, the
    same candidates out, every time. An explanation that cannot be reproduced is not
    evidence, and a demo that shows something different on the day is worse than none."""
    df = load()
    out: list[dict] = []
    base = df.groupby("account_ref")["amount_eur"].median().rename("median_eur")

    for acc, g in df.groupby("account_ref"):
        med = float(base[acc])
        g = g.sort_values("date")

        for r in g[g["amount_eur"] > med * SPIKE_RATIO].itertuples():
            out.append({
                "rule": "amount_spike", "account_ref": acc,
                "date": r.date.date().isoformat(), "txn_ids": [r.txn_id],
                "txn_count": 1, "amount_eur": float(r.amount_eur),
                "account_median_eur": round(med, 2),
                "times_normal": round(float(r.amount_eur) / med, 1),
                "category": r.category, "channel": r.channel, "country": r.country,
                "planted_type": r.planted_type,
            })

        for day, dg in g.groupby(g["date"].dt.date):
            if len(dg) >= BURST_MIN:
                out.append({
                    "rule": "rapid_burst", "account_ref": acc, "date": day.isoformat(),
                    "txn_ids": list(dg["txn_id"]), "txn_count": int(len(dg)),
                    "amount_eur": round(float(dg["amount_eur"].sum()), 2),
                    "account_median_eur": round(med, 2),
                    "times_normal": round(float(dg["amount_eur"].sum()) / med, 1),
                    "category": dg["category"].mode().iloc[0],
                    "channel": dg["channel"].mode().iloc[0],
                    "country": dg["country"].mode().iloc[0],
                    "planted_type": dg["planted_type"].mode().iloc[0],
                })

        fg = g[(g["country"] != HOME_COUNTRY) & (g["device_new"])]
        for day, dg in fg.groupby(fg["date"].dt.date):
            out.append({
                "rule": "new_country_new_device", "account_ref": acc, "date": day.isoformat(),
                "txn_ids": list(dg["txn_id"]), "txn_count": int(len(dg)),
                "amount_eur": round(float(dg["amount_eur"].sum()), 2),
                "account_median_eur": round(med, 2),
                "times_normal": round(float(dg["amount_eur"].sum()) / med, 1),
                "category": dg["category"].mode().iloc[0],
                "channel": dg["channel"].mode().iloc[0],
                "country": ", ".join(sorted(dg["country"].unique())),
                "planted_type": dg["planted_type"].mode().iloc[0],
            })

        sg = g[g["amount_eur"].between(STRUCT_LO, STRUCT_HI, inclusive="left")]
        if len(sg) >= STRUCT_MIN:
            span = (sg["date"].max() - sg["date"].min()).days
            if span <= STRUCT_DAYS:
                out.append({
                    "rule": "threshold_structuring", "account_ref": acc,
                    "date": sg["date"].min().date().isoformat(),
                    "txn_ids": list(sg["txn_id"]), "txn_count": int(len(sg)),
                    "amount_eur": round(float(sg["amount_eur"].sum()), 2),
                    "account_median_eur": round(med, 2),
                    "times_normal": round(float(sg["amount_eur"].sum()) / med, 1),
                    "category": sg["category"].mode().iloc[0],
                    "channel": sg["channel"].mode().iloc[0],
                    "country": sg["country"].mode().iloc[0],
                    "planted_type": sg["planted_type"].mode().iloc[0],
                })

    # Ranked by departure from the account's OWN baseline. Never by amount. See the
    # guardrail in the module docstring.
    out.sort(key=lambda c: c["times_normal"], reverse=True)
    for i, c in enumerate(out):
        c["candidate_id"] = f"cand_{i:03d}"
    return out


def score() -> dict:
    """Score the detector against the planted ground truth.

    READ THE CAVEAT BEFORE QUOTING THE NUMBER. Recall here is ~100%, and that is not an
    achievement — the detector's thresholds and the generator's planting rules were written
    by the same author, so this measures whether the code agrees with itself. It is
    structurally the same trap as Round 1's 60.5%: a number that looks like accuracy and is
    actually agreement. The caveat travels with the figure, in the return value, so the
    number cannot be lifted onto a slide without it.

    What it does legitimately establish: the detector is deterministic, it covers all four
    patterns rather than only the easy one, and its false-positive rate on ordinary traffic
    is measurable. What it cannot establish: how it performs against a pattern nobody
    thought to plant. Only a pilot on real traffic answers that.
    """
    df = load()
    cands = detect()
    flagged = {t for c in cands for t in c["txn_ids"]}
    planted = set(df.loc[df["planted_type"] != "", "txn_id"])
    tp = len(flagged & planted)
    by_type = {}
    for k, g in df[df["planted_type"] != ""].groupby("planted_type"):
        ids = set(g["txn_id"])
        by_type[k] = {"planted": len(ids), "found": len(ids & flagged),
                      "recall_pct": round(100 * len(ids & flagged) / len(ids), 1)}
    return {
        "candidates": len(cands),
        "transactions_flagged": len(flagged),
        "planted": len(planted),
        "recall_pct": round(100 * tp / len(planted), 1) if planted else 0.0,
        "precision_pct": round(100 * tp / len(flagged), 1) if flagged else 0.0,
        "by_type": by_type,
        "caveat": ("Detector thresholds and the data generator were written together, so "
                   "this is self-agreement, not a detection rate. It cannot be reported as "
                   "accuracy. Only a pilot on real traffic measures that."),
    }


# An ordinal is not a claimed figure. "the 90th percentile" was being read as the number 90
# and rejected as uncomputed, which stopped a correct section during a live run. The
# quantifier is possessive so the engine cannot backtrack into the middle of "90th" and
# match a bare 9; a multiplier like "10.8x" is still a figure and still checked.
# The repeated group keeps a grouped decimal whole: "EUR 1,660.29" was being read as
# 1660 AND 29, and the stray 29 matched nothing in the record, so a correctly grounded
# note would have been rejected the first time one was written with a separator.
_NUM = re.compile(r"\b\d++(?:[.,]\d++)*+(?!(?:st|nd|rd|th)\b)")


def _numbers_in(text: str) -> list[float]:
    out = []
    for m in _NUM.finditer(text or ""):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            pass
    return out


def _allowed(c: dict) -> set[float]:
    a = {float(c["amount_eur"]), float(c["account_median_eur"]), float(c["times_normal"]),
         float(c["txn_count"])}
    a |= set(_numbers_in(c["date"]))
    df = load()
    a |= {float(v) for v in df.loc[df["txn_id"].isin(c["txn_ids"]), "amount_eur"]}
    return a


@lru_cache(maxsize=1)
def _txns_by_candidate() -> dict:
    """candidate_id -> the transaction ids behind it."""
    return {c["candidate_id"]: list(c["txn_ids"]) for c in detect()}


def transactions_for(candidate_id: str):
    """The individual rows behind a candidate, oldest first.

    Derived from detect() rather than read off the queue. detect() is deterministic — same
    batch, same candidates, same ids — so this cannot disagree with what was flagged, and it
    needs no queue rebuild, which would re-call the model for every item and replace the
    batch the screenshots and the demo recording show.
    """
    ids = _txns_by_candidate().get(candidate_id, [])
    df = load()
    return df[df["txn_id"].isin(ids)].sort_values("date")


class Anomaly:
    name = "anomaly"
    title = "Anomaly flagging"
    threshold = THRESHOLD
    model = MODEL

    def ref(self, request: dict) -> str:
        return pseudonymise(request.get("candidate", {}).get("account_ref", "unknown"))

    def validate(self, request: dict) -> str | None:
        c = request.get("candidate")
        if not isinstance(c, dict) or "candidate_id" not in c:
            return "no candidate supplied — the detector selects, the model only explains"
        if c.get("rule") not in RULES:
            return f"'{c.get('rule')}' is not a rule this detector runs"
        return None

    def messages(self, request: dict) -> list[dict]:
        c = request["candidate"]
        system = (
            "You write case notes for a bank's transaction monitoring team. You do not "
            "decide whether anything is fraud, you do not block anything, and you do not "
            "contact customers. An analyst reads your note and decides.\n\n"
            "You are given a candidate that a deterministic detector has already raised, "
            "with its actual figures. Explain to the analyst, in plain language, what the "
            "pattern is and why it was raised.\n\n"
            "Rules:\n"
            "- Use ONLY the figures given. Never state a number that is not in the "
            "candidate record. Do not calculate anything new.\n"
            "- Do not assert that this IS fraud. Describe the pattern; the analyst judges.\n"
            "- Say what would most quickly confirm or dismiss it — one concrete check.\n"
            "- Write 2 to 4 sentences.\n"
            "- confidence is how well the figures support raising this at all. If the "
            "pattern looks weak or ordinary, say so with a low confidence.\n\n"
            'Respond with JSON only:\n'
            '{"explanation": "<2-4 sentences>", "next_check": "<one concrete check>", '
            '"confidence": <number 0-1>}')
        user = (
            f"Candidate {c['candidate_id']}\n"
            f"Pattern: {RULE_LABEL[c['rule']]} — {RULES[c['rule']]}\n"
            f"Account: {c['account_ref']} (pseudonymous)\n"
            f"Date: {c['date']}\n"
            f"Transactions in this candidate: {c['txn_count']}\n"
            f"Total amount: EUR {c['amount_eur']}\n"
            f"This account's median transaction: EUR {c['account_median_eur']}\n"
            f"Times that median: {c['times_normal']}\n"
            f"Category: {c['category']}   "
            f"Channel: {CHANNEL_LABEL.get(c['channel'], c['channel'])}   "
            f"Country: {c['country']}")
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def parse(self, text: str) -> dict:
        o = parse_json_object(text)
        if not str(o.get("explanation", "")).strip():
            raise ValueError("model returned an empty explanation")
        return {"explanation": str(o.get("explanation", "")).strip(),
                "next_check": str(o.get("next_check", "")).strip(),
                "confidence": o.get("confidence")}

    def scope_check(self, parsed: dict, request: dict) -> str | None:
        c = request["candidate"]
        known = set(load()["txn_id"])
        if not c["txn_ids"] or any(t not in known for t in c["txn_ids"]):
            return "REJECT_ACCOUNT_NOT_IN_LEDGER"
        return None

    def grounding_check(self, parsed: dict, request: dict) -> tuple[str | None, str]:
        c = request["candidate"]
        allowed = _allowed(c)
        text = f"{parsed['explanation']} {parsed['next_check']}"
        bad = []
        for n in _numbers_in(text):
            tol = 0.55 if float(n).is_integer() else 0.055
            if not any(abs(a - n) <= tol for a in allowed):
                bad.append(n)
        if bad:
            return ("REJECT_VALUE_MISMATCH",
                    "value(s) in the note do not match the transaction record: "
                    + ", ".join(f"{b:g}" for b in bad[:4]))
        return None, f"all {len(_numbers_in(text))} value(s) match the transaction record"

    def summarise(self, parsed: dict, request: dict) -> str:
        c = request["candidate"]
        return (f"Raise {c['candidate_id']} — {RULE_LABEL.get(c['rule'], c['rule'])}, "
                f"{c['times_normal']}x this account's normal")

    def citations(self, parsed: dict, request: dict | None = None) -> list[str]:
        return [parsed["next_check"]] if parsed.get("next_check") else []
