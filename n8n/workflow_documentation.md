# Automation POC — Complaint Triage in n8n

Author: Ugo Ahukannah
Capstone Round 1 · Deliverable 4 of 7 · Use case UC-1

---

## What it does

A complaint arrives. The workflow reads it, proposes which team should handle it, quotes
the sentence that drove that decision, and hands both to a human handler. It does not
route anything on its own.

```
Run demo ─┐                                                    ┌─→ Safe to propose? ─┬─→ Propose to handler
          ├─→ Normalise → Classify (OpenAI) → Validate and route                     └─→ Send to human review
Webhook ──┘                                                    └─→ Trace to LangSmith   (leaf)
```

Ten nodes. Two entry points: a **manual trigger** carrying a real complaint from the
corpus for demonstration, and a **webhook** for how it would actually receive complaints
in production.

## Why it is assist-only, and not automatic

This is the design consequence of the measurement in `classifier/FINDINGS.md`, not a
hedge. Against the only labels available, team-level **agreement** is **60.5%**
(gpt-4o, n=240) — agreement, not accuracy. Auto-routing on a number that weak would send
roughly four in ten complaints to the wrong team, silently.

So the workflow proposes and a person confirms. Every branch ends at a human. The value
on offer in Round 1 is a handler who opens a complaint already read, already categorised,
with the reason visible — not a headcount reduction.

## Input is validated before anything is spent

`Normalise complaint` is a Code node, not a field-mapper. It validates what the *caller*
sent before any model call happens — which matters most for the webhook, because that
entry point is untrusted.

| Check | Rejected when |
|---|---|
| `product` is a non-empty string | missing, or not a string |
| `product` exists in the taxonomy | e.g. `"Mortgage"` — a product this system does not handle |
| `narrative` is a non-empty string | missing, or not a string |
| `narrative` is at least 20 characters | too short to classify |
| `narrative` is capped at 6,000 characters | truncated, not rejected |

Failure throws `REJECT_INVALID_INPUT: <reason>` and the execution stops there.

The point is where it stops. Previously an unknown product flowed through, the classifier
was offered only `OTHER`, and the complaint was rejected — **after** paying for an API
call to reach a conclusion that was knowable up front. Verified: with `product` set to
`"Mortgage"`, execution 19402 ran `Run demo → Sample complaint → Normalise complaint` and
halted. `Classify complaint` never executed.

This makes the workflow symmetrical. Five guards check what the model says; five checks
verify what the caller says. Trusting the input while interrogating the output is the
wrong way round.

## Tracing sits beside the decision, never in it

`Validate and route` fans out: the routing decision goes to `Safe to propose?`, and the
same item goes to `Trace to LangSmith`, which POSTs it to the `capstone-triage-live`
tracing project. Nothing reads the trace node's response — it is a leaf.

That shape is deliberate, and it was learned the hard way. Placed inline, the HTTP node
replaced the item payload with the LangSmith response, so the IF downstream lost
`decision` and every complaint fell to human review. **Observing broke the observed.**
On the parallel branch, with `onError: continueRegularOutput`, LangSmith can 403, 422 or
time out and the complaint is still routed correctly — which was demonstrated
accidentally while the credential was being fixed.

Two consequences worth stating in the pitch:

* Running the workflow now produces a LangSmith trace. The system demonstrated and the
  system monitored are the same system.
* Every decision is traced, not only the successes — the node sits before the branch, so
  rejections carry their reason code into monitoring too.

Run ids are 32 hex characters; LangSmith rejects anything else with a 422.

Duration is measured from the input boundary: `Normalise complaint` stamps `t0`, and the
trace uses it as `start_time`. An earlier version sent the same instant for start and end,
so every n8n trace recorded 0.00s and the latency panel was meaningless for exactly the
runs the demo produces. Traces before 2026-08-30 11:51 still show 0.00s; they are not
rewritten.

One reading trap in the LangSmith trace list: the Input and Output columns preview a
single arbitrary key from the record, so the column shows `n8n`, `demo` or `gpt-4o-mini`
as often as it shows the decision. That is a display artifact — open the row for the
full record.

## The validation layer is the interesting part

The `Validate and route` node exists because a language model's answer is a claim, not a
result. Nothing the model says is trusted until it passes four checks:

| Check | Failure routes to a human because |
|---|---|
| Did it return valid JSON? | A malformed response is a broken call, not a low-confidence one |
| Is the queue real **for this product**? | The taxonomy is product-scoped. A credit-card complaint can never be "Managing an account". A model proposing a queue from another product is hallucinating, and hallucination is not a routing decision |
| Is confidence ≥ 0.70? | Below that the model is guessing |
| **Is the evidence quote verbatim in the complaint?** | A fabricated quote is worse than no quote — it manufactures false justification. The node checks the quote actually appears in the text |

