# Use Case Definition

Author: Ugo Ahukannah
Capstone Round 2 · Client: **Chleo**, CEO of a mid-size EU retail bank
Working name of the system: **Assist**

---

## Business problem statement

Every complaint that arrives at the bank is read by a person who decides what it is about
and which team should handle it. The reading is unavoidable and skilled. The categorising
that follows it is repetitive, inconsistent between handlers, and invisible to management
until something goes wrong — and in a regulated firm, "goes wrong" means a missed deadline,
an ombudsman referral, or a redress bill.

Three symptoms of the same underlying problem:

1. **Routing is slow and inconsistent.** Complaints run a median of 1,201 characters (90th
   percentile 3,013) across 64 issue categories. Two handlers reading one complaint
   routinely choose different categories, because neighbouring categories describe the same
   event.
2. **Regulatory reporting is written by hand from spreadsheets**, under time pressure, by
   the people least able to spare the time — and every figure in it has to be right.
3. **Unusual transaction patterns surface as complaints rather than as alerts.** Fraud and
   unauthorised-transaction complaints are 7.4% of the reference corpus. By the time they
   arrive as a complaint, the money has already moved and the customer is already angry.

What makes this persist without AI is not that the work is hard. It is that it is *high
volume, low complexity, and requires reading unstructured text* — the one shape of work a
mid-size firm can neither automate with rules nor afford to staff generously.

The blocker to solving it is not technical. Chleo's stated objection is that **AI is not
transparent**: she will not authorise a system whose decisions she cannot see. Every design
choice below is downstream of that.

## Company profile (industry, size, current state)

| | |
|---|---|
| Industry | Financial services — retail banking (current accounts, cards, personal and vehicle lending) |
| Region | EU, single market, EUR |
| Size | Mid-size: ~250,000 customers, ~450 staff, complaint handling by a shared operations team rather than a dedicated triage desk |
| Current state | Complaints arrive by web form, email and phone note. A handler reads each one, picks a category, and forwards it. Reporting is assembled by hand each quarter. Transaction monitoring is rules-based and tuned for card fraud only |
| Data | No labelled complaint corpus. No expert-assigned categories. Category history exists but was recorded by whoever handled the case |
| AI maturity | None in production. No MLOps, no model governance, no AI policy |

This profile is **assumed**, not measured — Chleo left the dinner before giving details. It
is stated here so every downstream number can be checked against it, and Phase 0 begins by
replacing it with the real thing.

Because no client data exists, all analysis uses the **CFPB Consumer Complaint Database**
(public, US) as a structural stand-in, and **synthetic transaction data** for anomaly work.
The shape transfers — the mix of issues, the language customers use, how cases end. The
volume does not, and no forecast here depends on it.

## Proposed AI solution and system type

**Assist** — one decision spine, three capabilities, a person in every loop.

```
validate the input → the model proposes → guards verify it is grounded → a human confirms
```

| | Capability | AI system type | What it proposes | What it must be grounded in |
|---|---|---|---|---|
| **UC-1** | Complaint triage | Text classification with generated justification (LLM, `gpt-4o-mini`) | A routing queue and the team that owns it | A verbatim quote from the complaint |
| **UC-3** | Reporting assistance | Conditional text generation over computed figures | 3–5 sentences of report prose | Figures computed by the bank's own metrics module |
| **UC-2** | Anomaly flagging | Deterministic statistical detection + LLM explanation | An analyst case note on a raised pattern | The transaction record's own values |

Three properties define the system type more usefully than the model does:

- **It is assist-only.** The output is always a proposal. There is no configuration in which
  it routes, files, blocks or contacts a customer by itself. In UC-2 the model does not even
  choose what to look at — a deterministic detector selects, and the model only explains.
- **Every proposal carries its evidence, and the evidence is checked.** A guard verifies that
  the quote is really in the complaint, that the figure was really computed, that the value
  really matches the record. In the Round 1 sample of 60, this caught four confidently
  fabricated quotations.
- **Every refusal carries a reason code, not prose.** Eleven codes, one vocabulary across all
  three capabilities, shown to the handler and recorded in monitoring. An unexplained "no" is
  a log line, not transparency.

## Key stakeholders and interests

| Stakeholder | What they want | What would make them say no |
|---|---|---|
| **Chleo, CEO** | To see what the AI does, in terms she can repeat to her board | A system she has to take on trust; a vendor answer to "how does it decide?" |
| **Head of Complaint Operations** | Faster routing without more headcount, and no disruption to her team's day | Handlers spending longer correcting the AI than they saved |
| **Compliance Officer / DPO** | A defensible EU AI Act position, a lawful basis, and an audit trail | Automated decisions about customers; personal data leaving the EU; no DPIA |
| **CTO / Head of IT** | Something maintainable by a small team, with no new platform to run | A bespoke ML stack; a model nobody can debug; an opaque vendor dependency |
| **Complaint handlers** | Less repetitive categorising; to stay the decision-maker | Being measured against the AI, or having to justify disagreeing with it |
| **Customers** | Their complaint reaching the right team first time | Any sense that a machine decided their outcome |
| **The regulator / ombudsman** | Evidence the firm can explain and reproduce its decisions | Decisions the firm cannot reconstruct after the fact |

