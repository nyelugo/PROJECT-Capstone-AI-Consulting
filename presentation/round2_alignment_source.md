---
title: Assist
subtitle: What works, what does not yet pay, and how to decide with evidence
round: Capstone Round 2
author: Ugo Ahukannah
status: Follow-up alignment source
main_slides: 11
backup_slides: 7
---

# Purpose of this source

This is the canonical source for the follow-up alignment of `presentation.pptx`,
`presentation.pdf`, and the embedded speaker notes after the active deck pass is complete.

The communication job is:

> By the end, Chleo's CEO, Compliance, Technology and Operations panel should be able to
> accept or reject a bounded evidence programme because they understand what Round 1
> established, what has now been built, what the complete analysis revealed, and which
> conditions must be met before deployment.

The presentation is one connected decision story:

1. Round 1 bridge
2. What was built
3. Proof
4. What the analysis revealed
5. What could prevent proceeding
6. How uncertainty is resolved
7. Recommendation

## Alignment rules

- One argument per slide.
- Main deck: one title slide plus ten content slides. Slides 12–18 are backup only.
- The Round 1 problem and initial test case are established context, not a new pitch.
- The final recommendation is this project's consulting conclusion, not an Ironhack-mandated
  answer.
- Visible copy states the claim. Speaker notes carry the connected explanation.
- Speaker notes are direct-read prose: no timing labels, stage directions, “land this”,
  “point at”, or narration of slide furniture.
- Do not walk through the rubric, repository, risk matrix, legal document or architecture
  inventory.
- Demonstrations prove only what is visible. They do not prove accuracy, production readiness
  or client value.
- Retain the 24pt minimum body-text rule from the Round 2 presentation guide.
- Preserve source blocks in the embedded notes for every non-trivial claim.
- The live demos may be replaced by the existing recordings if needed. That contingency is a
  production cue, not spoken narration.

---

## Slide 1 — Assist

**Narrative job:** Open at the level Round 1 earned; establish what Round 2 must decide.

**Takeaway:** The solution is more capable than Round 1 and more commercially conditional.

### On-slide copy

**Assist**

Three capabilities. One controlled decision process.

What works, what does not yet pay, and how to decide with evidence.

### Speaker notes

Round 1 established the direction: an inspectable AI assistant, tested safely before any
deployment. Since then, the scope has widened to all three proposed use cases, the working
MVP has been built, and the business and compliance work has been completed. The result is
more capable than the Round 1 proposal, but the commercial case is more conditional. This is
the evidence behind that conclusion and the recommendation that follows from it.

### Sources

[Sources]
- `presentation/round1_pitch.pptx`, slides 1–6
- `feedback/round1_decision.md`
- `README.md`, Round 2 deliverables and headline findings

### Build notes

- Minimal dark cover.
- No agenda, metric strip or feature list.
- Keep only the title, three-capability line and decision-oriented subtitle.

---

## Slide 2 — Round 1 established the direction; Round 2 changed the evidence

**Narrative job:** Bridge the two rounds without replaying the Round 1 pitch.

**Takeaway:** The client, lead use case and human-decision boundary stayed; the scope and
evidence changed.

### On-slide copy

**Kept**

- Mid-size EU financial services firm
- Complaint triage as the lead use case
- The system proposes; a person decides

**Changed**

- One implemented use case became three
- A POC became a working MVP
- Cost estimates became ROI, risk and compliance assessments

**Decision now**

A staged evidence programme—not deployment.

### Speaker notes

Nothing in the Round 1 feedback challenged the sector, the client profile, complaint triage
as the lead use case, or the human-decision boundary. The decision was KEEP. The substantive
feedback was to implement all three proposed use cases rather than carry only triage into
Round 2. That recommendation has been followed. The question is no longer whether this is a
credible direction. It is what the completed work now supports, and under which conditions
the client should proceed.

### Sources

[Sources]
- `feedback/round1_decision.md`
- `use_case_definition.md`, “How this evolved from Round 1”
- `presentation/round1_pitch.pptx`, slides 2–3

### Build notes

- Use one restrained kept/changed comparison and one decision line.
- Do not repeat the full Round 1 findings, feedback chronology or course process.

---

## Slide 3 — Three jobs share one accountability problem

**Narrative job:** Show why the widened scope is coherent rather than three disconnected
features.