Only a complaint passing all four reaches `Propose to handler`. Everything else reaches
`Send to human review` **with the reason stated**, so a handler is told why there was no
proposal rather than receiving silence.

Measured on 240 complaints, the model proposed a non-existent queue 0.0% of the time
(gpt-4o) / 0.4% (gpt-4o-mini), and its evidence quote was genuinely verbatim 99.6% of the
time. The guards rarely fire — which is the point. They are there for when they do.

## Why this fits the use case

Chleo's objection is that AI is not transparent. n8n's execution view is the answer, and
it is why n8n rather than a script: after a run, every node can be opened and the exact
data going in and coming out inspected. She can see the complaint text, the exact prompt
sent, the model's raw reply, each validation check, and the routing decision — as data,
on screen, without reading code.

That is a demonstration of observability, not a claim about it.

## How to run it

**In n8n:** import `workflow.json` into a **new, empty** workflow (importing over an
existing workflow appends a second disconnected copy of every node rather than replacing
it). Set the OpenAI credential on the `Classify complaint` node, then press **Test
workflow**.

**Via webhook**, once activated:

```bash
curl -X POST https://<your-n8n-host>/webhook/complaint-triage \
  -H 'Content-Type: application/json' \
  -d @n8n/sample_complaint.json
```

## The workflow file is generated, not hand-edited

`workflow.json` is produced by `python n8n/build_workflow.py`, which reads the prompt from
`classifier/prompt.py` and the taxonomy from `classifier/taxonomy.json`. The prompt
running in n8n is therefore byte-for-byte the prompt measured in `classifier/evaluate.py`.

Hand-editing the JSON would let the demo quietly drift away from the evidence supporting
it. Change the prompt, re-run the build, re-import.

## What this POC does not prove

- **It does not prove the accuracy is good enough.** It is not. See `FINDINGS.md`: the
  public labels are consumer-selected, so the honest position is that accuracy is
  unestablished until the client provides expert-labelled complaints.
- **It does not handle volume.** One complaint per execution, no batching, no retries, no
  rate-limit handling, no dead-letter queue.
- **It has no persistence.** Nothing is written to a case management system; the proposal
  is the output of a run.
- **It has no authentication on the webhook**, no PII redaction before the text leaves the
  network, and no model-hosting region control. All three are mandatory before real
  complaint data touches it — the GDPR transfer question is a Round 2 deliverable.
- **The 7-team mapping is a reconstruction**, not Chleo's org chart.

## Execution evidence — it was run, not just built

Imported into the cohort's hosted n8n (**v2.13.2**) as a new workflow,
id `NkRpklvLHKgcP3Ol`, using the `Ugo_OpenAI` credential. Both branches were executed and
the results read back from the executions API rather than the editor panel — the n8n UI
displays values it has not necessarily saved.

**Run 1 — proposal path** (execution `16212`, success in 3.6s). Input: a real
checking/savings complaint from the corpus about disputed CashApp charges.

| Field | Value |
|---|---|
| `proposed_queue` | Problem with a lender or other company charging your account |
| `proposed_team` | Disputes and fraud |
| `confidence` | 0.8 |
| `evidence` | "my dispute was denied by CashApp" |
| `evidence_is_verbatim` | true |
| `decision` | PROPOSE_TO_HANDLER — passed all checks |

The proposed queue matches that complaint's actual CFPB label exactly. One correct case is
not an accuracy claim — the agreement measurement is in `classifier/FINDINGS.md` — but it
does show the path works end to end on real text.

**Run 2 — abstention path** (execution `16215`, success). The sample was temporarily
replaced with a deliberately vague complaint ("It was not good and I would like someone to
look at it please") to check the guard actually fires rather than merely existing:

| Field | Value |
|---|---|
| `proposed_queue` | OTHER |
| `proposed_team` | HUMAN_REVIEW |
| `confidence` | 0.5 |
| `decision` | HUMAN_REVIEW |
| `why_no_proposal` | "no queue on this product matches the complaint" |

The handler is told *why* there was no proposal. The original sample was then restored and
verified byte-identical.

Screenshots of both runs are in `screenshots/`.

## Files

| File | Role |
|---|---|
| `workflow.json` | The importable workflow — generated, do not hand-edit |
| `build_workflow.py` | Generates it from the tested prompt and taxonomy |
| `sample_complaint.json` | The real corpus complaint used in the demo, with its CFPB label |
| `screenshots/` | Execution evidence |
