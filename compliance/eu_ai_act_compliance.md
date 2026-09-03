# EU AI Act Compliance Assessment

Author: Ugo Ahukannah
Capstone Round 2 · System: **Assist** — complaint triage, reporting assistance, anomaly flagging
Client: **Chleo**, mid-size EU retail bank
Instrument: **Regulation (EU) 2024/1689** (the AI Act)

> Round 1 deliberately gave no tier label. It said: *"This is not a tier classification and
> not a legal opinion — Round 2 owes the validation."* This document is that validation.
>
> **It is still not legal advice.** It is the reasoning a consultant owes a client so that
> counsel can check it in an hour instead of starting from nothing. Points requiring legal
> confirmation are marked **[verify]** and listed together at the end.

---

## 1. Where the Act stands today

| Milestone | Date | Relevant here |
|---|---|---|
| Entry into force | 1 Aug 2024 | — |
| Prohibited practices (Art. 5) + **AI literacy (Art. 4)** | 2 Feb 2025 | **In force. Art. 4 applies to this system regardless of its risk class** |
| GPAI obligations | 2 Aug 2025 | Falls on the model provider, not the bank |
| **Annex III high-risk obligations** | 2 Aug 2026 | **In force now.** A wrong classification is a live exposure, not a future one |
| Annex I product high-risk | 2 Aug 2027 | Not applicable |

The date matters to the recommendation: if this system were high-risk, the obligations
would already apply. There is no grace period left to classify into.

## 2. Roles — who the bank actually is under the Act

This is settled before classification because the obligations differ by role, and getting
it wrong is a more common failure than getting the tier wrong.

| Role | Who | Why |
|---|---|---|
| **Provider** (Art. 3(3)) | **The bank** | The system is developed for the bank and put into service **under its own name, for its own use**. Building it in-house or via a consultant does not make the consultant the provider — the bank places it into service |
| **Deployer** (Art. 3(4)) | **The bank** | It uses the system under its own authority |
| **GPAI provider** | OpenAI | Chapter V obligations sit with them. The bank inherits none of them, but does depend on their compliance |
| Consultant | Neither | Delivers the build; does not place the system on the market or into service |

**Consequence:** the bank carries *both* provider and deployer duties. Most banks assume
they are only a deployer because they did not train a model. That is wrong here, and it is
the single most useful sentence in this document.

**Art. 25 warning.** A deployer becomes a provider if it puts its name on a system, makes a
**substantial modification**, or **changes the intended purpose**. Switching this system
from proposing to acting would be a change of intended purpose. That is recorded here so it
cannot happen as a quiet product decision.

---

## 3. Classification, step by step

Applied to each capability separately, because they are three intended purposes even though
they share one codebase. Sharing a spine is an engineering fact; the Act classifies by
**intended purpose**, not by architecture.

### Step 1 — Is it an AI system at all? (Art. 3(1))

**Yes, for all three.** Each is a machine-based system that infers from input how to
generate an output (a classification, a text, an explanation) that influences a decision.

Note for UC-2: the **detector** is deterministic arithmetic — a threshold rule, not an AI
system on its own. The **explainer** is. Both are assessed as one system because they are
placed into service together and the analyst sees them as one output. Assessing only the
LLM part would be a technicality, and the wrong instinct.

### Step 2 — Is it a prohibited practice? (Art. 5)

**No, for all three.** Working through the list rather than asserting it:

| Art. 5 practice | Applies? |
|---|---|
| Subliminal / manipulative techniques distorting behaviour | No — no customer-facing surface at all |
| Exploiting vulnerabilities (age, disability, social/economic situation) | No — no customer interaction, no targeting |
| **Social scoring** — evaluating persons over time on social behaviour leading to detrimental treatment in unrelated contexts | **No, and worth stating why.** UC-2 evaluates transaction behaviour, but only against the account's own baseline, only for the purpose the data was collected for, and it never produces a persistent score attached to a person |
| Predicting criminal offending based on profiling / personality | **The closest call.** UC-2 raises unusual patterns for review. It does **not** assess the likelihood of a person committing an offence; it flags a transaction pattern for a human to look at, and it makes no assertion about the person. **[verify]** |
| Untargeted facial-image scraping; emotion inference at work; biometric categorisation; real-time remote biometric ID | No — no biometric data of any kind |

### Step 3 — High-risk under Art. 6(1)? (safety component of an Annex I product)

**No.** Not a safety component of a regulated product (machinery, medical devices, lifts,
toys, vehicles). No Annex I sector applies to a complaints tool.

### Step 4 — High-risk under Art. 6(2)? (an Annex III use case)

Each of the eight Annex III areas, against each capability:

