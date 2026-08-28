# Monitoring Sample — What Is Watched, and What It Showed

Author: Ugo Ahukannah
Capstone Round 1 · Deliverable 5 of 7

---

## The question this answers

Chleo's objection is that AI is not transparent. The dashboard shows her the *business*.
The n8n POC shows her *one decision*. This shows her that **every** decision is recorded,
including the ones where the system deliberately did nothing — and that the record is
honest about what it does not know.

## The experiment

| | |
|---|---|
| Workspace | LangSmith, **EU region** (`https://eu.api.smith.langchain.com`) |
| Dataset | `capstone-complaint-triage` — 60 public CFPB complaints, 10 per product |
| Experiment | `triage-round1-ebb7facb` |
| Model / prompt | `gpt-4o-mini`, prompt version `0ded1e114c89` |
| Environment | `eval` — never `live` |
| Dataset | https://eu.smith.langchain.com/o/bdd29afc-aefb-432d-a118-2ee71dc41429/datasets/074b52a4-d07a-46e6-9b10-7aac69b24c79 |
| Experiment | https://eu.smith.langchain.com/o/bdd29afc-aefb-432d-a118-2ee71dc41429/datasets/074b52a4-d07a-46e6-9b10-7aac69b24c79/compare?selectedSessions=148f16a5-714e-42c0-ac94-c37c61f1ca65 |
| Export | `traces_export.json` (60 decision records), `experiment_summary.json` |
| Screenshots | `screenshots/` |

Reproduce: `python langsmith/run_monitoring_sample.py 60` then
`python langsmith/summarise_experiment.py`.

> **On the links.** They point into a private LangSmith workspace, so an instructor without
> access will get a login wall. That is why the run records are exported to
> `traces_export.json` and the aggregates to `experiment_summary.json`, and why the
> screenshots are committed — the deliverable accepts either, and the export is the one
> that works without credentials.

> **Region note.** A key from an EU workspace authenticates against the default US endpoint
> and then returns 403 on every call, which reads as a bad key rather than a wrong region.
> `configure_langsmith()` sets the endpoint explicitly for that reason.

## Results

| Metric | Rate | Measured on |
|---|---:|---|
| Auto-proposed (reached a handler with a suggestion) | 86.2% | 58 of 60 runs |
| Evidence quote genuinely verbatim | 93.1% | 58 of 60 runs |
| Correct team, where a team was proposed | 63.3% | **49 of 60 runs** |

**Reason codes, from run outputs — complete, 60 of 60:**

| Code | n | What it means |
|---|---:|---|
| `OK_PROPOSED` | 52 | Passed all four guards |
| `REJECT_EVIDENCE_NOT_VERBATIM` | 4 | The model's justification quote was not actually in the complaint |
| `REJECT_LOW_CONFIDENCE` | 4 | Below the 0.70 routing threshold |

Every complaint is accounted for. Nothing vanished into an unexplained bucket.

## Five design decisions, and why each one is load-bearing

### 1. Every rejection carries a code, not prose
`classifier/decide.py` defines the reason vocabulary and the **declared order** the guards
fire in. A complaint failing two guards is always reported under the first, so the
distribution is comparable between runs rather than drifting with phrasing.

That module generates the n8n Code node too (`n8n/build_workflow.py`), so the POC and the
monitoring cannot describe the same rejection differently. The n8n run now emits
`reason_code: OK_PROPOSED` — the same string LangSmith records.

### 2. "Not measured" is not zero
`team_correct` is deliberately `None` when no team was proposed — abstaining is not a
routing error, and scoring it 0 would punish the system for behaving correctly. The
summary therefore reports **63.3% on 49 of 60 runs**, never a bare 63.3%. A rate without
its coverage is a claim you cannot check.

### 3. Environment is part of identity, not a label
Every run carries `environment: eval`. An evaluation result can never be read as
production behaviour, because the two are distinguishable in every record rather than by
remembering which dashboard you are looking at.

### 4. No raw identifiers reach the trace
Complaint ids are replaced with a salted pseudonym **before** the run is created — not
after, because by then the raw value would already have been sent. The CFPB ids are
public, but the production equivalent is a customer reference, so the boundary is built
in from the start.

### 5. Observing cannot affect the observed
`traced_classify()` falls back to plain `classify()` if LangSmith is unreachable or
unconfigured. Telemetry is best-effort. The decision path does not depend on it.

## Three defects this monitoring found — in itself

The point of observability is to catch what tests do not. All three of these passed every
presence check and would have shipped as correct numbers.

### a) A key that existed and did not join
The trace recorded `customer_ref: cx_9fecc0a5a610bad6` on the input and
`cx_7748cc2ad163b705` on the output **for the same complaint**. Both non-empty, both
correctly prefixed, both the right length — and useless, because the evaluation harness
passed an already-pseudonymised reference back in and it was hashed a second time.

*Fix:* `pseudonymise()` is now idempotent, and the join is a **named, measured fact** in
every summary: `customer_ref join: 60/60 joined, 0 mismatched -> OK`. Before/after
screenshots are in `screenshots/`.

### b) Duplicate feedback rows inflating a rejection count
The raw feedback table returned 240 rows for 60 runs, including duplicates. Averaging rows
weighted some complaints twice, and the reason-code tally read 11 rejections against an
export showing 9.

*Fix:* deduplicate per `(run, metric)` before averaging, and report the collapsed
duplicates rather than hiding them.

### c) The feedback table is lossy; run outputs are not
Reason codes read from feedback accounted for only 57 of 60 runs. Read from the runs' own
outputs they account for 60 of 60. A distribution that silently drops three decisions is
worse than no distribution.

*Fix:* reason codes come from run outputs. Feedback is for evaluator scores only, and the
summary says so out loud when the two disagree.

## What this shows Chleo

- **The system can be watched.** Every decision, including every non-decision, has a
  record with the evidence and the rule that produced it.
- **It admits what it does not know.** 8 of 60 complaints were stopped before a
  suggestion was made, each with a stated reason.
- **It catches its own worst failure.** In 4 of 60 cases the model produced a justification
  quote that was not actually in the complaint — a fabricated reason. The guard caught
  every one. This is the single most important number here: a system that explains itself
  convincingly but falsely is more dangerous than one that says nothing.
- **The monitoring is not a rubber stamp.** It found three real defects in this project's
  own instrumentation before any of it reached a client.

## Limits

- 60 complaints is a demonstration, not a baseline. A pilot needs continuous capture.
- `team_correct` is still measured against complainant-selected labels, so it inherits the
  ceiling described in `classifier/FINDINGS.md`. It is reported because it is what exists,
  not because it is trustworthy.
- No alerting, no thresholds, no on-call. Round 1 shows the decisions are observable;
  deciding *what should page someone* is a pilot conversation.
- Complaint text is sent to LangSmith in this sample. That is acceptable for public CFPB
  data and **is not acceptable for real complaints** without addressing retention, region
  and processor terms — a Round 2 GDPR deliverable.
