"""Measure the ceiling, not the model.

Team accuracy sits near 60% for both gpt-4o-mini and gpt-4o. Either both models are
weak, or the task itself is ambiguous. This distinguishes the two: run the SAME model
twice over the SAME complaints at temperature 1 and measure how often it agrees with
itself.

Self-agreement is an upper bound on achievable accuracy. If the model cannot reproduce
its own answer, no amount of prompt work will make it reproduce a stranger's.
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
MODEL = "gpt-4o"
N = 100


def load_key() -> str:
    m = re.search(r"^OPENAI_API_KEY=(.+)$",
                  (Path.home() / ".config/ironhack/.env.local").read_text(), re.M)
    return m.group(1).strip().strip('"').strip("'")


def one(client, product, narrative):
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": P.SYSTEM_PROMPT},
                      {"role": "user", "content": P.build_user_message(product, narrative)}],
            response_format={"type": "json_object"}, temperature=1.0)
        return str(json.loads(r.choices[0].message.content).get("queue", "OTHER"))
    except Exception:                                        # noqa: BLE001
        return "ERROR"


def main():
    client = OpenAI(api_key=load_key())
    df = pd.read_csv(ROOT / "data" / "complaints_triage.csv.gz").sample(N, random_state=7)
    pairs = list(zip(df["Product"], df["Consumer complaint narrative"]))

    with ThreadPoolExecutor(max_workers=10) as ex:
        run_a = list(ex.map(lambda t: one(client, t[0], t[1]), pairs))
        run_b = list(ex.map(lambda t: one(client, t[0], t[1]), pairs))

    d = pd.DataFrame({"product": df["Product"].values, "a": run_a, "b": run_b})
    d = d[(d["a"] != "ERROR") & (d["b"] != "ERROR")]
    d["team_a"] = d["a"].map(T.team_for)
    d["team_b"] = d["b"].map(T.team_for)

    res = {
        "model": MODEL, "n": int(len(d)), "temperature": 1.0,
        "self_agreement_exact_queue_pct": round(100 * (d["a"] == d["b"]).mean(), 1),
        "self_agreement_team_pct": round(100 * (d["team_a"] == d["team_b"]).mean(), 1),
    }
    (Path(__file__).parent / "ambiguity_results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    print("\nThis is the ceiling. Accuracy against a stranger's label cannot exceed the "
          "rate at which the task has one defensible answer.")


if __name__ == "__main__":
    main()
