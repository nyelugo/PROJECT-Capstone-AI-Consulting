"""Read the experiment back out of LangSmith and report it honestly.

Two habits this enforces, both learned the hard way on this run:

* **Deduplicate per run before averaging.** The raw feedback table returned 61
  evidence_verbatim rows for 60 runs — two runs carried the score twice and one carried it
  not at all. Averaging the rows would have quietly weighted two complaints double.
* **Report coverage, not just the rate.** "How many runs did this metric actually measure?"
  is a separate signal from the metric. A metric measured on 49 of 60 runs is not the same
  claim as one measured on all 60, and no amount of reading the percentage tells them apart.
"""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "classifier"))
import traced_classifier as TC          # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    meta = json.loads((HERE / "experiment.json").read_text())
    TC.configure_langsmith(meta["dataset"])
    from langsmith import Client
    client = Client()

    runs = list(client.list_runs(project_name=meta["experiment"], is_root=True))
    feedback = list(client.list_feedback(run_ids=[r.id for r in runs]))

    # Reason codes come from the RUN OUTPUTS, not the feedback table. The feedback table is
    # lossy — 3 of 60 runs carried no guard row on this experiment — while every run's own
    # output records its reason_code. Reading the distribution off feedback would have
    # silently dropped three decisions from a total that is supposed to account for all of
    # them. Feedback is for evaluator scores; the run's own output is the record of what it did.
    reason_from_outputs = collections.Counter(
        (r.outputs or {}).get("reason_code", "MISSING_OUTPUT") for r in runs)

    # one score per (run, metric); duplicates collapse, they do not accumulate
    per_run: dict[tuple[str, str], float] = {}
    dupes = collections.Counter()
    guard_by_run: dict[str, str] = {}
    for f in feedback:
        key = (str(f.run_id), f.key)
        if f.score is not None:
            if key in per_run:
                dupes[f.key] += 1
            per_run[key] = f.score
        # Reason codes must be deduplicated per run too. Counting raw rows here once
        # inflated the guard tally to 11 against an export showing 9 — the duplicate
        # feedback rows were being counted as extra rejections.
        if f.key == "guard" and f.comment:
            guard_by_run[str(f.run_id)] = f.comment

    # Measure the join rather than assume it. Both sides carrying a customer_ref proves
    # nothing — they may be different key spaces. This check exists because they were:
    # an already-pseudonymised ref was being re-hashed, producing a valid-looking alias
    # on the output that joined to nothing on the input.
    joined = mismatched = missing = 0
    for r in runs:
        a = (r.inputs or {}).get("customer_ref")
        b = (r.outputs or {}).get("customer_ref")
        if not a or not b:
            missing += 1
        elif a == b:
            joined += 1
        else:
            mismatched += 1

    n = len(runs)
    metrics = {}
    for metric in sorted({k for _, k in per_run}):
        scores = [v for (rid, k), v in per_run.items() if k == metric]
        metrics[metric] = {
            "rate_pct": round(100 * sum(scores) / len(scores), 1),
            "measured_on": len(scores),
            "unmeasured": n - len(scores),
            "coverage_pct": round(100 * len(scores) / n, 1),
        }

    out = {
        "experiment": meta["experiment"], "dataset": meta["dataset"],
        "environment": meta["environment"], "model": meta["model"],
        "prompt_version": meta["prompt_version"], "runs": n,
        "feedback_rows_raw": len(feedback),
        "duplicate_feedback_rows": dict(dupes),
        "metrics": metrics,
        "customer_ref_join": {"joined": joined, "mismatched": mismatched,
                              "missing_one_side": missing,
                              "join_rate_pct": round(100 * joined / len(runs), 1)},
        "reason_code_distribution": dict(reason_from_outputs.most_common()),
        "reason_codes_via_feedback_lossy": dict(collections.Counter(guard_by_run.values()).most_common()),
    }
    (HERE / "experiment_summary.json").write_text(json.dumps(out, indent=2))

    print(f"experiment {meta['experiment']} | {n} runs | env={meta['environment']} "
          f"| model={meta['model']} | prompt {meta['prompt_version']}")
    print(f"raw feedback rows {len(feedback)}; duplicates collapsed: {dict(dupes) or 'none'}")
    verdict = "OK" if joined == n else "BROKEN"
    print(f"customer_ref join: {joined}/{n} joined, {mismatched} mismatched, "
          f"{missing} missing a side  -> {verdict}")
    print()
    for k, v in metrics.items():
        cov = "" if v["unmeasured"] == 0 else f"  [{v['unmeasured']} not measured]"
        print(f"  {k:<18} {v['rate_pct']:>5.1f}%   on {v['measured_on']}/{n} runs{cov}")
    total = sum(reason_from_outputs.values())
    print(f"\n  reason codes, from run outputs ({total}/{n} runs — complete):")
    for k, v in reason_from_outputs.most_common():
        print(f"    {v:>3}  {k}")
    via_fb = sum(collections.Counter(guard_by_run.values()).values())
    if via_fb != n:
        print(f"  (the feedback table would have shown only {via_fb}/{n} — it is lossy; "
              f"run outputs are authoritative)")


if __name__ == "__main__":
    main()
