# GDPR Documentation

Author: Ugo Ahukannah
Capstone Round 2 · System: **Assist** — complaint triage, reporting assistance, anomaly flagging
Client: **Chleo**, mid-size EU retail bank
Instrument: **Regulation (EU) 2016/679** (GDPR)

> **GDPR applies regardless of the AI Act tier.** A "not high-risk" conclusion in
> [`eu_ai_act_compliance.md`](eu_ai_act_compliance.md) changes nothing here. Complaint
> narratives are personal data, and the bank is the controller.
>
> Not legal advice. Points needing the DPO or counsel are marked **[verify]**.

---

## 1. The finding that matters most

**Pseudonymisation in this system protects the *reference*, not the *content*.**

Every decision record carries a salted alias (`cx_…`) instead of a complaint or account
identifier. That is real and it is tested. But the complaint **narrative itself is sent to
the model provider in full**, and the verbatim quote the model returns is **stored in the
monitoring record**. A complaint narrative routinely contains a name, an account reference,
a transaction, a medical explanation for a missed payment, or a description of financial
hardship.

So the honest statement is:

| | Identifier | Narrative content |
|---|---|---|
| Sent to the model provider | ❌ never | ✅ **in full** |
| Stored in monitoring | ❌ never | ✅ **the quoted sentence** |
| In the decision log | ❌ never | ✅ the quoted sentence |

Anyone claiming "it's fine, the data is pseudonymised" has not read the system. Under
Recital 26, pseudonymised data remains personal data in any case. This section exists so
that sentence is never said in this engagement.

**What follows from it:** the transfer analysis in §6 is the load-bearing control, not the
pseudonymisation.

## 2. Roles

| Role | Party |
|---|---|
| **Controller** | The bank — determines purposes and means of processing complaint and transaction data |
| **Processor** | OpenAI (model inference), LangSmith / LangChain (monitoring), n8n host (workflow execution) |
| **Data subjects** | Customers who complain; account holders whose transactions are monitored; **and the bank's own handlers**, whose acceptance decisions are logged |
| **DPO** | The bank's — this assessment is prepared for their review, not in place of it |

Handlers are named deliberately. The decision log records who accepted what, which is
personal data about an employee and carries its own purpose limitation (§3, PA-5).

## 3. Records of processing activities (Art. 30)

| # | Processing activity | Purpose | Categories of data | Legal basis (Art. 6) | Recipients | Retention |
|---|---|---|---|---|---|---|
| **PA-1** | **Complaint triage** — classify the narrative and propose a routing queue | Route a complaint to the correct team; meet regulatory complaint-handling deadlines | Complaint narrative (free text: name, account, transaction, circumstances), product, complaint reference | **Art. 6(1)(c)** legal obligation — regulated complaint handling. Fallback **6(1)(f)** legitimate interests for the AI-assisted element **[verify]** | OpenAI (US); LangSmith (EU); the receiving team | Narrative: per the bank's existing complaints retention (typically 6 years). **Quoted sentence in monitoring: 90 days** |
| **PA-2** | **Reporting assistance** — draft regulatory report prose | Produce the periodic complaints return | **Aggregate figures only.** No narrative, no identifiers | Art. 6(1)(c) legal obligation | OpenAI (US); LangSmith (EU) | Draft text: 90 days. The report itself: per statutory retention |
| **PA-3** | **Transaction anomaly flagging** — detect and explain unusual patterns | Detect unauthorised transactions and financial crime; protect the customer | **Art. 6(1)(c)** legal obligation (AML/CTF and payment-services duties). **Not** legitimate interests — the obligation is the cleaner basis and the one supervisors expect **[verify]** | OpenAI (US); LangSmith (EU); the analyst | Candidate + case note: 12 months, or per AML retention where a case is opened |
| **PA-4** | **Decision monitoring** — record every proposal, reason code and outcome | Demonstrate the system can be audited; detect degradation | Pseudonymous reference, reason code, confidence, latency, **the quoted sentence (PA-1)** | Art. 6(1)(f) legitimate interests — model governance and auditability | LangSmith (EU) | **90 days**, then aggregate reason-code counts only |
| **PA-5** | **Handler acceptance logging** — record what the person did with each proposal | Calibrate the system; detect automation bias (risk R2) | Handler identifier, action taken, timestamp | Art. 6(1)(f) legitimate interests | Internal only — never a processor | 90 days, then aggregate |