**Takeaway:** The output changes, but each capability needs evidence, controls and a named
human decision.

### On-slide copy

| Complaint triage | Reporting assistance | Anomaly flagging |
|---|---|---|
| Proposes a routing queue | Proposes report narrative | Proposes an explanation of a flag |
| Grounds it in the complaint | Grounds it in computed figures | Grounds it in transaction values |
| A handler decides | A named employee approves | An analyst decides |

**The task changes. The accountability problem does not.**

### Speaker notes

The three capabilities support different jobs, but they have the same accountability
problem. Triage must show the words behind a routing proposal. Reporting must use only
figures the firm actually computed. Anomaly review must explain only values present in the
transaction record. In every case, the system proposes, checks its own evidence and stops
before action. A handler, approver or analyst remains responsible for the decision. That
common shape is what makes the widened scope manageable.

### Sources

[Sources]
- `use_case_definition.md`, proposed solution and system type
- `mvp/mvp_documentation.md`, capabilities and human-decision boundaries
- `feedback/round1_decision.md`, shared-spine rationale

### Build notes

- Three simple columns, not three UI cards.
- Keep each capability to one proposal, one evidence source and one human owner.

---

## Slide 4 — One decision spine controls all three

**Narrative job:** Explain the solution at the level needed by the panel.

**Takeaway:** Safety and accountability are shared infrastructure, not promises repeated in
three products.

### On-slide copy

**Validate input → Model proposes → Guards verify → Human decides**

The guards test:

- Is the proposal in scope?
- Is the system confident enough to propose?
- Does every quote, figure or value exist in the evidence?

**The system never routes, files or blocks anything by itself.**

### Speaker notes

All three capabilities run through one decision spine. The input must meet the contract. The
model may then propose an answer. Deterministic guards check that the answer is in scope,
confident enough to show and grounded in evidence that exists. Only then does a person see
the proposal and decide what to do. A failure and an abstention have different reason codes,
so neither can disappear as “nothing happened”. The shared spine is the control model for
the entire product.

### Sources

[Sources]
- `mvp/mvp_documentation.md`, architecture, six guards and error handling
- `mvp/spine.py`
- `mvp/test_spine.py`

### Build notes

- One horizontal four-step flow.
- Show only the three guard questions, not the complete reason-code inventory.
- Keep the detailed guard ladder in the repository, not the main deck.

---

## Slide 5 — The POC proves the mechanism—not accuracy

**Narrative job:** Demonstrate the narrow proof and state its boundary immediately.

**Takeaway:** The workflow can propose, cite evidence, stop and wait for a person; it cannot
establish client performance.

### On-slide copy

**What the POC proves**

- The workflow runs end to end
- The proposal carries verbatim evidence
- Failed checks stop the output
- The final decision remains human

**What it does not prove**

- Accuracy on the client's cases
- Operational integration
- Business value at this firm's scale

### Speaker notes

The POC processes a complaint, proposes a routing team and quotes the customer's own words
as evidence. If the quote is missing or confidence is too low, it stops and records why. It
never routes the complaint. This proves that the decision mechanism is visible and that
uncertain cases can fail safely. It does not establish accuracy. The public CFPB labels were
selected by complainants rather than expert handlers, so agreement with those labels is not
client performance. The client's own labelled cases must supply that evidence.

### Sources

[Sources]
- `poc/poc_documentation.md`
- `poc/poc_workflow.json`
- `demo/recordings/poc_demo.mp4`
- `classifier/FINDINGS.md`
- CFPB Consumer Complaint Database: https://www.consumerfinance.gov/data-research/consumer-complaints/

### Build notes

- Use one accepted case and one stopped case.
- Keep the live demonstration to the visible decision path; use the existing recording as
  fallback.
- Do not narrate workflow-node names or the complete toolchain.

---

## Slide 6 — The system works; the bespoke economics do not

**Narrative job:** Deliver the finding that changes the recommendation.

**Takeaway:** At the client's current scale, a one-off deployment does not recover its cost
within 36 months.

### On-slide copy

**−31.0%** 36-month ROI

**Month 69** break-even

The bespoke model needs about **3,800 complaints a year**.

The client has about **2,426**.

| Commercial structure | 36-month ROI |
|---|---:|
| Bespoke build; consultant oversight | −31.0% |
| Productised across five firms | +16.9% |
| Productised; oversight brought in-house | +96.6% |