| Annex III area | UC-1 Triage | UC-3 Reporting | UC-2 Anomaly |
|---|---|---|---|
| 1. Biometrics | No | No | No |
| 2. Critical infrastructure | No | No | No |
| 3. Education and vocational training | No | No | No |
| 4. Employment, worker management | No | No | **No — but see below** |
| 5(a). Essential **public** services and benefits | No | No | No |
| **5(b). Creditworthiness / credit scoring of natural persons** | **No** | **No** | **No** |
| 5(c). Risk assessment and pricing in life and health insurance | No | No | No |
| 5(d). Emergency call triage / dispatch | No | No | No |
| 6. Law enforcement | No | No | **No — but see below** |
| 7. Migration, asylum, border control | No | No | No |
| 8. Administration of justice and democratic processes | No | No | No |

**The three that need reasoning, not a "no":**

**5(b) creditworthiness — the one everybody expects to catch a bank.** It covers systems
"intended to be used to evaluate the creditworthiness of natural persons or establish their
credit score". None of the three does. Triage decides *which team reads a complaint*.
Reporting summarises figures already computed. Anomaly flagging raises a transaction pattern
for review. **None evaluates a customer's credit, access to a financial product, or terms.**
This is why creditworthiness scoring is a permanent exclusion in
[`../use_case_definition.md`](../use_case_definition.md) — not because it is hard, but
because it would move the entire system into a class with conformity assessment, registration
and a fundamental-rights impact assessment before a single decision.

**5(a) essential services.** Applies to *public* assistance benefits and services. A private
bank's complaint handling is not that. **[verify]** — the boundary between "essential private
services" and public ones is the kind of thing counsel should confirm rather than a
consultant.

**Fraud detection (UC-2).** Recital 58 addresses AI used to detect fraud in the offering of
financial services, indicating it should not be treated as high-risk in that context. UC-2
is closer to internal transaction monitoring than to a credit decision, and it produces no
customer-facing consequence. **[verify]** — the exact scope of that recital, and whether
national AML/CTF supervisory expectations impose their own requirements independently of the
AI Act, both need legal input. AML obligations are a separate regime and are **not**
displaced by a "not high-risk" AI Act conclusion.

**Employment (4).** Named because it is a live trap rather than because it applies today.
The decision log records, per handler, how often they accept the system's proposal. **If
that data were ever used to evaluate, promote or manage a handler, the system would enter
Annex III(4) and become high-risk.** It is used for calibration, not performance management,
and that restriction is written into [`gdpr_documentation.md`](gdpr_documentation.md) as a
purpose limitation rather than left to custom.

### Step 5 — The Art. 6(3) derogation

Not reached, because Step 4 found no Annex III use. Recorded anyway because it is the
fallback if **[verify]** goes the other way: Art. 6(3) exempts a system that performs a
narrow procedural task, improves a previously completed human activity, detects patterns
without replacing human assessment, or performs a preparatory task — **unless it performs
profiling of natural persons**, in which case it is always high-risk.

**UC-1 and UC-3 would plausibly fall inside the derogation** (narrow procedural task /
preparatory task). **UC-2 would not**, because analysing an individual's transaction
behaviour is profiling. So if the fraud-detection reasoning above fails, **UC-2 becomes
high-risk and UC-1 and UC-3 do not.** That asymmetry is the reason UC-2 is built last and
can be switched off without touching the other two.

### Step 6 — Transparency obligations (Art. 50)

| Provision | Applies? |
|---|---|
| 50(1) — systems interacting directly with natural persons must disclose they are AI | **No.** No customer-facing surface. The users are the bank's own staff, who are told plainly |
| 50(2) — synthetic content must be machine-readably marked | **UC-3 generates text.** It is internal draft material reviewed and signed by a person, not published synthetic content. **[verify]**, and mitigated regardless: every draft is watermarked in the decision log as machine-drafted and human-accepted |
| 50(3) — emotion recognition / biometric categorisation disclosure | No |
| 50(4) — deep fakes; text published to inform the public on matters of public interest | **No** for the deep-fake limb. For the text limb: a regulatory return is not "published to inform the public", and it carries a human signature. **[verify]** |

### Step 7 — Obligations that apply whatever the tier

**Art. 4 — AI literacy.** In force since 2 Feb 2025 and **applies to this system today.**
Providers and deployers must ensure a sufficient level of AI literacy among staff operating
the system. This is the one concrete AI Act obligation the bank has right now, and it is
funded in Phase 2 (handler and analyst training) rather than assumed.

---

## 4. Conclusion and the requirements that follow

