"""Create the LangSmith dataset and run the monitored experiment.

Produces the Round 1 monitoring deliverable: a dataset instructors can open, and an
experiment whose every run answers "why did this complaint get this outcome?".

Usage:  python langsmith/run_monitoring_sample.py [n]
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "classifier"))
import decide as D                       # noqa: E402
import prompt as P                       # noqa: E402
import teams as T                        # noqa: E402
import traced_classifier as TC           # noqa: E402

DATASET = "capstone-complaint-triage"
ENVIRONMENT = "eval"          # never "live" — this is a measurement, not production
N_DEFAULT = 60


def build_dataset(client, n: int):
    df = pd.read_csv(ROOT / "data" / "complaints_triage.csv.gz")
    parts = [g.sample(min(n // 6, len(g)), random_state=42)
             for _, g in df.groupby("Product")]
    s = pd.concat(parts).reset_index(drop=True)
    s["truth_queue"] = [r.Issue if r.Issue in P.PRODUCT_QUEUES.get(r.Product, []) else "OTHER"
                        for r in s.itertuples()]
    s["truth_team"] = s["truth_queue"].map(T.team_for)

    if client.has_dataset(dataset_name=DATASET):
        client.delete_dataset(dataset_name=DATASET)
    ds = client.create_dataset(
        dataset_name=DATASET,
        description=("Public CFPB complaints (no personal data; narratives scrubbed by the "
                     "CFPB). Ground truth is the complainant's own issue selection, which is "
                     "why it is a weak yardstick — see classifier/FINDINGS.md."))
    # One dict per example. The older form - parallel inputs=[...] / outputs=[...] lists -
    # falls through to **kwargs, which the SDK labels "Legacy keyword args" and routes to a
    # deprecated endpoint. That is what raises the "Legacy API usage detected" banner in the
    # LangSmith UI. Deadline for the old endpoint is 2027-01-31.
    client.create_examples(
        dataset_id=ds.id,
        examples=[{
            "inputs": {"customer_ref": TC.pseudonymise(r["Complaint ID"]),
                       "product": r["Product"],
                       "narrative": r["Consumer complaint narrative"]},
            "outputs": {"truth_queue": r["truth_queue"], "truth_team": r["truth_team"]},
        } for _, r in s.iterrows()])
    return ds, len(s)


# --- evaluators -------------------------------------------------------------------
# Each returns a fact that is measured, never inferred. "Cannot tell" is expressed by
# returning None rather than 0, so an unmeasured case never renders as a failure.

def team_correct(outputs: dict, reference_outputs: dict) -> dict:
    if outputs.get("decision") != D.PROPOSE:
        return {"key": "team_correct", "score": None,
                "comment": "no team proposed — not a routing error"}
    return {"key": "team_correct",
            "score": int(outputs.get("proposed_team") == reference_outputs.get("truth_team"))}


def evidence_verbatim(outputs: dict) -> dict:
    return {"key": "evidence_verbatim", "score": int(bool(outputs.get("evidence_is_verbatim")))}


def auto_proposed(outputs: dict) -> dict:
    return {"key": "auto_proposed", "score": int(outputs.get("decision") == D.PROPOSE)}


def guard_fired(outputs: dict) -> dict:
    """Which guard stopped this one. The value carries the code, so the reason-code
    distribution is readable straight off the experiment."""
    return {"key": "guard", "score": int(outputs.get("reason_code") == "OK_PROPOSED"),
            "comment": outputs.get("reason_code")}


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_DEFAULT
    if not TC.configure_langsmith(project=DATASET):
        raise SystemExit("LANGSMITH_API_KEY not found in ~/.config/ironhack/.env.local")

    from langsmith import Client, evaluate
    client = Client()

    ds, count = build_dataset(client, n)
    print(f"dataset '{DATASET}': {count} examples")

    def target(inputs: dict) -> dict:
        return TC.classify(inputs["customer_ref"], inputs["product"], inputs["narrative"],
                           environment=ENVIRONMENT)

    res = evaluate(
        target, data=DATASET,
        evaluators=[team_correct, evidence_verbatim, auto_proposed, guard_fired],
        experiment_prefix="triage-round1",
        metadata={"environment": ENVIRONMENT, "model": P.MODEL,
                  "prompt_version": TC.PROMPT_VERSION,
                  "confidence_threshold": P.CONFIDENCE_THRESHOLD},
        max_concurrency=6)

    name = getattr(res, "experiment_name", None)
    print(f"experiment: {name}")
    Path(__file__).parent.joinpath("experiment.json").write_text(json.dumps(
        {"dataset": DATASET, "experiment": name, "n": count,
         "environment": ENVIRONMENT, "model": P.MODEL,
         "prompt_version": TC.PROMPT_VERSION,
         "endpoint": "https://eu.api.smith.langchain.com"}, indent=2))


if __name__ == "__main__":
    main()