**The technology is unchanged. Who pays for the build changes.**

### Speaker notes

On the central assumptions, a bespoke build for a firm of this size returns minus thirty-one
per cent over three years and breaks even in month sixty-nine. The volume threshold is about
three thousand eight hundred complaints a year; this firm has about two thousand four
hundred. That is a commercial problem, not a technical failure. The same capability becomes
positive when the build is shared across several firms, and stronger again when oversight is
brought in-house. The pilot therefore has to test value before deployment and support a
commercial structure that does not charge one firm for the entire build.

### Sources

[Sources]
- `roi_risk_assessment.md`, headline, ROI, break-even and sensitivity
- `cost_estimation/roi_model.json`
- `strategic_plan.md`, commercialisation model

### Build notes

- One dominant negative result, one scale comparison and one short commercial-structure
  table.
- Do not add every cost line, scenario or sensitivity result to the main slide.

---

## Slide 7 — Three risks decide whether a pilot is defensible

**Narrative job:** Surface the risks that could reverse the recommendation.

**Takeaway:** The most consequential risks concern value, human behaviour and oversight—not
whether the model can generate text.

### On-slide copy

| Risk | L × I | Control |
|---|---:|---|
| The value assumptions fail on real data | 4 × 5 | Measure before committing to deployment |
| Handlers rubber-stamp proposals | 4 × 4 | Acceptance above 97% is a failure signal |
| Oversight costs more than it saves | 3 × 4 | Measure effort during the pilot |

**Fixed phase exits let the client stop before deployment.**

### Speaker notes

The highest risk is that the value assumptions do not survive contact with the client's
data. The pilot is designed to measure that rather than argue it away. The second is
automation bias: handlers may stop reading and simply accept the suggestion. That is why an
acceptance rate above ninety-seven per cent is treated as a warning, not a success. The third
is oversight cost. If three capabilities require more supervision than they save, the case
fails. These risks are operational and measurable, and the client can stop at each phase.

### Sources

[Sources]
- `roi_risk_assessment.md`, risk matrix R1–R3
- `strategic_plan.md`, Phase 1 KPIs and exit gates
- `mvp/mvp_documentation.md`, decision logging and monitoring

### Build notes

- Show only R1–R3.
- Keep the complete 12-risk matrix in `roi_risk_assessment.md`.
- Avoid red/amber/green decoration that implies a resolved status.

---

## Slide 8 — The current design is not high-risk; real-data use still has gates

**Narrative job:** Give the honest legal and data-protection conclusion without reading the
compliance pack.

**Takeaway:** Human decision-making supports the current classification, but GDPR and the
open anomaly question still constrain the pilot.

### On-slide copy

**EU AI Act working conclusion**

- Complaint triage: not high-risk
- Reporting assistance: not high-risk; marking applied in practice
- Anomaly flagging: not high-risk on the current reasoning; counsel must confirm
- AI literacy applies now

**GDPR gate before real client data**

The identifier is pseudonymised. The complaint narrative is still sent in full.

Complete the data-processing agreement, transfer assessment and zero-retention controls
before real-data processing.

### Speaker notes

Under the current intended use, complaint triage and reporting assistance are not classified
as high-risk. Anomaly flagging carries the open question because it profiles transaction
behaviour; counsel must confirm that reasoning before it proceeds. AI literacy applies
regardless of tier. GDPR is the immediate gate. Pseudonymisation protects the reference, not
the complaint narrative, which is sent to the model provider in full. No real-data pilot
should begin until the processing agreement, transfer assessment and zero-retention controls
are complete.

### Sources

[Sources]
- `compliance/eu_ai_act_compliance.md`, classification conclusion and mandatory requirements
- `compliance/gdpr_documentation.md`, data flow, DPIA and transfer assessment
- Regulation (EU) 2024/1689: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
- Regulation (EU) 2016/679: https://eur-lex.europa.eu/eli/reg/2016/679/oj

### Build notes

- One classification summary and one GDPR gate.
- Do not list every Article, conformity-control row, processing activity or data-subject
  right in the main deck.
- Keep the full classification path and data-flow detail in backup.

---

## Slide 9 — The programme earns each next step

**Narrative job:** Convert the risks and legal gates into a staged operating plan.

