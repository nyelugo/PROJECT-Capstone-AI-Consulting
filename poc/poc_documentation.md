# POC Documentation

Author: Ugo Ahukannah
Capstone Round 2 · Proof of concept for **Assist**
Workflow export: [`poc_workflow.json`](poc_workflow.json) · n8n workflow id `NkRpklvLHKgcP3Ol`

> This is the **POC**, not the MVP. It proves a complaint can be classified, checked and
> routed with a reason — inside a low-code tool a client could maintain. The working
> application that came out of it is [`../mvp/`](../mvp/), documented in
> [`../mvp/mvp_documentation.md`](../mvp/mvp_documentation.md).
>
> `poc_workflow.json` and `../n8n/workflow.json` are **generated from one source** by
> `../n8n/build_workflow.py` and are byte-identical. Neither is a copy maintained by hand.

---

## Tools used, and why

| Tool | Role | Why this one |
|---|---|---|
| **n8n** (v2.13.2, cohort-hosted) | Workflow orchestration | Accepted by the brief, and the right shape for the audience: Chleo's team can *see* the flow as boxes and arrows. A Python script would have been faster to write and impossible to show a CEO |
| **OpenAI `gpt-4o-mini`** | Classification and justification | Measured at 1/16.7 the cost of `gpt-4o` for this task with no meaningful quality difference on the five highest-volume issue classes |
| **LangSmith** (EU workspace) | Decision monitoring | Every execution leaves a record with its reason code. This is the evidence for "you can watch it", which is the pitch |
| **Python** | Generating the workflow | The prompt, taxonomy and guard logic live in `classifier/`. The workflow JSON is generated from them, so the POC and the MVP cannot classify differently |

**The workflow is generated, never hand-edited in the n8n UI.** Editing in the browser would
fork the guard logic from `classifier/decide.py`, and the two would disagree without anyone
noticing. Change the Python, rebuild, re-import.

## What the workflow does, node by node

```
  Run demo ─► Sample complaint ─┐                      ┌─► Safe to propose? ─┬─► Propose to handler
                                ├─► Normalise ─► Classify ─► Validate ┤      └─► Send to human review
  Complaint received ───────────┘   complaint   complaint   and route  │
                                                                       └─► Trace to LangSmith   (leaf)
```

| # | Node | In | Out |
|---|---|---|---|
| 1 | **Run demo** (Manual Trigger) | A click | Fires the pinned sample, for demoing without a POST |
| 2 | **Sample complaint** (Set) | The trigger | One pinned complaint, in the same shape the webhook sends |
| 3 | **Complaint received** (Webhook, POST) | `{product, narrative}` | The same shape as (2), so both entry points converge on (4) |
| 4 | **Normalise complaint** (Code) | Raw request | Validated request + `t0` timestamp. **Rejects** an unknown product, text under 20 characters; caps at 6,000. Throws `REJECT_INVALID_INPUT: <reason>` |
| 5 | **Classify complaint** (HTTP → OpenAI) | Product + that product's queues + narrative | `{queue, confidence, evidence}` as JSON |
| 6 | **Validate and route** (Code) | The model's answer | A `decision` with a **reason code**, applying the five guards in declared order |
| 7 | **Safe to propose?** (If) | The decision | Branches on `decision`, not on confidence — the guard already decided |
| 8 | **Propose to handler** (Set) | A clean proposal | Queue, team, confidence and the customer's own quoted sentence |
| 9 | **Send to human review** (Set) | Anything rejected | The reason code, in words a handler can act on |
| 10 | **Trace to LangSmith** (HTTP) | The decision | One monitoring record. **A leaf** |

### Why the trace node is a leaf, and not in line

It was in line first, and that broke the POC. The HTTP node **replaced the payload** with
LangSmith's response, so `Safe to propose?` no longer saw a `decision` field and every
complaint fell down the review branch. Observing changed the observed.

It now hangs off `Validate and route` in parallel, so nothing downstream depends on it.
Monitoring being unavailable cannot alter a routing decision. The same rule is enforced in
the MVP, where `runtime.trace()` returns a bool that nothing reads.

## The AI capability being demonstrated

**Text classification with a generated, verifiable justification, and a calibrated refusal.**

Three things are on show, and the second and third matter more than the first:

1. **It classifies.** Product-conditioned — the CFPB issue taxonomy is product-scoped, so a
   model asked to choose from all 64 issues without the product is not being given a hard
   problem, it is being given an ill-posed one. Conditioning on product took agreement from
   40% to 56.8% on the pinned model (60.5% on `gpt-4o`).
2. **It says why, and the reason is checked.** The model must quote the sentence that drove
   its decision, verbatim. A guard confirms that sentence is really in the complaint. In the
   sample of 60, **four quotations were fabricated** — confidently — and all four were
   caught.
3. **It refuses, and says which refusal this is.** Seven reason codes, not a boolean. Of 60:
   52 proposed cleanly, 4 stopped because the quote was not real, 4 because confidence was
   below 0.70. Nothing was silently wrong.

## What the POC proves, and what it does not

**Proves:**
- The decision is inspectable end to end, by a non-technical person, in a tool they could own
- A guard can catch a fabricated justification before it reaches a handler
- Abstention works, and reports *which* kind of abstention
- Every execution leaves a monitoring record without altering the decision
- Cost is negligible — €0.000121 per complaint, €0.29 a year at this volume

