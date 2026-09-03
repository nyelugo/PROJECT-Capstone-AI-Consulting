# The Stack — what each element does

Author: Ugo Ahukannah
Capstone Rounds 1 and 2 · a high-level map, not a code tour

There are ten moving parts. Each answers one question, and the questions are different.
Where two of them look similar in a UI, this document says why they are not.

**Round 2 added three of the ten** — the MVP and its synthetic transaction batch — and the
scope widened from one use case to three. Everything Round 1 built is unchanged and still
read by the newer parts rather than copied into them.

---

## At a glance

| Element | What it is | The question it answers | What it is **not** |
|---|---|---|---|
| **Data** | 16,839 curated public CFPB complaints | What does a complaint book look like? | Not the client's data. A structural proxy |
| **Dashboard** | Streamlit + Plotly, 6 metrics. Runs standalone | Can a CEO see her own problem? | Not an AI product, and not part of the product either — a pitch artifact on public data, shown from the deck |
| **Classifier** | Prompt, taxonomy, team map, decision rules | Given one complaint, which team? | Not a service. It is the logic two runtimes share |
| **n8n workflow** | 10 nodes on the cohort instance | Can she watch a decision happen? | Not production. Assist-only, a person decides |
| **LangSmith experiment** | 60 examples with reference answers | How good is it? | Cannot judge a live complaint — no answer key exists yet |
| **LangSmith tracing** | One record per real execution | What did it just do, and why? | Cannot score anything. No ground truth at run time |
| **Cost / ROI model** | Python, every figure derived | What would this cost, what does it return, and what must be true? | Not a quote. An order of magnitude with stated assumptions |
| **MVP (`mvp/`)** | One Streamlit app, five pages: Overview for both supervisors, three capabilities on one decision spine, and the decision log | Can a person actually use it, and is the human step real? | Not production. No case-system integration, and decisions persist to one machine rather than to a case system |
| **Demo recorder (`demo/`)** | A cue list, TTS and a driven browser | Can the demos be re-made after a UI change? | Not a product feature. Tooling, and the recordings are the deliverable |
| **Synthetic transactions** | 2,069 records, anomalies planted with labels | Does the anomaly detector find what it should? | Not real data, and not proof against a pattern nobody planted |

---

## How a complaint moves through

```
complaint ─► Dashboard        aggregates it into the business picture (offline, no AI)
          │
          ├─► n8n workflow    THE POC — can she watch a decision happen?
          │      1. validate the input      reject unknown product / short text, before spending
          │      2. classify                one OpenAI call, product-scoped queue list
          │      3. check the answer        4 guards: shape, queue valid, confident, quote real
          │      4. fan out ──┬─ route      propose to a handler, or send to human review
          │                   └─ trace      one record to LangSmith, off the critical path
          │
          └─► MVP             THE PRODUCT — the same decision, plus the human step made real
                 1. validate       same contract
                 2. propose        same prompt, read from classifier/ rather than copied
                 3. guard          6 stages, 11 reason codes, the ladder shown on screen
                 4. A PERSON       accept or override — and the click is recorded beside
                                   what was proposed. That pairing is the audit record
```

Nothing is routed by the machine. Every branch, in both runtimes, ends at a person.

**The MVP runs three capabilities through that one spine.** Triage grounds its proposal in a
verbatim quote, reporting in a figure `dashboard/metrics.py` computed, anomaly flagging in
the transaction record's own values. The control structure is identical; only the definition
of "grounded" changes. That is why the second and third capabilities cost a prompt and a
check rather than a new system.

---

## The two LangSmith artifacts, and why both exist

They sit in different places in the UI for a reason.

| | Experiment `triage-round1-ebb7facb` | Tracing `capstone-triage-live` |
|---|---|---|
| Found under | Datasets & Experiments | Tracing → charted in Monitoring |
| Has reference answers | Yes — that is the point | No |
| Output | Scores: 63.3% team agreement, 93.1% verbatim (n=60) | A record: decision, reason code, quote, latency |
| Rhythm | Batch, repeatable, offline | Continuous, one per execution |
| Answers | *Is version B better than version A?* | *Why was THIS complaint routed here?* |

**The dividing line is ground truth.** An experiment can score because each example carries
a known answer. A live trace cannot — when a real complaint arrives nobody yet knows the
right team. That is not a gap to close; it is what "live" means.

Neither replaces the other. The 4-in-60 fabrication *rate* needs the batch — one execution
cannot produce a rate. Catching the fabrication in a *particular* complaint needs the trace.

---

## What keeps the pieces honest

**One definition, two runtimes.** The n8n workflow is generated by `n8n/build_workflow.py`
from `classifier/prompt.py` and `classifier/decide.py`. The prompt running in the demo is
byte-for-byte the prompt that was measured, and the reason codes are the same vocabulary in
both. Edit the workflow in the n8n UI and that link breaks — change the source and rebuild.

**One source per number.** `dashboard/metrics.py` and `cost_estimation/cost_model.py` are
the only places figures are computed. The documents and the deck read from them, so a
number cannot say one thing on a slide and another in a file.
`evidence_walkthrough.ipynb` re-derives all of it and reconciles against what the deck
states — currently 0 mismatches.

**Telemetry cannot break the system.** Tracing is a leaf on a parallel branch with
`onError: continueRegularOutput`. This was demonstrated by accident: while the LangSmith
credential was wrong, the tracing call returned 403 and then 422, and every complaint was
still routed correctly.

---

## Where things run

| | Where | Notes |
|---|---|---|
| Dashboard | Your machine, `localhost:8501` | Desktop launcher; no network, no keys |
| n8n workflow | Ironhack cohort instance | Credentials `Ugo_OpenAI`, `Ugo_LangSmith` |
| Model calls | OpenAI API | `gpt-4o-mini`, temperature 0 |
| Traces and experiments | LangSmith **EU** workspace | A key from EU 403s against the US endpoint |
| Everything else | This repository | Reproducible from committed files |

---

## The honest limits

* The data is a **proxy**. Shape transfers — issue mix, language, the cost ratio. Volume
  does not. Phase 0 measures the real thing.
* 56.8% is **agreement, not accuracy**. The labels were chosen by complainants, not
  experts. No accuracy figure exists for this system yet.
* The trace records **the decision, not the delivery**. Today the handler step is a Set
  node so nothing can fail; once it writes to a case system, a successful trace will no
  longer prove a human received the proposal.
* **Rejected input is not traced.** Validation throws before the fan-out, so a malformed
  request leaves no monitoring record — the one case where "why did nothing happen?"
  is most likely to be asked.

The last two are Phase 1 work, not defects to hide.