**Takeaway:** The client buys evidence first and deployment only after explicit gates pass.

### On-slide copy

| Phase | What it buys | Fee | Exit |
|---|---|---:|---|
| 0 — Discovery and expert labels | Ground truth, baselines, legal and transfer closure | €5,600 | Go/no-go on pilot |
| 1 — Configuration and 60-day shadow run | Evidence on the client's process with no action on suggestions | €12,600 | Go/no-go on deployment |
| 2 — Deployment | Integration, training and handover | €14,000 | Only if the pilot and commercial case pass |

**€18,200 reaches the deployment decision.**

Deployment requires:

- ≥80% accuracy against expert labels
- 75–97% handler acceptance
- Zero ungrounded outputs reaching a handler

### Speaker notes

Phase zero creates the ground truth that does not exist today. Two experienced handlers label
three hundred complaints, the current baselines are measured, and the legal and transfer
questions are closed. Phase one configures the three capabilities for the client and runs
them in shadow for sixty days. Staff follow the existing process and nobody acts on an AI
suggestion. Phase two begins only if accuracy reaches eighty per cent, acceptance remains
between seventy-five and ninety-seven per cent, and no ungrounded output reaches a handler.
Eighteen thousand two hundred euros buys the evidence and the deployment decision.

### Sources

[Sources]
- `strategic_plan.md`, phase plan, milestones and KPIs
- `roi_risk_assessment.md`, upfront costs and recommendation
- `use_case_definition.md`, measurable success criteria

### Build notes

- Use one left-to-right phase progression.
- Show only the three hard deployment gates. Keep G4–G7 in backup.
- Do not repeat the risk, compliance or ROI arguments on this slide.

---

## Slide 10 — The MVP makes every proposal accountable

**Narrative job:** Show the operational product that grew from the POC.

**Takeaway:** The MVP connects a proposal, its checks and a named human action in one record.

### On-slide copy

**A queue, not a chatbot**

- Existing work is prioritised by operational deadline
- Every proposal shows its evidence and checks
- Nothing happens until a person acts
- The human action is recorded beside the proposal

**That pairing is the audit record.**

### Speaker notes

The POC showed one complaint moving through a workflow. The MVP begins with the team's actual
unit of work: a queue. It brings the deadline forward, opens the proposal beside its evidence
and shows every check that ran. Nothing has happened at this point. A person must confirm,
override or reject the proposal, and that action is recorded beside what the system suggested.
The result is not merely an AI output. It is an accountable decision record that shows what
the system proposed and what the responsible person did.

### Sources

[Sources]
- `mvp/mvp_documentation.md`, capabilities, UI, decision log and demo brief
- `demo/recordings/mvp_demo.mp4`
- `mvp/app.py`
- `mvp/queue_store.py`

### Build notes

- Demonstrate one queue item from proposal through human action to decision log.
- Use the existing recording if the live app is unavailable.
- Do not tour all six pages or all three capabilities during the main demo.

---

## Slide 11 — Proceed to evidence—not deployment

**Narrative job:** Resolve the opening with one recommendation the client can accept or
reject.

**Takeaway:** Fund the staged evidence programme only under its legal, performance and
commercial conditions.

### On-slide copy

**Recommendation**

Approve Phases 0 and 1 up to **€18,200**.

**Conditions**

- Close the legal and data-transfer gates before real-data processing
- Retain fixed phase exits and the stated pilot thresholds
- Do not fund the **€14,000 deployment phase** unless the evidence and commercial structure
  support it

**The system works. The pilot determines whether it is worth deploying here.**

### Speaker notes

Round 1 established that this direction was worth taking forward. Round 2 shows a working
system, an honest compliance position and a commercial case that does not support immediate
deployment for a firm of this size. My recommendation is therefore bounded: approve the
evidence programme through the shadow pilot, subject to the legal and data-protection gates,
and preserve the right to stop. Do not approve deployment unless the client data clears the
performance thresholds and the commercial structure makes the economics work.

### Sources

[Sources]
- `roi_risk_assessment.md`, recommendation and phase costs
- `strategic_plan.md`, phase exits and deployment gates
- `compliance/gdpr_documentation.md`, blockers to real-data processing

### Build notes

- Dark closing slide.
- One recommendation, three conditions, one final sentence.
- No generic “Thank you”, summary grid or repeated feature list.

