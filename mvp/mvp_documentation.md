# Assist — MVP documentation

**Capstone Round 2 · working MVP.** Three capabilities, one decision spine, a person in
every loop. Nothing in this application acts on a customer, a case or an account. It
proposes, shows its reasoning, and waits.

---

## Run it

```bash
cd PROJECT-Capstone-AI-Consulting
conda activate bootcamp-env          # or any Python 3.11+ environment
pip install -r requirements.txt
streamlit run mvp/app.py
```

Opens on <http://localhost:8502>. Editing a module under `mvp/` — as opposed to a
page script — needs a server restart, not just a browser refresh. On macOS, double-click **`Assist.app`** on the Desktop
(build it once with `./make_desktop_app.sh`); on Windows, **`run_mvp.bat`**.

**One app, five pages, left-hand navigation.** The Round 1 dashboard is a page inside this
application rather than a second server on a second port — two ports is a seam the audience
sees, and it contradicts the claim that this is one system. `dashboard/app.py` is *reused*,
not copied, and still runs standalone as the Round 1 deliverable it is.

### Keys

One key is required, one is optional.

| Variable | Required | What happens without it |
|---|---|---|
| `OPENAI_API_KEY` | **yes** | The app loads and explains itself, and every capability button is disabled with a message naming the file to fix |
| `LANGSMITH_API_KEY` | no | Everything works; decisions are not sent to monitoring, and the app says so under each result |
| `LANGSMITH_ENDPOINT` | no | Defaults to `https://eu.api.smith.langchain.com` — this workspace is EU-hosted, and a US endpoint returns 403 in a way that reads as a bad key |

Keys are read from `~/.config/ironhack/.env.local` (one shared file for all Ironhack work),
or a repo-local `.env.local`, or the environment — in that order. `.env.example` lists the
names. **No key value is ever printed**: the sidebar shows presence as a length and an
8-character digest, which is enough to tell "wrong key" from "no key" without exposing one.

### Test it without a key or a network

```bash
python -m mvp.test_spine        # 27 guard cases, all three capabilities
```

Exercises every rejection path against a stubbed model. Each case asserts the reason code
**and** the stage that stopped it — a test that only checked "went to a human" would pass
for the wrong reason, and the entire claim of this system is that a refusal says why.

---

## What it does

| Page | Who it is for | What it shows | The action |
|---|---|---|---|
| **Overview** | Chleo, **weekly** | Was this a normal week — this week against last, nine weeks of receipts, what was held and why, agreement, cost, and a switch per capability | Switch a capability off |
| **Operations** | Ops lead, **daily** | What is past target and untouched, outstanding by team, where the model is overridden and **where handlers sent it instead**, acceptance per handler | None — a directing page |
| **Complaint triage** | Handler | A standing queue, already classified. Proposed team, confidence, the sentence that decided it | Accept · reroute · escalate. Tick several for a bulk action |
| **Anomaly review** | Fraud analyst | A standing queue, ranked by departure from each account's own normal. Case note already written | Escalate · dismiss · needs more |
| **Reporting assistance** | Compliance officer | The **whole return**, all sections drafted, every figure checked against what this system computed | Sign off · reject, **per section** |
| **Decision log** | Compliance, audit | One row per human action, in order. Filterable, exportable | None — export it |

**The Round 1 dashboard is deliberately not in here.** It sized an opportunity from public
data for a pitch — a different job, for a different audience, on data that is not the
client's. A page needing a label telling you which part to ignore belongs somewhere else.
It stays at `dashboard/app.py`, runs standalone, and is shown from the deck.

**Queues, not forms.** Nobody types a complaint into a box that already arrived in the case
system. The AI runs over the batch beforehand (`python -m mvp.build_queues`), so a queue
renders instantly, shows the same thing every rehearsal, and does not put sixty live model
calls in front of a panel. Handled items stay visible — an inbox that empties tells you
nothing about what was decided this morning.

**The clock.** Triage carries an age, days-to-target and a deadline state, computed in
`queue_store.clock()` against the batch's own newest item rather than today's date — the
corpus is a fixed historical batch, and measuring against today would show every complaint
as months overdue and make the column meaningless. `SLA_DAYS` is an assumption standing in
for a first-response target, not a regulatory citation; the firm's real target is set in
Phase 0. Anomaly review carries an age but no target: a fraud pattern is not on a
complaints deadline.

**Nothing is rendered under a request it no longer matches.** The reporting page stores its
drafts with the audience that produced them and clears them when that changes. An earlier
version kept the last result and displayed it under whatever the form said now, so the page
could show a draft of one section while the selector read another. A page that silently
shows the wrong thing is worse than one that shows nothing.

