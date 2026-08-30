"""Send a batch of decisions to a plain LangSmith TRACING project.

Why this exists separately from run_monitoring_sample.py:

LangSmith files a session under "Datasets & Experiments" when it has a reference
dataset attached, and under "Tracing" (which is what the Monitoring tab charts) when it
does not. The evaluation runs are the former, so the Monitoring tab was empty — which
reads badly on a slide that says the system is watched.

The evaluation answers "how good is it against the labels we have". This answers
"what is it doing right now", which is what monitoring means in production. Both are
wanted; they are not the same artifact.

Usage:  python langsmith/emit_live_traces.py [n]
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "classifier"))
import traced_classifier as TC          # noqa: E402

PROJECT = "capstone-triage-live"        # no dataset attached -> a tracing project
N_DEFAULT = 20


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_DEFAULT
    if not TC.configure_langsmith(project=PROJECT):
        raise SystemExit("LANGSMITH_API_KEY not found in ~/.config/ironhack/.env.local")

    df = pd.read_csv(ROOT / "data" / "complaints_triage.csv.gz").sample(n, random_state=99)
    print(f"tracing {n} decisions into project '{PROJECT}' (environment=demo)…")

    counts = {}
    for _, r in df.iterrows():
        out = TC.traced_classify(
            r["Complaint ID"], r["Product"], r["Consumer complaint narrative"],
            environment="demo",           # never 'live' - this is a demonstration
        )
        counts[out["reason_code"]] = counts.get(out["reason_code"], 0) + 1

    print("\nreason codes emitted:")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>3}  {k}")
    print(f"\nOpen LangSmith -> Tracing -> {PROJECT}. Monitoring charts this project.")


if __name__ == "__main__":
    main()
