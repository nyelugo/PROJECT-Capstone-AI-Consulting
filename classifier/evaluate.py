"""Measure the triage prompt against the real corpus, before it ships anywhere.

Ground truth is the CFPB's own Issue label, folded to OTHER where the issue is below the
taxonomy's 1% floor for its product. Sampling is per-product so every product gets a
readable score; the headline is then re-weighted by real product volume so it reflects
the mix an actual inbox would see.

The number that matters is not overall accuracy. It is **accuracy on what gets routed
automatically** — the complaints no human looks at.

Usage:
    python classifier/evaluate.py [n_per_product]
"""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prompt as P
import teams as T

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
SEED = 42


def load_key() -> str:
    m = re.search(r"^OPENAI_API_KEY=(.+)$",
                  (Path.home() / ".config/ironhack/.env.local").read_text(), re.M)
    if not m:
        raise SystemExit("OPENAI_API_KEY not found in ~/.config/ironhack/.env.local")
    return m.group(1).strip().strip('"').strip("'")


def sample(n_per_product: int) -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "complaints_triage.csv.gz")
    parts = []
    for product, queues in P.PRODUCT_QUEUES.items():
        g = df[df["Product"] == product]
        if g.empty:
            continue
        parts.append(g.sample(min(n_per_product, len(g)), random_state=SEED))
    s = pd.concat(parts).reset_index(drop=True)
    s["truth"] = [row.Issue if row.Issue in P.PRODUCT_QUEUES.get(row.Product, []) else "OTHER"
                  for row in s.itertuples()]
    return s


def classify(client: OpenAI, product: str, narrative: str, model: str = P.MODEL) -> dict:
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": P.SYSTEM_PROMPT},
                      {"role": "user", "content": P.build_user_message(product, narrative)}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        out = json.loads(r.choices[0].message.content)
        return {"queue": str(out.get("queue", "OTHER")),
                "confidence": float(out.get("confidence", 0.0)),
                "evidence": str(out.get("evidence", "")),
                "tokens": r.usage.total_tokens}
    except Exception as e:                                   # noqa: BLE001
        return {"queue": "ERROR", "confidence": 0.0, "evidence": str(e)[:120], "tokens": 0}


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    model = sys.argv[2] if len(sys.argv) > 2 else P.MODEL
    client = OpenAI(api_key=load_key())
    s = sample(n)
    print(f"evaluating {len(s)} complaints ({n} per product across "
          f"{s['Product'].nunique()} products)...")

    with ThreadPoolExecutor(max_workers=10) as ex:
        preds = list(ex.map(lambda t: classify(client, t[0], t[1], model),
                            zip(s["Product"], s["Consumer complaint narrative"])))

    s["pred"] = [p["queue"] for p in preds]
    s["confidence"] = [p["confidence"] for p in preds]
    s["evidence"] = [p["evidence"] for p in preds]
    s["tokens"] = [p["tokens"] for p in preds]
    s["routed"] = [P.route(pr, p["queue"], p["confidence"]) for pr, p in zip(s["Product"], preds)]
    s["correct"] = s["pred"] == s["truth"]
    s["truth_team"] = s["truth"].map(T.team_for)
    s["pred_team"] = s["pred"].map(T.team_for)
    s["team_correct"] = s["truth_team"] == s["pred_team"]
    s["invented"] = [q not in P.PRODUCT_QUEUES.get(pr, []) and q != "ERROR"
                     for pr, q in zip(s["Product"], s["pred"])]
    s["evidence_ok"] = [bool(e) and e[:60].lower() in str(t).lower()
                        for e, t in zip(s["evidence"], s["Consumer complaint narrative"])]

    ok = s[s["pred"] != "ERROR"].copy()
    auto = ok[ok["routed"] == "TEAM_QUEUE"]

    # Real product mix, so the headline reflects an actual inbox rather than the sample.
    mix = pd.read_csv(ROOT / "data" / "complaints_dashboard.csv")["Product"].value_counts(normalize=True)
    per_product_acc = ok.groupby("Product")["team_correct"].mean()
    weighted = float((per_product_acc * mix.reindex(per_product_acc.index)).sum()
                     / mix.reindex(per_product_acc.index).sum())

    res = {
        "n_evaluated": int(len(ok)),
        "api_errors": int((s["pred"] == "ERROR").sum()),
        "HEADLINE_team_accuracy_volume_weighted_pct": round(100 * weighted, 1),
        "auto_routed_pct": round(100 * len(auto) / len(ok), 1),
        "exact_label_accuracy_pct": round(100 * ok["correct"].mean(), 1),
        "TEAM_accuracy_pct": round(100 * ok["team_correct"].mean(), 1),
        "TEAM_accuracy_when_auto_routed_pct": round(100 * auto["team_correct"].mean(), 1),
        "exact_accuracy_when_auto_routed_pct": round(100 * auto["correct"].mean(), 1),
        "sent_to_human_pct": round(100 * (1 - len(auto) / len(ok)), 1),
        "invented_queue_pct": round(100 * ok["invented"].mean(), 1),
        "evidence_verbatim_pct": round(100 * ok["evidence_ok"].mean(), 1),
        "mean_tokens_per_complaint": int(ok["tokens"].mean()),
        "per_product": {
            p: {"n": int(len(g)),
                "queues": len(P.PRODUCT_QUEUES.get(p, [])),
                "exact_accuracy_pct": round(100 * g["correct"].mean(), 1),
                "team_accuracy_pct": round(100 * g["team_correct"].mean(), 1),
                "auto_routed_pct": round(100 * g["routed"].eq("TEAM_QUEUE").mean(), 1),
                "team_accuracy_when_auto_routed_pct": (
                    round(100 * g[g["routed"] == "TEAM_QUEUE"]["team_correct"].mean(), 1)
                    if (g["routed"] == "TEAM_QUEUE").any() else None)}
            for p, g in ok.groupby("Product")},
        "model": model,
        "confidence_threshold": P.CONFIDENCE_THRESHOLD,
        "sample_seed": SEED,
    }
    (HERE / f"eval_results_{model}.json").write_text(json.dumps(res, indent=2))
    ok.drop(columns=["Consumer complaint narrative"]).to_csv(HERE / f"eval_predictions_{model}.csv", index=False)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