**PA-5 purpose limitation, written down rather than left to custom:** this data is used to
**calibrate the system**, never to evaluate, rank, discipline or manage a handler. Using it
for performance management would (a) breach purpose limitation under Art. 5(1)(b), and
(b) move the system into Annex III(4) of the AI Act and make it high-risk. Two regimes, one
prohibition. It belongs in the works-council consultation for Phase 2. **[verify]**

### Special category data (Art. 9) — the uncomfortable part

Complaint narratives are free text written by distressed customers. They **will** contain
Art. 9 data that nobody asked for: health conditions explaining a missed payment,
bereavement, and occasionally trade-union or religious context.

The bank does not *seek* special category data, but it processes it. Art. 9(2)(f)
(establishment, exercise or defence of legal claims) and Art. 9(2)(g) (substantial public
interest, where national law provides it) are the plausible conditions. **[verify] — this is
the first question for the DPO.** No condition is asserted here because the honest answer is
that it depends on the member state's implementing law.

**What is done regardless:** the system never routes on the basis of Art. 9 content, never
extracts or indexes it, and never surfaces it as a feature. It is passed through as part of
the narrative and quoted only where the customer's own words drove the routing decision.

## 4. Data flow map

```
  CUSTOMER                                                       [EU]
     │  files a complaint (web form / email / phone note)
     ▼
  ┌──────────────────────────────────────────────────────────┐
  │ BANK — case management system            CONTROLLER  [EU] │
  │  complaint id · narrative · product · customer record     │
  └───────────────┬──────────────────────────────────────────┘
                  │  narrative + product        ← identifier NOT sent
                  │  reference → pseudonymised at this boundary (cx_…)
                  ▼
  ┌──────────────────────────────────────────────────────────┐
  │ ASSIST — input validation                            [EU] │
  │  rejects out-of-taxonomy product, text < 20 chars,        │
  │  caps at 6,000 chars. Costs no tokens, leaves no trace    │
  └───────────────┬──────────────────────────────────────────┘
                  │
                  ▼  ⚠ TRANSFER — narrative in full
  ┌──────────────────────────────────────────────────────────┐
  │ OpenAI — gpt-4o-mini                     PROCESSOR   [US] │
  │  returns: queue · confidence · verbatim quote             │
  │  no training on API data · zero data retention available  │
  └───────────────┬──────────────────────────────────────────┘
                  │
                  ▼
  ┌──────────────────────────────────────────────────────────┐
  │ ASSIST — guards                                      [EU] │
  │  scope · confidence · grounding. Ungrounded output is     │
  │  rejected here and never reaches a person                 │
  └───────┬──────────────────────────────────┬───────────────┘
          │ proposal + reason code           │ (leaf — cannot alter the decision)
          ▼                                  ▼  ⚠ STORES the quoted sentence
  ┌────────────────────────┐   ┌──────────────────────────────────────┐
  │ HANDLER — decides [EU] │   │ LangSmith — monitoring   PROCESSOR    │
  │  accept / override     │   │  eu.api.smith.langchain.com     [EU]  │
  └───────────┬────────────┘   │  cx_ ref · reason code · quote · 90d  │
              │                └──────────────────────────────────────┘
              ▼
  ┌────────────────────────────────────────────────────────┐
  │ BANK — case system: routed, with the reason recorded    │
  └────────────────────────────────────────────────────────┘
```

**UC-2 differs in one respect:** account references are pseudonymous *from creation* in the
pilot, because the data is synthetic. In production the same boundary applies — the analyst
sees the real account, the model never does. Only the transaction's own values and the
account's own baseline are sent.

