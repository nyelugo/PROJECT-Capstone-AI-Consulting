"""Precompute the two standing work queues. Run once; commit the result.

Why precompute rather than classify live on the page. Sixty model calls while a panel
watches is sixty chances for a network to fail, and the guard behaviour being demonstrated
is identical either way. Precomputing also makes the queue *the same every time*, which is
what lets you rehearse a demo — and what lets a grader see what you saw.

Deterministic: fixed seed, fixed sample, temperature 0. Rerunning replaces the queue with
an equivalent one, so only rerun deliberately.

Run:  python -m mvp.build_queues            (about a minute, roughly one cent)
      python -m mvp.build_queues --triage 40
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from .capabilities.anomaly import Anomaly, detect
from .capabilities.triage import Triage
from .queue_store import ANOMALY_FILE, QUEUES, TRIAGE_FILE
from .runtime import call_model, pseudonymise
from .spine import run

CORPUS = Path(__file__).resolve().parents[1] / "data" / "complaints_triage.csv.gz"
SEED = 20260831
DEFAULT_N = 60          # matches the Round 1 evaluation sample, so rates stay comparable
WORKERS = 8


def _sample(n: int) -> pd.DataFrame:
    """Stratified by product, so the queue looks like a real day's intake rather than a
    pile of credit-card disputes. Deterministic."""
    df = pd.read_csv(CORPUS, parse_dates=["Date received"])
    df = df[df["Consumer complaint narrative"].str.len().between(120, 4000)]
    share = df["Product"].value_counts(normalize=True)
    out = []
    for product, frac in share.items():
        take = max(2, round(n * frac))
        sub = df[df["Product"] == product]
        out.append(sub.sample(min(take, len(sub)), random_state=SEED))
    return (pd.concat(out).sample(frac=1, random_state=SEED)
            .head(n).sort_values("Date received", ascending=False).reset_index(drop=True))


def build_triage(n: int) -> list[dict]:
    cap, rows = Triage(), _sample(n)
    print(f"triage: classifying {len(rows)} complaints…")

    def one(r):
        narrative = r["Consumer complaint narrative"]
        d = run(cap, {"complaint_id": r["Complaint ID"], "product": r["Product"],
                      "narrative": narrative}, call=call_model)
        return {
            "item_id": f"t-{d.ref}",
            "ref": d.ref,
            "received": r["Date received"].date().isoformat(),
            "product": r["Product"],
            "narrative": narrative,
            "decision": d.decision,
            "reason_code": d.reason_code,
            "reason": d.reason,
            "proposed_team": cap.team(d.payload) if d.payload.get("queue") else "—",
            "proposed_queue": d.payload.get("queue") or "",
            "confidence": d.confidence,
            "evidence": d.payload.get("evidence", ""),
            "grounding": d.grounding_detail,
            "latency_ms": d.latency_ms,
            "model": d.model,
        }

    with ThreadPoolExecutor(WORKERS) as ex:
        items = list(ex.map(one, (r for _, r in rows.iterrows())))
    return items


def build_anomaly() -> list[dict]:
    cap, cands = Anomaly(), detect()
    print(f"anomaly: explaining {len(cands)} candidates…")

    def one(c):
        d = run(cap, {"candidate": c}, call=call_model)
        return {
            "item_id": c["candidate_id"],
            "ref": d.ref,
            "raised": c["date"],
            "rule": c["rule"],
            "txn_count": c["txn_count"],
            "amount_eur": c["amount_eur"],
            "account_median_eur": c["account_median_eur"],
            "times_normal": c["times_normal"],
            "category": c["category"],
            "channel": c["channel"],
            "country": c["country"],
            "decision": d.decision,
            "reason_code": d.reason_code,
            "reason": d.reason,
            "confidence": d.confidence,
            "explanation": d.payload.get("explanation", ""),
            "next_check": d.payload.get("next_check", ""),
            "grounding": d.grounding_detail,
            "latency_ms": d.latency_ms,
            "model": d.model,
        }

    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(one, cands))


def _report(name: str, items: list[dict]) -> None:
    held = [i for i in items if i["decision"] != "PROPOSE_TO_HANDLER"]
    codes: dict[str, int] = {}
    for i in held:
        codes[i["reason_code"]] = codes.get(i["reason_code"], 0) + 1
    print(f"  {name}: {len(items)} items · {len(items)-len(held)} proposed · {len(held)} held")
    for c, n in sorted(codes.items(), key=lambda kv: -kv[1]):
        print(f"      {n:>3}  {c}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--triage", type=int, default=DEFAULT_N)
    ap.add_argument("--skip-anomaly", action="store_true")
    ap.add_argument("--skip-triage", action="store_true")
    a = ap.parse_args()

    QUEUES.mkdir(parents=True, exist_ok=True)
    if not a.skip_triage:
        t = build_triage(a.triage)
        TRIAGE_FILE.write_text(json.dumps(t, indent=2))
        _report("triage", t)

    if not a.skip_anomaly:
        an = build_anomaly()
        ANOMALY_FILE.write_text(json.dumps(an, indent=2))
        _report("anomaly", an)

    print(f"\nwritten to {QUEUES}")