The **decision log** in the MVP exists for the last three rows specifically: it records what
the system proposed *beside what the person actually did about it*. A proposal with no human
action next to it is an incomplete record, not a decision.

## Success criteria (measurable)

Phase-gated on purpose. Criteria 1 and 2 are what greenlight a pilot; 3 to 5 are what
greenlight full deployment.

| # | Criterion | Target | Measured how | Status today |
|---|---|---|---|---|
| 1 | **Expert-label accuracy on triage** | ≥80% team-level agreement with two trained handlers | Phase 0: 300 complaints labelled independently by two handlers, then scored | **Not yet measurable — no expert labels exist** |
| 2 | **Correct abstention** | ≥95% of items the system is unsure about go to a person rather than being guessed | Reason-code distribution in monitoring; `REJECT_LOW_CONFIDENCE` and `REJECT_OUT_OF_TAXONOMY` rates | Measured: guards fire as specified across 32 test cases |
| 3 | **Handler agreement in live use** | ≥75% of proposals accepted unchanged by the handler | The MVP decision log — proposal vs. the human action beside it | Instrumented, not yet populated with real handlers |
| 4 | **Grounding integrity** | **Zero** ungrounded outputs reach a person | Every guard rejection is counted; a fabricated quote, an uncomputed figure or a mismatched value never renders | Measured: 4 fabrications caught in 60 Round 1 cases; guards verified in test |
| 5 | **Reporting time** | ≥50% reduction in hours to first draft of the quarterly complaints report | Timed before/after in the pilot | Not measured — an assumption in the ROI model, explicitly flagged there |

**Criterion 1 is deliberately not claimed today.** The system currently reaches **60.5%
agreement** with the CFPB's labels, and 88.0% self-agreement on repeat runs (exact queue). That is
*agreement, not accuracy*: the CFPB label was chosen by the complainant from a dropdown, not
assigned by an expert. The model is consistent; it disagrees with an untrained label. Phase 0
exists to create the ground truth that turns criterion 1 into a real measurement, and it is
worth buying even if the bank never builds this — it reveals whether the firm's own
categories can be applied consistently by anybody.

## Out-of-scope boundaries

**Excluded from the system, permanently:**

- **Customer-facing conversation.** No chatbot, no generated reply, no customer-visible
  output of any kind. Errors would be unbounded and public, in the bank's voice.
- **Creditworthiness assessment.** Annex III high-risk under the EU AI Act. Months of
  conformity work before a single decision, for a use case Chleo did not ask for.
- **Deciding complaint outcomes.** The system routes and explains; a person resolves.
- **Automated action on a transaction.** No blocking, no freezing, no customer contact. UC-2
  raises a pattern to an analyst and stops.

**Standing guardrail:** *a predicted payout never orders the queue.* Neither triage nor
anomaly ranking may be ordered by expected monetary exposure, because that optimises the
firm's cost rather than the customer's harm. Anomaly candidates rank by departure from each
account's **own** baseline, so a large-but-normal transaction on a wealthy account does not
outrank a small-but-impossible one on a modest account.

**Out of scope for this engagement, but not forever:** integration with the case management
system, real-time transaction streaming, multi-language complaint handling, and any model
training or fine-tuning. All three capabilities use a hosted model with prompt engineering
and deterministic guards — deliberately, because a mid-size firm with no MLOps function
should not own a training pipeline.

## How this evolved from Round 1

**Industry and use case are unchanged.** Round 1 pitched complaint triage for a mid-size EU
financial services firm; nothing in the staff feedback challenged the sector, the client
profile, triage as the lead, or the position that 60.5% is agreement rather than accuracy.
The Round 1 decision is recorded as **KEEP** in [`feedback/round1_decision.md`](feedback/round1_decision.md).

**What changed is scope.** The one substantive recommendation from the staff presentation was
to build all three proposed use cases rather than carrying triage alone into Round 2. That
recommendation is followed literally: UC-2 and UC-3 are no longer "later options", they are
implemented and running in the MVP.

| | Round 1 | Round 2 |
|---|---|---|
| Use cases proposed | 3 | 3 (unchanged) |
| Use cases **built** | 1 (triage) | **3, on one shared decision spine** |
| POC | n8n workflow, triage only | Same workflow, plus a working application |
| Anomaly data | none — the reason UC-2 was deferred | Synthetic transaction batch, anomalies planted with labels so the detector can be scored |
| Guard vocabulary | 7 reason codes, triage-specific | 11 codes, one vocabulary across three capabilities; the Round 1 seven unchanged so monitoring data stays comparable |
| Human step | implied by the routing branch | explicit — every proposal ends at a button, and the click is recorded |

**How the widening was kept safe.** The brief is emphatic that a small MVP that runs beats an
ambitious one that does not. Rather than three applications, there is one control structure
with three thin capabilities on top: the input contract, guard order, reason codes, error
handling and trace record are written once. Triage — the capability that already ran — was
hardened and verified first, before either new one was started. Adding a capability costs a
prompt and a grounding rule, not a new system.

**What did not change, and was not asked to:** the two refusals (chatbot, credit scoring) and
the payout guardrail. The room recommended building the three proposed use cases, not
revisiting the two refused ones.