**UC-3 sends no personal data at all** — the fact sheet is aggregate figures. It is the only
capability where the transfer question does not arise.

## 5. DPIA — Short form, for the highest-risk processing

**Subject: PA-3, transaction anomaly flagging.**

Selected over complaint triage deliberately. Triage processes more sensitive *content*, but
it improves a decision the bank already makes about a complaint the customer chose to file.
PA-3 is **systematic monitoring of behaviour that the customer did not initiate, involving
profiling, on a large scale** — the combination Art. 35(3)(a) and the EDPB criteria treat as
requiring assessment.

**Is a DPIA required?** Art. 35(3)(a) covers systematic and extensive evaluation of personal
aspects based on automated processing, including profiling, on which decisions producing
legal or similarly significant effects are based. PA-3 profiles and it is systematic, but
**no decision with legal or similarly significant effect is automated** — the system raises a
pattern and an analyst decides. So Art. 35(3)(a) is not squarely met. Against the EDPB's
nine criteria it scores on **evaluation/scoring**, **systematic monitoring**, **vulnerable
data subjects** and **innovative technology** — four, where two is the usual trigger.

**Conclusion: a DPIA is required.** Marginal calls go to doing the assessment.

| | |
|---|---|
| **Nature and scope** | Batch analysis of transaction records for ~250,000 retail customers. Deterministic detection of four patterns; an LLM writes the case note for raised candidates only |
| **Necessity and proportionality** | Necessary: AML/CTF and payment-services obligations require monitoring; unauthorised-transaction complaints are 7.4% of the corpus and arrive after the money has moved. Proportionate: only raised candidates reach the model — 56 of 2,069 records in the pilot batch, about 2.7%. The other 97.3% are never sent anywhere |
| **Risk 1 — false positives cause customer detriment** | *Likelihood 3, severity 3.* A wrongly flagged customer could face a frozen payment or an intrusive query. **Mitigation:** the system cannot freeze, block or contact. Every flag ends at an analyst. Ranking is by departure from the account's own baseline, never by amount |
| **Risk 2 — discriminatory flagging** | *Likelihood 2, severity 4.* Monitoring could disadvantage a group. **Mitigation:** no demographic attribute is an input; behaviour is compared only to the same account's history, so cross-customer comparison — the usual route to proxy discrimination — does not occur. Flag rates reviewed by segment during the pilot |
| **Risk 3 — narrative and behavioural data crossing purposes** | *Likelihood 2, severity 4.* PA-1 and PA-3 data joined would build a richer profile than either purpose supports. **Mitigation:** separate stores, separate pseudonym namespaces (`cx_` derived per source), no join key. Enforced by design, not policy |
| **Risk 4 — case-note text repeats data the analyst should not see** | *Likelihood 2, severity 2.* **Mitigation:** the grounding guard restricts the note to the candidate record's own values; anything else is rejected as `REJECT_VALUE_MISMATCH` |
| **Risk 5 — transfer to a US processor** | *Likelihood 3, severity 3.* See §6 |
| **Residual risk** | **Low-to-medium**, dominated by Risk 5. Acceptable for a pilot on synthetic data. **A pilot on real transaction data must not begin until §6 is closed** |
| **Consultation** | DPO review required before Phase 1. Works-council consultation required for PA-5. Art. 36 prior consultation with the supervisory authority **not** indicated, since residual risk is not high after mitigation **[verify]** |

## 6. Third-party and cross-border transfers

| Processor | Location | What it receives | Transfer mechanism | Status |
|---|---|---|---|---|
| **OpenAI** | **US** | **Complaint narratives in full** (PA-1); aggregate figures (PA-2); transaction values (PA-3) | EU–US Data Privacy Framework certification, **or** SCCs plus a transfer impact assessment | ⚠ **OPEN — the biggest gap in this pack** |
| **LangSmith** | **EU** (`eu.api.smith.langchain.com`) | Pseudonymous ref, reason code, confidence, **the quoted sentence** | No third-country transfer. Endpoint pinned in code, not left to a default | ✅ Closed |
| **n8n** | Cohort-hosted (POC only) | Demo data only | n/a — never touches production data | ✅ Out of scope |