**One event log, two views.** Every human action is appended to
`mvp/queues/decision_events.json`. The queues project it — an item's status is simply its
latest event — and the Decision log renders it in full. So an item somebody revisited
appears once in the queue and twice in the log, which is the correct answer to both
questions. Append-only, for the reason the GDPR pack already commits to: a past decision is
a record of what was decided at the time, and editing it away destroys the audit value that
justifies keeping it.

## How it is built

```
validate input → model proposes → guards verify it is grounded → a human confirms
```

Every capability is that shape. `mvp/spine.py` owns the control structure; a capability
supplies only a prompt, a scope rule and a grounding rule. Adding a fourth would not touch
the spine, the error handling, the reason-code vocabulary or the trace record.

```
mvp/
├── spine.py                 the six guards, the reason codes, the Decision record
├── runtime.py               keys, the model client, pseudonymisation, tracing
├── app.py                   entry point — st.navigation, sidebar, system status
├── ui.py                    ONE renderer + the shared queue widgets
├── queue_store.py           the queues, and the append-only event log
├── build_queues.py          precompute both queues (run once, commit the result)
├── app_pages/               overview · triage · anomaly · reporting · decision_log
├── queues/                  triage_queue.json · anomaly_queue.json (committed)
│                            decision_events.json (NOT committed — operator state)
├── test_spine.py            27 guard cases, no network, no keys
├── capabilities/
│   ├── triage.py            UC-1 · reads classifier/prompt.py, unchanged
│   ├── reporting.py         UC-3 · reads dashboard/metrics.py, unchanged
│   └── anomaly.py           UC-2 · deterministic detector + explainer
└── synth/
    ├── make_transactions.py deterministic generator, anomalies planted with labels
    └── transactions.csv     2,069 transactions · 40 accounts · 2026-04-01 to 2026-06-29
```

Triage and reporting import the **Round 1 modules directly**, not a fork. The MVP, the n8n
POC and the Round 1 dashboard therefore cannot disagree about a classification or a figure
— a difference between the demo and the product would make the demo evidence for nothing.

### The six guards, in declared order

Order is part of the contract: a proposal failing two guards is always reported under the
first, so reason-code distributions stay comparable across capabilities and across rounds.

| Stage | Fails as | Meaning |
|---|---|---|
| input | `REJECT_INVALID_INPUT` | The request never met the contract. Costs no tokens |
| call | `ERROR_MODEL_CALL` | The model call itself failed |
| parse | `REJECT_MALFORMED_OUTPUT` | Not valid JSON, or confidence was not a number |
| scope | `REJECT_QUEUE_NOT_IN_PRODUCT`, `REJECT_OUT_OF_TAXONOMY`, `REJECT_METRIC_NOT_PUBLISHED`, `REJECT_ACCOUNT_NOT_IN_LEDGER` | The thing proposed does not exist |
| confidence | `REJECT_LOW_CONFIDENCE` | Below 0.70. Abstention is a correct answer |
| grounding | `REJECT_EVIDENCE_NOT_VERBATIM`, `REJECT_FIGURE_NOT_COMPUTED`, `REJECT_VALUE_MISMATCH` | The proposal cited something that is not there |

Codes carried unchanged from Round 1's `classifier/decide.py` still mean what they meant, so
Round 1 and Round 2 monitoring data are directly comparable.

The UI renders this ladder beside every result, with a tick against each check passed and a
cross against the one that stopped it. That display **is** the answer to Chleo's objection:
not "trust it", but "here is every check, by name, and here is the one it failed".

### Error handling

`spine.run()` never raises. Every exit is a `Decision` carrying a reason code, including a
crash — a capability that failed and a capability that abstained are both observable
outcomes, and they must not look the same in monitoring. "Cannot tell" is not "nothing
happened". Concretely: a missing key, a network failure, a timeout, malformed JSON, a
number where a string was expected, and an unparseable request all resolve to a reason code
and a rendered result, never a stack trace on screen.

### Monitoring

Every decision is sent to LangSmith project `capstone-mvp` with its reason code, failed
stage, capability, latency and pseudonymous reference. Tracing is a **leaf**: it is called
after the `Decision` already exists, it returns a bool, and nothing downstream reads it.
Round 1 wired a trace step inline into the n8n workflow, where it replaced the payload and
broke the routing that followed — observing must not affect the observed. Monitoring being
down cannot stop the system deciding.

### Personal data

The reference attached to every decision and trace is a salted pseudonym (`cx_…`). Raw
complaint references and account identifiers never enter the record — `test_spine.py`
asserts this rather than assuming it. Pseudonymisation is idempotent, because in Round 1
re-hashing an already-hashed reference produced a second valid-looking alias that joined to
nothing, and every presence check passed while the key was useless.

---

## Demo recording (the backup for Slide 9)

