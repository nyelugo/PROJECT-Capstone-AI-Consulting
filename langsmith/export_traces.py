"""Export the monitored runs as a committable artifact.

The Round 1 brief accepts a link to the experiment or an export. A link needs the reader
to have access to a private workspace; this export does not, and unlike a screenshot it can
be diffed, searched and re-checked.

Narratives are deliberately NOT exported — they are already in data/, and duplicating
complaint text into a second file is how personal data spreads in real systems. Only the
decision record travels.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "classifier"))
import traced_classifier as TC          # noqa: E402

HERE = Path(__file__).resolve().parent
KEEP = ["customer_ref", "environment", "product", "model", "prompt_version",
        "decision", "reason_code", "reason", "proposed_queue", "proposed_team",
        "confidence", "evidence_is_verbatim", "narrative_chars"]


def main() -> None:
    meta = json.loads((HERE / "experiment.json").read_text())
    TC.configure_langsmith(meta["dataset"])
    from langsmith import Client
    client = Client()

    runs = list(client.list_runs(project_name=meta["experiment"], is_root=True))
    fb = {}
    for f in client.list_feedback(run_ids=[r.id for r in runs]):
        if f.score is not None:
            fb.setdefault(str(f.run_id), {})[f.key] = f.score

    records = []
    for r in runs:
        o = r.outputs or {}
        rec = {k: o.get(k) for k in KEEP}
        rec["latency_s"] = round((r.end_time - r.start_time).total_seconds(), 2) if r.end_time else None
        rec["scores"] = fb.get(str(r.id), {})
        records.append(rec)
    records.sort(key=lambda x: (x["reason_code"] or "", x["product"] or ""))

    out = {"experiment": meta["experiment"], "environment": meta["environment"],
           "endpoint": meta["endpoint"], "n": len(records),
           "note": ("Decision records only. Complaint narratives are not duplicated here — "
                    "they live in data/complaints_triage.csv.gz. Customer references are "
                    "salted pseudonyms, generated before the trace was created."),
           "runs": records}
    (HERE / "traces_export.json").write_text(json.dumps(out, indent=2))
    print(f"exported {len(records)} decision records -> langsmith/traces_export.json")
    bad = [r for r in records if r["reason_code"] != "OK_PROPOSED"]
    print(f"of which {len(bad)} were stopped by a guard:")
    for r in bad[:12]:
        print(f"  {r['reason_code']:<30} conf={r['confidence']:<5} {r['product'][:34]}")


if __name__ == "__main__":
    main()