**What must happen before any pilot on real data — a Phase 0 gate, not a Phase 2
discovery:**

1. **Confirm OpenAI's current transfer mechanism** and whether the bank's contracting entity
   is covered by DPF certification or requires SCCs.
2. **Execute a Data Processing Agreement** under Art. 28 with the sub-processor list, audit
   rights and breach notification terms.
3. **Complete a Transfer Impact Assessment** covering US government access risk against
   complaint narratives specifically — not generic API traffic.
4. **Enable zero data retention** on the API so prompts are not stored by the processor, and
   confirm API data is excluded from model training.
5. **Evaluate an EU-hosted alternative.** If the TIA is uncomfortable, the choice of model
   provider is a configuration change, not a redesign: prompts and guards live in version
   control and are provider-agnostic. API cost is 0.004% of running cost, so provider choice
   can be driven by data protection rather than price. *This is the practical answer to the
   transfer problem, and it is cheap because of how the system was built.*

**Until items 1–4 are complete, the pilot runs on the public CFPB corpus and synthetic
transactions — as it does today.** No customer data has been processed by this system.

## 7. Data subject rights

| Right | How it is supported | Honest limit |
|---|---|---|
| **Access (Art. 15)** | The case system is the record of truth and already supports access. The decision record adds the proposal, the reason code and what the handler did — all retrievable by pseudonymous ref, which the bank can re-derive from the complaint id | The salt must be retained for the life of the records, or the link is unrecoverable. Recorded as an operational dependency |
| **Rectification (Art. 16)** | Corrections are made in the case system. A past proposal is **not** rewritten — it is a record of what the system said at the time | Deliberate. Rewriting decision history would destroy the audit value that justifies PA-4 |
| **Erasure (Art. 17)** | Deletion in the case system; the monitoring record expires at 90 days regardless. For earlier erasure, the record is deleted by pseudonymous ref | Erasure **cannot** be propagated to the model provider retrospectively — which is exactly why zero data retention (§6 item 4) is a gate rather than a nice-to-have |
| **Restriction (Art. 18)** | A complaint can be marked excluded from AI processing; it routes manually. The system already treats "no proposal" as a first-class outcome, so this needs no special path | — |
| **Portability (Art. 20)** | Applies to 6(1)(a)/(b) processing. PA-1 and PA-3 rest on 6(1)(c), so it does not apply. Supported by the case system where it does | — |
| **Object (Art. 21)** | Applies to PA-4 and PA-5 (6(1)(f)). A customer objecting to monitoring processing has it excluded; the routing decision still gets made, by a person | — |
| **Not to be subject to solely automated decision-making (Art. 22)** | **Does not apply — and this is the cleanest statement in the pack.** No decision here is solely automated. Every capability ends at a human who accepts or overrides, and the acceptance is recorded. `decision` has exactly two possible values in code, neither of which is "act" | If the human step were ever removed, Art. 22 would engage immediately and require its own safeguards. Same trigger as the AI Act reclassification — one design property, two regimes |

## 8. Open points for the DPO

| # | Question | Blocks |
|---|---|---|
| 1 | Which Art. 9(2) condition covers special category data arriving unbidden in complaint narratives, under this member state's law? | Phase 0 |
| 2 | Is Art. 6(1)(c) or 6(1)(f) the correct basis for the AI-assisted element of PA-1? | Phase 0 |
| 3 | Confirm OpenAI's transfer mechanism; complete the DPA and TIA | **Any pilot on real data** |
| 4 | Is 90 days the right monitoring retention, balancing auditability against minimisation? | Phase 1 |
| 5 | Works-council consultation on PA-5 handler logging | Phase 2 |
| 6 | Is Art. 36 prior consultation indicated for PA-3? | Phase 1 |