---

## Slide 12 — Backup

**Narrative job:** Separate the presented story from evidence used only in questions.

### On-slide copy

**Supporting evidence**

Accuracy · anomaly testing · AI Act · data flows · pilot gates

### Speaker notes

The remaining slides support questions and are not part of the main presentation.

### Sources

[Sources]
- Repository evidence listed on slides 13–18

### Build notes

- Dark divider.
- Do not present unless moving into questions.

---

## Slide 13 — Why 60.5% is not accuracy

**Takeaway:** Public, complainant-selected labels cannot establish expert-routing accuracy.

### On-slide copy

- `gpt-4o`: 60.5% agreement with CFPB-derived team labels
- `gpt-4o-mini`: 56.8% agreement
- Repeated runs were much more consistent than agreement with the public label
- The label was selected by the complainant, not an expert handler

**Phase 0 creates the missing expert-labelled reference set.**

### Speaker notes

The sixty-point-five per cent figure is agreement with a label derived from a consumer's
dropdown selection. It is not expert-routing accuracy. Repeated classifications were more
consistent than agreement with that public label, which indicates a systematic label
mismatch as well as model error. The project therefore makes no accuracy claim. Two trained
handlers independently labelling three hundred client complaints is what creates the first
reference set that can support one.

### Sources

[Sources]
- `classifier/FINDINGS.md`
- `classifier/eval_results_gpt-4o.json`
- `classifier/eval_results_gpt-4o-mini.json`
- CFPB Consumer Complaint Database: https://www.consumerfinance.gov/data-research/consumer-complaints/

---

## Slide 14 — Why 100% anomaly detection is not real-world performance

**Takeaway:** Synthetic test success proves implementation consistency, not effectiveness on
live fraud or transaction data.

### On-slide copy

- The detector's thresholds were used to plant the synthetic anomalies
- The test therefore measures whether the implementation matches its own specification
- It does not establish precision on real client traffic

**Pilot measure:** at least 30% of raised candidates are judged worth investigating.

### Speaker notes

The anomaly detector's perfect synthetic result should not be presented as real-world
performance. The same thresholds used by the detector were used to plant the anomalies, so
the test proves that the implementation agrees with its own specification. It does not prove
precision on live client traffic. The operational measure belongs in the pilot: at least
thirty per cent of raised candidates must be judged worth investigating by the client's
analysts.

### Sources

[Sources]
- `mvp/synth/make_transactions.py`
- `mvp/capabilities/anomaly.py`
- `strategic_plan.md`, Phase 1 KPI G6

---

## Slide 15 — AI Act classification, step by step

**Takeaway:** The classification follows the intended use and human boundary; UC-2 remains
the open question.

### On-slide copy

1. AI system under Article 3(1)
2. No prohibited practice identified under Article 5
3. Not an Annex I safety component
4. UC-1 and UC-3 do not match an Annex III high-risk use
5. UC-2 requires counsel confirmation because it profiles transaction behaviour
6. Article 50 marking is applied to generated reporting text in practice
7. Article 4 AI literacy applies now

### Speaker notes

The classification is tied to the intended use. The system is an AI system, but no prohibited
practice or Annex I safety-component route applies. Complaint triage and reporting assistance
do not match the Annex III creditworthiness use because they neither assess eligibility nor
make the customer decision. Anomaly flagging is the open question because it profiles
transaction behaviour. If that reasoning fails, UC-2 may become high-risk while UC-1 and
UC-3 remain outside that tier. AI literacy applies regardless.

### Sources

[Sources]
- `compliance/eu_ai_act_compliance.md`, classification steps 1–7
- Regulation (EU) 2024/1689: https://eur-lex.europa.eu/eli/reg/2024/1689/oj

---

## Slide 16 — What actually leaves the bank

**Takeaway:** Pseudonymisation removes the direct reference; it does not remove personal data
from the narrative.

### On-slide copy

| Data | Leaves the bank? | Stored in monitoring? |
|---|---|---|
| Complaint identifier | No | No |
| Complaint narrative | Yes, in full | No |
| Quoted evidence | Returned by the model | Yes |
| Pseudonymous reference | Yes | Yes |

**The transfer assessment is the load-bearing control.**

### Speaker notes

