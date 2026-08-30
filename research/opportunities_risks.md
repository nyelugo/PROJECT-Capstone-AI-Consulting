# Opportunities and Risks — AI at a Mid-Size Financial Services Firm

Author: Ugo Ahukannah
Capstone Round 1 · Companion to `sector_research.md`

---

## 1. Framing

Chleo is not asking whether AI works. She is asking what it *is* and whether she can
trust it. So this map is organised by **how visible the AI's reasoning is**, not by how
clever the technique is. Opportunities where a human can see and overrule the machine
are ranked above opportunities with a better theoretical payoff and an opaque middle.

## 2. Opportunity map

| # | Opportunity | Evidence from the data | Visibility to a non-technical CEO | Verdict |
|---|---|---|---|---|
| O1 | **Complaint triage and routing** | Top 5 of 64 issue classes = 46.1% of volume; median narrative 1,201 chars | High — the input is text, the output is a label plus a reason | **Pitch it** |
| O2 | **Transaction anomaly flagging for human review** | "Fraud or scam" 810 + "Unauthorized transactions" 437 = 7.4% of complaints | Medium-high if the flag carries its reason and a human decides | **Pitch it** |
| O3 | **Regulatory and complaint reporting assistance** | 98.0% timely response is already a reported SLA; 19.7% relief rate is already tracked | High — drafts a document a human signs | **Pitch it** |
| O4 | Early-warning on monetary-relief exposure | Credit card relief 17.2% vs vehicle 3.0% (5.7x) | Medium — a prediction with money attached | Round 2 candidate, under the guardrail that predicted payout never orders the queue |
| O5 | Customer-facing chatbot for account queries | Not evidenced by this corpus | Low — the classic "what is the AI?" trap | **Do not pitch now** |
| O6 | Creditworthiness scoring / automated lending decisions | Out of corpus scope | Low, and Annex III high-risk under the AI Act | **Do not pitch** |

**Why O5 and O6 are refused in the pitch.** A chatbot is the first thing a nervous CEO
imagines and the worst possible opening move: it fails in public, in the customer's voice,
and its errors are unbounded. Credit scoring is squarely Annex III high-risk under the
EU AI Act, which means conformity assessment, registration and a fundamental-rights
impact assessment before a single decision goes live. Recommending either to a
transparency-averse client in a first meeting would be malpractice. Saying no to them
out loud is part of the pitch.

## 3. Risk map

Likelihood and impact are 1–5. This is the Round 1 view; the full matrix with mitigations
per risk is a Round 2 deliverable.

### Regulatory and legal

| Risk | L | I | Note |
|---|:-:|:-:|---|
| Misclassifying the system's AI Act risk tier and building to the wrong obligations | 3 | 5 | Preliminary view is limited risk, but this must be *argued*, not asserted — see §4 |
| Complaint text is personal data under GDPR; a triage model processes it | 4 | 4 | Legal basis, retention and DPIA all required before production |
| Automated routing later drifts into automated decision-making (GDPR Art. 22) | 2 | 5 | Routing is not deciding. The boundary has to be designed in, not assumed |
| Cross-border transfer if an LLM API processes EU customer text outside the EEA | 4 | 4 | Real and immediate — model hosting region is a procurement decision, not a detail |

### Technical

| Risk | L | I | Note |
|---|:-:|:-:|---|
| Model performs well on US CFPB text and poorly on the client's own | 4 | 3 | The corpus is a structural proxy, not the client's book. Pilot on real data before trusting numbers |
| Long tail: 59 of 64 issue classes carry 53.9% of volume with thin per-class examples | 4 | 3 | Design for abstention — "I don't know" routed to a human is a correct answer |
| Silent degradation after deployment | 3 | 4 | This is exactly what the monitoring sample exists to answer |
| Prompt injection via customer-submitted complaint text | 3 | 3 | Customers write the input. Treat narratives as untrusted data |

### Ethical

| Risk | L | I | Note |
|---|:-:|:-:|---|
| Triage systematically deprioritises a group (language, complexity, vulnerability) | 3 | 5 | Vulnerable-customer complaints are the ones that most need a human. Measure per-segment, not just overall accuracy |
| Automation bias — reviewers rubber-stamp the model's label | 4 | 3 | Mitigated by showing confidence and reason, and by sampling overrides |
| Relief-exposure prediction (O4) used to slow-walk expensive complaints | 2 | 5 | The reason O4 is deferred, not pitched |

### Operational

| Risk | L | I | Note |
|---|:-:|:-:|---|
| Staff read this as a headcount reduction and disengage | 4 | 4 | Pitch it as triage support with the human deciding, and mean it |
| Live demo fails in front of the panel | 3 | 2 | Backup recording — required by the presentation guide |
| Scope creep from triage into a full service platform | 4 | 3 | One capability, end to end. Everything else is Round 2 or later |
| 98.0% timely response leaves little headline room for improvement | 3 | 3 | Honest reframe: the win is cost and consistency, not the SLA number |

## 4. The compliance position, stated honestly

**Round 1 working view: on the intended use, complaint triage has not been identified as
matching an Annex III high-risk use. This is not a tier classification and not a legal
opinion — Round 2 owes the validation. The reasoning below matters more than any label.**

- It is not Annex III creditworthiness assessment — it never evaluates a customer's
  credit or access to a financial product.
- It classifies and routes; a human confirms and resolves. Keeping that boundary intact is
  what keeps the position defensible. Autonomous routing would be a new assessment, not an
  upgrade to this one.
- Transparency obligations (Art. 50) apply if a customer is interacting with the AI
  directly. Under the design pitched here, they are not — it is an internal tool.
- GDPR applies regardless of any AI Act tier. Complaint narratives are personal data.
- Hosting region and cross-border transfer controls are not yet verified.

**This is deliberately not a final classification.** Round 2 owes the step-by-step
reasoning, a conformity summary and a technical documentation outline. Presenting a
confident tier label in Round 1 without that work would be exactly the kind of
unearned certainty Chleo is right to distrust.

## 5. What this means for the pitch

1. Lead with the use case whose reasoning is visible, not the one with the biggest number.
2. Show the monitoring before showing the accuracy. Chleo's question is "can I see it?",
   not "how good is it?".
3. Name the two things we refuse to build (chatbot, credit scoring) and why. A consultant
   who only says yes is selling, not advising.
4. Be explicit that the US dataset proves the *shape* of the problem, and that her real
   numbers come from a pilot.