| Capability | Classification | Confidence |
|---|---|---|
| **UC-1 — Complaint triage** | Not high-risk. Minimal-risk with voluntary transparency measures | High |
| **UC-3 — Reporting assistance** | Not high-risk. Art. 50(2) marking treated as applicable in practice | High on tier, medium on Art. 50(2) |
| **UC-2 — Anomaly flagging** | Not high-risk on the fraud-detection reasoning; **would be high-risk if that reasoning fails**, because it profiles | **Medium — this is the open question** |

**The honest headline: minimal risk, and the reason matters more than the label.** What
holds all three out of the high-risk tier is not a clever argument — it is a design
property. *The system proposes; a person decides.* Every capability ends at a human, and
`decision` has exactly two possible values in code. Remove that and the classification
changes.

### Mandatory requirements summary

Nothing in Chapter III Section 2 (Arts. 8–15) is mandatory on this classification. What
follows is therefore split into what the Act **requires**, and what the bank should do
anyway.

| Requirement | Source | Status |
|---|---|---|
| **AI literacy of staff operating the system** | **Art. 4 — mandatory now** | Funded in Phase 2. Handlers and analysts trained on what the system does, what its reason codes mean, and that they are the decision-maker |
| No prohibited practices | Art. 5 — mandatory | Assessed above; none apply |
| Transparency where content is machine-generated | Art. 50(2) — **[verify]** | Applied voluntarily: every UC-3 draft is marked machine-drafted / human-accepted in the decision log |
| Risk management, data governance, technical documentation, logging, human oversight, accuracy and robustness | Arts. 9–15 — **not mandatory here** | **Substantially implemented anyway.** See the conformity summary below |
| GDPR compliance | Regulation (EU) 2016/679 — mandatory, independent of any AI Act tier | [`gdpr_documentation.md`](gdpr_documentation.md) |
| AML/CTF supervisory expectations for transaction monitoring | National regime — mandatory, independent | **Out of scope of this assessment.** Named so it is not mistaken for covered |

---

## 5. Conformity Assessment Summary

*No conformity assessment is legally required on this classification.* This is a **voluntary
self-assessment against the Annex III high-risk requirements** (Arts. 9–15), for one reason:
if any **[verify]** point resolves against us — most plausibly UC-2 — the bank needs to know
its distance from compliance in days, not months. It is also the evidence Art. 95 voluntary
codes of conduct contemplate.

**Scope:** Assist v1, three capabilities, as built in `mvp/` and `poc/`.
**Method:** documentary review against Arts. 9–15, plus inspection of the running system.
**Date:** 2026-08-31. **Assessor:** Ugo Ahukannah (self-assessment; not a notified body).

| Art. | Requirement | Assessment | Gap |
|---|---|---|---|
| **9** | Risk management system across the lifecycle | **Partial.** 12 risks identified, scored and mitigated in [`../roi_risk_assessment.md`](../roi_risk_assessment.md), reviewed quarterly under the funded oversight line | No formal iterative risk-management *procedure* document. Phase 1 |
| **10** | Data governance — relevant, representative, error-free training/validation data | **Partial, and honestly weak.** No training occurs — a hosted model with prompts and deterministic guards. But the *evaluation* data is a US public corpus and synthetic transactions, neither representative of this bank | **The main gap.** Phase 0 expert labelling and a real transaction feed close it. Until then no accuracy claim is made |
| **11** | Technical documentation (Annex IV) | **Partial.** Outline complete (§6), content substantially exists across the repo | Not assembled into one Annex IV-shaped document. Phase 1 |
| **12** | Automatic logging over the lifetime | **Met.** Every decision is traced with reason code, failed stage, latency, model and pseudonymous reference. Tracing is a leaf that cannot alter the decision | Retention period not yet set — a GDPR decision as much as an AI Act one |
| **13** | Transparency and information for deployers | **Met.** `mvp/mvp_documentation.md` states capabilities, limits, the guard ladder and ten known limitations. The UI shows the reasoning per decision, not just the outcome | — |
| **14** | Human oversight — able to understand, monitor, override, and not over-rely | **Met, and the strongest area.** Nothing acts autonomously; every proposal ends at a button; the reason code and confidence are shown *before* the action; overrides are recorded beside proposals | Automation bias (R2) is a real residual. Acceptance rate is monitored per handler and a rate near 100% is treated as a warning |
| **15** | Accuracy, robustness, cybersecurity | **Partial.** Robustness is good: 32 guard cases, no unhandled exception path, graceful degradation when the model or monitoring is unavailable. **Accuracy is explicitly not established** — 56.8% is agreement with complainant-chosen labels (gpt-4o-mini) | Accuracy metric requires Phase 0. Penetration testing and secrets rotation are Phase 2 |