**Does not prove:**
- **Accuracy.** 56.8% is *agreement* with labels a complainant picked from a dropdown, not
  accuracy against expert labels. No accuracy figure for this system exists. Phase 0 creates
  one
- **That it helps.** Handler acceptance in live use is unmeasured. The MVP instruments it;
  the pilot populates it
- **Delivery.** A trace records that the system decided, not that a handler received it
- **Scale.** One complaint at a time, no queue, no retry, no throughput testing
- **The other two use cases.** The POC is triage only. UC-2 and UC-3 exist in the MVP

## Limits versus a production version

| | This POC | Production |
|---|---|---|
| Input | Manual trigger or an open webhook | Case-management system event, authenticated |
| Output | A JSON object in n8n | A routed case, with receipt confirmed back |
| Rejected input | Throws before the trace fan-out, so **it leaves no monitoring record** | Rejections traced too — a malformed request that vanishes is the gap most likely to hide a real integration fault |
| Credentials | Two n8n credentials owned by one person | Service accounts, rotated, least-privilege |
| Data | Public CFPB complaints | Real customer narratives — which is why the transfer work in [`../compliance/gdpr_documentation.md`](../compliance/gdpr_documentation.md) is a Phase 0 gate |
| Failure handling | The model call retries; nothing else does | Dead-letter queue, alerting, an on-call owner |
| Model | Pinned to `gpt-4o-mini` | Same, plus a fallback and an EU-hosted option evaluated on data-protection rather than price |
| Throughput | One at a time | ~2,426 complaints a year is roughly 10 a working day — genuinely small. Scale is not the risk here |

## How to reproduce it

**Rebuild the workflow from source:**

```bash
cd PROJECT-Capstone-AI-Consulting
python n8n/build_workflow.py          # writes n8n/workflow.json AND poc/poc_workflow.json
```

Credential ids are read from `N8N_OPENAI_CREDENTIAL_ID` and `N8N_LANGSMITH_CREDENTIAL_ID`,
falling back to whatever is already in `n8n/workflow.json`. *That fallback exists because a
rebuild without them once replaced two working ids with a placeholder — a failure that would
only have appeared on re-import, as an auth error, on a demo day.*

**Import and run:**

1. In n8n: **Workflows → Import from file → `poc/poc_workflow.json`**.
   Import into a **new** workflow — importing over an existing one appends nodes rather than
   replacing them.
2. Attach two credentials: an OpenAI API key, and a **Header Auth** credential for LangSmith
   with header `x-api-key`.
3. Click **Run demo**. The pinned sample is a checking-account complaint, 1,099 characters.
4. To see the other branch, edit the pinned narrative to something unrelated to the product —
   the guard fires and the case goes to review with a reason code.
5. Check LangSmith project **`capstone-triage-live`** for the trace.

**Use `Run demo`, not the webhook, on the cohort instance.** The `Complaint received` webhook
is the production entry point and is correct in the export, but its **test** URL does not work
on the shared cohort n8n: clicking Execute returns `{"waitingForWebhook": true}` and the canvas
says it is listening, while every POST to the URL n8n itself publishes answers
`404 — webhook "complaint-triage" is not registered`. That was checked from two clients, in
parallel, and with both URL forms. One process accepts the registration and another serves
`/webhook-test/*` without knowing about it, so it is a property of that deployment rather than
of this workflow — the same export runs green end to end from the manual trigger.

**Verify the guard logic without n8n at all:**

```bash
python -m mvp.test_spine     # 32 guard cases, no network, no keys
```

The POC's guards are generated from the same `classifier/decide.py` those tests exercise.

## Demo recording

**Required as a file** by the deliverables page: *"Demo recording (2–5 minutes), end to
end."* It is a separate checkbox from the presentation, so demoing live on the day does not
discharge it.

**Target three minutes.** The deliverable allows 2–5, but pf-05 gives Slide 4 a **2–3 minute**
slot — so a five-minute recording satisfies the file and overruns the talk. Three does both.

pf-05 asks you to *narrate as it runs*, in these three beats:

| Beat | Say | On screen |
|---|---|---|
| **The trigger** | "This is the trigger — a complaint arrives on a known product." | Click **Run demo**; the pinned sample loads |
| **The AI** | "Here it reads the complaint and proposes a queue, and it has to quote the sentence that decided it." | Green ticks moving through **Classify** and **Validate and route** |
| **The output** | "And this is what the handler receives — a team, a confidence, and the customer's own words." | Open **Propose to handler** |

Then the second run, which is the one worth the time: edit the pinned narrative to something
unrelated to the product and run again. It goes to review. **Read the reason code aloud** —
"it didn't fail, it said which check stopped it."

Close on LangSmith: project `capstone-triage-live`, one row per run, reason codes visible.

**pf-05 also asks for three things after the demo.** Say them over the last shot:

1. **Tools, and why** — n8n, because a client's team can read it as boxes and arrows; a
   Python script would have been faster to write and impossible to show a CEO.
2. **What it does and does not prove** — it proves the decision is inspectable and that a
   fabricated quotation gets caught. It does **not** prove accuracy: 56.8% is agreement with
   labels a complainant chose from a dropdown.
3. **What production changes** — the trigger becomes a case-system event rather than a
   button, rejected inputs get traced too, and delivery is confirmed back rather than
   assumed.
