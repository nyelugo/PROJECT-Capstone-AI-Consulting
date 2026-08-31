# Use Case Proposals — Three, Ranked

Author: Ugo Ahukannah
Capstone Round 1 · Client: "Chleo", CEO of a mid-size EU financial services firm

> **Round 2 update (2026-08-31).** This document is the Round 1 proposal and is kept as
> written. One thing in it is now out of date on purpose: the "Round 2 MVP?" column said
> UC-1 only. After the staff presentation the recommendation was to build all three, and
> all three now run on a shared decision spine. See
> [`../use_case_definition.md`](../use_case_definition.md) and
> [`../feedback/round1_decision.md`](../feedback/round1_decision.md).

---

## Why these three, and why in this order

Chleo's blocker is transparency, so each use case is chosen to answer a different half of
her question:

- **UC-1** answers *"what is the AI?"* — you can watch it read a complaint and say why.
- **UC-2** answers *"can I trust it with something that matters?"* — money, with a human in the loop.
- **UC-3** answers *"what do I get out of it?"* — a document her team already has to produce.

They also escalate in risk deliberately. UC-1 is the safest thing that is still worth
doing. If the pilot on UC-1 fails, nothing expensive has happened.

| | Use case | AI capability | Human role | Preliminary AI Act view | Built in Round 2? |
|---|---|---|---|---|---|
| **UC-1** | Complaint triage and routing | Text classification + reason generation | Decides and resolves | Limited risk | **Yes — the capability that must run** |
| **UC-2** | Transaction anomaly flagging for ops review | Anomaly detection + explanation | Confirms or dismisses every flag | Limited risk, subject to §UC-2 caveat | **Yes — on synthetic transaction data** |
| **UC-3** | Complaint reporting assistance | Summarisation + drafting | Reviews and signs | Minimal risk | **Yes** |

---

## UC-1 — Complaint triage and routing

**Problem.** Every inbound complaint is read by a person who decides which of ~64 issue
categories it belongs to and routes it to the right team. The reading is unavoidable; the
categorising is repetitive. In the reference corpus the median complaint runs 1,201
characters, with the 90th percentile at 3,013 — roughly 200 to 500 words per item, all day.

**Why it fits a mid-size firm specifically.** A large bank has a trained triage desk and
bespoke software. A small firm has few enough complaints to handle ad hoc. A mid-size firm
has the worst of both: enough volume for the task to be a real cost, not enough to justify
a dedicated team or a six-figure platform. This is the size of company where a narrow
classifier pays for itself.

**Why it is tractable.** The top 5 of 64 issue classes account for **46.1%** of all
complaints. The model does not need to be good at 64 things — it needs to be good at five
and honest about the rest. Anything it is unsure about goes to a human, which is where it
was going anyway.

**Proposed solution.** An LLM classifier over the complaint narrative that returns:
a predicted issue class, a confidence score, the sentence in the complaint that drove
the decision, and an explicit `UNSURE` option that routes to a human.

**Success criteria (measurable).**
1. ≥80% top-1 agreement on the five highest-volume issue classes against the corpus's own
   labels on a held-out split. Note this is agreement with consumer-selected labels, not
   accuracy; the accuracy criterion is set in Phase 0 against expert labels.
2. ≥95% of low-confidence items correctly abstain rather than guess — abstention is
   scored as a success, not a failure.

**Out of scope.** Drafting the reply to the customer. Deciding the outcome. Any
customer-facing surface. UC-1 hands a labelled, explained complaint to a person; the
person does the rest.

**Why this leads the Round 2 MVP.** It is the capability that can be built to actually
run, end to end, in the time available — and the rubric is explicit that a small MVP that
runs scores above an ambitious one that does not. It was therefore hardened and verified
*first*, before UC-3 and UC-2 were started, so the requirement was banked before anything
speculative began.

---

## UC-2 — Transaction anomaly flagging for human review

**Problem.** Fraud and unauthorised-transaction complaints are 7.4% of the reference
corpus (810 "Fraud or scam" + 437 "Unauthorized transactions"). Each one is a case where
the firm found out about a problem *after the customer did*. That is the expensive order
of events — the customer is already angry, and in cards the monetary-relief rate is 17.2%.

**Why it fits a mid-size firm.** The firm is large enough to be targeted and small enough
that it probably buys fraud detection as a black box from a vendor, or runs static rules.
A layer that explains *why* a transaction was flagged is directly responsive to Chleo's
complaint that AI is not transparent — including about the vendor system she already has.

**Proposed solution.** Anomaly scoring over transaction features, where every flag carries
a human-readable reason ("unusual merchant category for this customer, 3rd such
transaction within an hour"). A human confirms or dismisses every flag; the system never
blocks a transaction on its own.

**Success criteria.**
1. Flags surface a defined majority of complaint-generating incidents earlier than the
   customer's own complaint would have — measured on a replayed pilot window.
2. Every flag carries a reason a reviewer rates as intelligible, sampled weekly.

**Caveat that must be said out loud.** Keeping a human on every decision is what keeps this
at limited risk. An autonomous blocking system that freezes a customer's account is a
materially different proposition, both legally and in Chleo's boardroom. If the firm ever
wants that, it is a new assessment, not an upgrade.

**Data note.** The CFPB corpus contains complaints *about* fraud, not transaction records.
A Round 1 demo of UC-2 uses synthetic transaction data, which the brief permits, and the
pitch says so rather than implying we have transaction data we do not.

---

## UC-3 — Complaint reporting assistance

**Problem.** The firm already reports on complaint handling — volumes, categories, timeliness,
outcomes — to management and to its regulator. Someone assembles that by hand every cycle.
In the reference corpus the reportable measures are exactly the ones already tracked:
98.0% timely response, 19.7% closed with any relief, 12.7% with monetary relief.

**Why it fits a mid-size firm.** No dedicated regulatory-reporting function; the work lands
on a compliance lead who has other jobs.

**Proposed solution.** Generate the narrative sections of the periodic complaint report
from the same structured data behind the dashboard — trends, notable categories, movements
worth explaining — for a human to check, edit and sign.

**Success criteria.**
1. A reviewer accepts the generated draft with only light editing on a defined majority
   of sections.
2. Every figure in the draft traces to a query a human can re-run — no number appears in
   the text that cannot be checked.

**Why it is ranked third despite being the easiest.** It is the least visible. It produces
a document, not a demonstration, and Chleo's problem is that she cannot *see* what AI does.
It is included because it is the fastest payback of the three and a good pilot companion —
not because it should lead the pitch.

---

## Two exclusions and one guardrail

| Excluded | Why |
|---|---|
| Customer-facing chatbot | Fails in public, in the customer's voice, with unbounded errors. The worst opening move for a nervous client |
| Creditworthiness scoring | Annex III high-risk under the EU AI Act — conformity assessment, registration and a fundamental-rights impact assessment before go-live |

| Guardrail | Why |
|---|---|
| Predicted payout never determines routing priority | Predicting which complaints will cost money is not forbidden — letting that prediction order the queue is. It would create an incentive to treat expensive customers differently |

Naming these in the pitch is intentional. The fastest way to earn a sceptical CEO's trust
is to be the consultant who tells her what not to buy.

---

## Recommended sequence

**Pilot UC-1 alone, for 60 days, on the firm's own complaint data.** Report accuracy
against the Phase 0 expert labels — the first accuracy figure this project will have —
plus abstention rate and per-segment behaviour. If it holds, UC-3 follows almost for free —
it reads the same data. UC-2 is a separate conversation with a separate risk assessment,
and should not be bundled into a first engagement.