pf-05 makes the MVP demo **required** on Slide 9, gives it **1–2 minutes**, and is blunt
about the fallback: *"A live failure with no fallback costs you the easiest points in the
deck."* The rubric's presentation line accepts either — *"MVP demo works or backup recording
used"* — so the recording protects ten points at no cost.

Unlike the POC recording, this one is **not** a deliverable in its own right. It is
insurance.

The brief the guide sets is to **demo the upgrade**: *"Here is what the POC showed was
possible. Here is the beginning of the real product."* So lead with what the workflow could
not do.

| ~Time | Show | Say |
|---|---|---|
| 0:00 | **Complaint triage**, the queue | "The workflow classified one complaint. This is a morning's work, already read." |
| 0:20 | The **deadline** column, sorted | "And that is the column your regulator asks about." |
| 0:35 | Tick a row — the proposal, the quoted sentence | "It proposes a team, and quotes the sentence that decided it." |
| 0:55 | The **Checks** panel | "Every check it ran, by name, and the one it failed." |
| 1:10 | Press **Send to that team** | "Nothing happened until someone pressed that." |
| 1:20 | **Decision log** | "And the press is recorded beside what was proposed. That pairing is the audit record." |
| 1:35 | **Overview** | "Which is what she sees: what it proposed, what her people did, and how often they agreed." |

Record it at 1600×1500 or wider so the queue and the opened item fit one frame without
scrolling — the same window size the slide screenshots were taken at.


## What is measured, and what is not

**Triage.** 60.5% agreement with CFPB labels; 88.0% self-agreement on repeat runs. This is
**agreement, not accuracy** — the CFPB label was chosen by the complainant from a dropdown,
not assigned by an expert. No accuracy figure exists for this system, and Phase 0 (two
handlers labelling 300 complaints) is what would create one. See `classifier/FINDINGS.md`.

**Reporting.** The grounding guard is measured by construction: `test_spine.py` shows an
invented percentage rejected and the real figure accepted, including when rounded. What is
**not** measured is whether the prose is *good* — a draft can be fully grounded and still
emphasise the wrong thing. That is why a compliance officer accepts or rejects every draft.

**Anomaly.** The detector finds 100% of planted anomalies across all four patterns, at 97.1%
precision (56 candidates, 103 transactions flagged, 100 planted). **Do not report this as a
detection rate.** The detector's thresholds and the data generator were written by the same
author, so it measures whether the code agrees with itself — structurally the same trap as
the 60.5%. The caveat is bound to the figure in `score()`'s return value so it cannot be
lifted onto a slide alone. What it does establish: the detector is deterministic, covers all
four patterns rather than only the easy one, and its false-positive rate is measurable.

## Known limitations

1. **The grounding scan reads digits, not words.** "five transactions" is not checked;
   "5 transactions" is. A model writing figures as words could evade the check.
2. **Reporting confidence is weakly calibrated** — observed at 1.00 on live runs where a
   0.85 would have been more honest. The grounding guard, not the confidence, is what
   actually protects this capability.
3. **`/overview` deep-links to a "page not found" dialog.** Streamlit serves the default
   page only at `/`, and the dialog sits over the app swallowing clicks. Reach Overview from
   the sidebar, or link to `/`.
4. **Decisions persist to a local file, not to a case system.** `queues/decision_events.json`
   survives a refresh, a restart and a reboot — but it lives on one machine, and a fresh
   clone starts with an empty log. A production version writes to the case system, which is
   also where receipt would be confirmed.
5. **The trace records the decision, not the delivery.** A successful trace proves the
   system decided, not that a handler received it. Carried over from Round 1, still open.
6. **Anomaly detection runs on a fixed batch**, not a stream. Thresholds are static and
   would need per-portfolio tuning before a pilot.
7. **Rejected input is traced only from the MVP**, not from the n8n POC, where validation
   throws before the trace fan-out.
8. **One model, one temperature.** No fallback if `gpt-4o-mini` is unavailable; the call
   surfaces as `ERROR_MODEL_CALL` and the work goes to a person, which is the correct
   failure but not a resilient one.
9. **Sign-in is a name typed into a box.** It records who *said* they decided, not who did.
   For a page that calls itself an audit record that is a real limit, and it closes with the
   case-system integration in Phase 2, not before.
10. **One fixed batch: no new work arrives.** Week-on-week comparison IS available — the
    batch carries nine ISO weeks of real receipt dates — but the queue never grows, so
    nothing new turns up between visits. That waits on the Phase 2 feed.

## What would be different in production

Case-system integration in place of the session log; per-portfolio detector thresholds;
expert labels from Phase 0 replacing complainant labels as the triage benchmark; a real
transaction feed replacing `synth/`; retention and deletion wired to the GDPR register in
`compliance/gdpr_documentation.md`; and an on-call owner for the monitoring project, which
the cost model already funds as the largest running line.