The complaint identifier is replaced with a salted pseudonymous reference before the model
call. The narrative itself still leaves the bank in full, and the quoted evidence is stored
in monitoring. That means the data remains personal data and may include information the
customer supplied in free text. The transfer mechanism, processing agreement, impact
assessment and zero-retention configuration are therefore the controls that matter. The
pseudonym alone is not an answer.

### Sources

[Sources]
- `compliance/gdpr_documentation.md`, data flow and third-party transfers
- Regulation (EU) 2016/679: https://eur-lex.europa.eu/eli/reg/2016/679/oj

---

## Slide 17 — What the pilot must prove

**Takeaway:** Missing any of the first three gates stops deployment.

### On-slide copy

| Gate | Threshold |
|---|---:|
| Accuracy against expert labels | ≥80% |
| Handler acceptance | 75–97% |
| Ungrounded outputs reaching a handler | Zero |
| Correct abstention | ≥95% |
| Triage-time reduction | ≥40% |
| Anomaly precision | ≥30% |
| Oversight effort | ≤3 days per quarter |

**If UC-2 fails but the other gates pass, deploy UC-1 and UC-3 without it.**

### Speaker notes

The first three gates determine whether deployment can proceed at all. Accuracy must reach
eighty per cent against the client's expert labels. Acceptance must remain high enough to
show value but below the level that signals rubber-stamping. No ungrounded output may reach a
handler. The remaining measures test abstention, time saved, anomaly usefulness and oversight
cost. Because the capabilities share controls but remain separable, a failed anomaly result
does not require discarding triage and reporting.

### Sources

[Sources]
- `strategic_plan.md`, Phase 1 KPIs G1–G7
- `use_case_definition.md`, success criteria

---

## Slide 18 — Detection is deterministic; explanation is guarded

**Takeaway:** The language model explains an anomaly selected by arithmetic; it does not
decide which transactions are unusual.

### On-slide copy

**Deterministic detector**

- Compares each account with its own baseline
- Selects unusual transactions consistently

**Language model**

- Explains the already-selected candidate
- May cite only values present in that record

**Human analyst decides whether to investigate.**

### Speaker notes

The anomaly capability separates detection from explanation. Deterministic arithmetic
selects transactions that depart from the account's own baseline. The language model does
not choose what is suspicious; it explains an already-selected candidate in language an
analyst can use. A grounding guard checks every cited value against the transaction record,
and the analyst decides whether the case is worth investigating. This keeps the model away
from both the statistical baseline and the operational decision.

### Sources

[Sources]
- `mvp/capabilities/anomaly.py`
- `mvp/mvp_documentation.md`, anomaly capability and guards
- `mvp/test_spine.py`

---

# Noise and bloat removal ledger

The follow-up deck alignment should remove or move out of the main presentation:

- Any fresh explanation of why AI transparency matters; Round 1 established it.
- Any agenda or rubric walkthrough.
- “Three capabilities are running” repeated on more than one slide.
- The full six-guard ladder, reason-code vocabulary or architecture inventory.
- Workflow-node names and toolchain commentary during the POC demo.
- The complete ROI assumptions, sensitivity table or twelve-risk matrix.
- Article-by-article AI Act reasoning and the full GDPR processing register.
- All seven pilot KPIs from the main plan slide; retain only the three hard gates there.
- Tours of all MVP pages or all three capabilities during the main demonstration.
- Repeated explanations that a person remains responsible; establish it on slides 3–4 and
  demonstrate it on slide 10.
- Production instructions inside spoken notes: timing labels, “point at”, “switch to”,
  “land this”, “if time”, or apology prompts.
- Generic closing language, recap grids and “Thank you” slides after the recommendation.

# Follow-up update procedure

When the other agent's deck pass is complete:

1. Re-open the latest `presentation.pptx`; do not assume the current file is still canonical.
2. Compare its 11 main-slide jobs against this source before changing copy.
3. Preserve any strong visual work that serves these jobs; align titles, visible copy and
   embedded notes rather than rebuilding automatically.
4. Keep slide and note claims synchronized with the repository canon and this source.
5. Render and inspect every slide, then run overflow, placeholder, notes and duration checks.
6. Export `presentation.pdf` from the verified PPTX and confirm slide parity.
7. Commit only the approved source, PPTX, PDF and any deliberately changed supporting file.