**Conclusion.** On the current classification the system requires no conformity assessment.
Measured voluntarily against high-risk requirements it is **substantially conformant on
oversight, logging and transparency (Arts. 12–14)** and **materially short on data
governance and accuracy (Arts. 10, 15)** — both for the same underlying reason: *no
representative client data and no expert labels exist yet.* Phase 0 is the remedy, which is
why it is the first thing the engagement buys.

**Residual risk accepted:** UC-2's classification rests on the fraud-detection reasoning at
**[verify-3]**. If that fails, UC-2 alone becomes high-risk, and the gaps at Arts. 10 and 15
become mandatory rather than voluntary. UC-2 can be disabled independently without affecting
UC-1 or UC-3 — a deployment control, not just a technical one.

---

## 6. Technical Documentation Outline (Annex IV skeleton)

Structured to Annex IV so it can be completed rather than redesigned. Each item names where
the content already exists.

**1. General description of the AI system**
 1.1 Intended purpose, provider, date, version — `use_case_definition.md`
 1.2 How the system interacts with hardware/software it is not part of — `STACK.md`
 1.3 Versions of relevant software; forms of distribution — `requirements.txt`, repo tags
 1.4 Description of hardware on which it runs — *to write*
 1.5 Where a product component: photographs/illustrations — n/a
 1.6 Instructions for use for the deployer — `mvp/mvp_documentation.md`

**2. Detailed description of the elements and development process**
 2.1 Methods and steps performed for development — repo history; `n8n/build_workflow.py`
 2.2 Design specifications, general logic, key design choices, rationale — `mvp/spine.py` docstring; `classifier/prompt.py`
 2.3 System architecture; computational resources — `STACK.md`; `mvp/mvp_documentation.md` §How it is built
 2.4 Data requirements — datasheets on training/validation/testing data, provenance, labelling — **partial**; `data_prep.py`, `mvp/synth/make_transactions.py`. *Weakest section; Phase 0*
 2.5 Human oversight measures — `mvp/spine.py`, `mvp/app.py`; Art. 14 row above
 2.6 Predetermined changes and continued compliance — *to write*
 2.7 Validation and testing procedures; metrics; test logs — `mvp/test_spine.py`, `classifier/FINDINGS.md`, `classifier/ambiguity_test.py`
 2.8 Cybersecurity measures — *to write. Phase 2*

**3. Monitoring, functioning and control**
 Capabilities and limitations; expected accuracy and why; foreseeable unintended outcomes; input specifications — `mvp/mvp_documentation.md` §What is measured and §Known limitations

**4. Appropriateness of the performance metrics** — `classifier/FINDINGS.md`; the
agreement-versus-accuracy distinction is the substance of this section

**5. Risk management system (Art. 9)** — `roi_risk_assessment.md` risk matrix

**6. Lifecycle changes** — decision register; repo history

**7. Harmonised standards applied** — none to date; *to review as CEN-CENELEC outputs land*

**8. EU declaration of conformity** — n/a on this classification

**9. Post-market monitoring plan** — LangSmith project `capstone-mvp`; reason-code
distribution and handler acceptance rate as leading indicators; quarterly review funded at
€8,400/year

---

## 7. Points requiring legal confirmation

| # | Question | Why it matters | If it goes the other way |
|---|---|---|---|
| **[verify-1]** | Does UC-2 engage the Art. 5 prohibition on predicting criminal offending? | Prohibition, not a tier — it would mean *do not build* | UC-2 is dropped. UC-1 and UC-3 unaffected |
| **[verify-2]** | Is a private bank's complaint handling within Annex III(5)(a) "essential private services"? | Would make UC-1 high-risk | Art. 6(3) derogation likely applies to UC-1 (narrow procedural / preparatory task, no profiling) |
| **[verify-3]** | Does the Recital 58 fraud-detection reasoning cover UC-2 as built? | **The main open question.** UC-2 profiles, so the Art. 6(3) derogation would not save it | UC-2 becomes high-risk: conformity assessment, registration, FRIA. Disable UC-2 or commit to the full regime |
| **[verify-4]** | Does Art. 50(2) marking apply to internal draft text under UC-3? | Marking obligation | Already applied voluntarily — no change needed |
| **[verify-5]** | Do national AML/CTF supervisory expectations impose requirements on UC-2 independently? | A separate regime the AI Act does not displace | Additional model-risk governance, independent of this assessment |

**Recommendation: put [verify-1] and [verify-3] to counsel during Phase 0, before UC-2 is
built.** Both concern the same capability, both are answerable in a short opinion, and both
are far cheaper to answer before the build than after.
