# Cost Analysis — Complaint Triage

Author: Ugo Ahukannah
Capstone Round 1 · Deliverable 6 of 7

Every figure below is computed by `cost_model.py`. Re-run it to reproduce them:
`python cost_estimation/cost_model.py` → `cost_model.json` and `assumptions.md`.

**The full assumptions table is `assumptions.md`**, generated from the same model, with
every input classified as sourced, measured, an assumption about the client, or a
judgement of mine. The judgements are the ones to challenge first.

---

## The headline, before the detail

**At Chleo's size, this does not pay for itself on labour, and the pitch says so.**

The model is close to free to run — **€0.29 a year** in API charges. What costs money is the
oversight around it. Set against a realistic labour saving, the system runs at a **net
€2,822 a year**, and the case rests entirely on whether better routing prevents complaints
escalating to the ombudsman.

**It pays for itself if it prevents four ombudsman referrals a year.** Whether it does is
exactly what the pilot exists to measure. We are not claiming it does.

A consultant who arrived with a labour-saving story here would be selling a number that
does not survive contact with the firm's actual volume.

## 1. How many complaints Chleo actually has

Sized from a public regulatory benchmark rather than guessed.

| Input | Value | Source |
|---|---:|---|
| Current accounts | 250,000 | assumption — mid-size retail firm |
| Credit cards | 80,000 | assumption — ~32% cross-hold |
| Complaints per 1,000 current accounts, per half-year | 3.7 | FCA aggregate complaints data 2025 H2 |
| Complaints per 1,000 credit cards, per half-year | 3.6 | FCA aggregate complaints data 2025 H2 |

**≈ 2,426 reportable complaints a year** (1,850 current account + 576 card).

That is roughly **47 a week** — a real, continuous workload, and a much smaller one than
"AI for complaints" usually implies. Getting this number early is what stops the rest of
the model being fiction.

## 2. What triage costs today

| Input | Value | Basis |
|---|---:|---|
| Handler salary, gross | €45,000 | midpoint: NL banking CS ≈ €39.5k, IE complaints investigator ≈ €52k |
| Employer on-costs | +30% | judgement |
| Productive hours per FTE-year | 1,550 | judgement — net of leave, training, admin |
| **Fully loaded hourly cost** | **€37.74** | derived |
| Triage time per complaint, today | 6 min | judgement |

**243 hours a year, ≈ €9,156.** About 0.16 FTE. Worth improving; not worth a
transformation programme.

## 3. What it costs to run the AI

| Line | Per year | Note |
|---|---:|---|
| LLM API | **€0.29** | 684 input + 49 output tokens per complaint, **measured**, at gpt-4o-mini list price |
| Platform (n8n hosting, LangSmith, logging) | €1,800 | €150/month |
| Quarterly accuracy review and prompt maintenance | €5,600 | 2 days per quarter at €700 |
| **Total running cost** | **€7,400** | |

**The model is not the cost. Oversight is** — 97% of the running cost is human review and
platform, and 0.004% is the model. That single ratio is worth a slide on its own: it kills
the "AI is expensive" objection and replaces it with the true constraint, which is that a
system making decisions needs someone accountable for watching it.

At the current OpenAI list prices used in this model — [`gpt-4o-mini`](https://developers.openai.com/api/docs/models/gpt-4o-mini)
at $0.15/$0.60 and [`gpt-4o`](https://developers.openai.com/api/docs/models/gpt-4o) at
$2.50/$10.00 per 1 million input/output tokens — the same measured token mix costs 16.7×
as much on `gpt-4o`, taking the annual API line from €0.29 to €4.91. Model choice is simply
not a financial decision at this volume — it is an accuracy decision.

## 4. The saving, stated honestly

The recommended configuration is **assist-only**: the model proposes a team and quotes its
reason, and a handler confirms. The handler still reads the complaint. So the saving is the
categorise-and-route step, not the reading.

| | |
|---|---:|
| Triage time today | 6 min |
| Triage time assisted | 3 min (judgement) |
| **Annual labour saving** | **€4,578** |
| Running cost | €7,400 |
| **Net annual position** | **−€2,822** |

Claiming the full €9,156 would require the model to route unsupervised at an accuracy it
has not demonstrated. What has been measured is 56.8% *agreement* with consumer-selected
labels (`classifier/FINDINGS.md`), and agreement with those labels is not deployment
accuracy. The half-saving is the honest version.

## 5. Where the value actually is

| Input | Value | Source |
|---|---:|---|
| Uphold rate | 55.54% | FCA 2025 H2 |
| Average redress per upheld complaint | £215 (≈ €252) | FCA 2025 H2 |
| Ombudsman case fee | £650 (≈ €760) | FOS, frozen for 2025/26 |
| Free ombudsman cases per year | 3 | FOS |

**Break-even: 3.7 avoided ombudsman referrals a year covers the entire running cost.**

Mis-routed complaints sit in the wrong queue, breach response deadlines and escalate. At
€760 a case with only three free, a handful of avoided escalations pays for the system.
Four a year is a small number — which is the point. It is a target a pilot can actually
test, rather than a percentage improvement invented for a slide.

**This is a hypothesis, not a finding.** Nothing measured in Round 1 establishes that
better triage reduces escalations. The pilot's job is to test it.

## 6. Upfront cost — fixed fee per phase

The pricing basis is **€700 per consulting day**, but each phase is contracted as a fixed
fee. A client whose stated objection is uncertainty should not be handed an open-ended
commitment.

| Phase | Days | Fee | What it buys |
|---|---:|---:|---|
| **0 — Discovery and expert labelling** | 8 | **€5,600** | Scope, data access, and 300 complaints labelled by two of the firm's own handlers — the ground truth that does not currently exist |
| **1 — Pilot build and 60-day shadow run** | 12 | **€8,400** | Shadow triage alongside the existing process; handlers do not act on suggestions, and performance is measured against the firm's own labels |
| **2 — Deployment, if the pilot passes** | 15 | **€10,500** | Case-system integration, handler training, monitoring, handover |
| **Commitment to the pilot decision** | 20 | **€14,000** | |
| **Full programme** | 35 | **€24,500** | |

Chleo commits **€14,000** to reach a decision point, not €24,500. Phase 2 is contingent.

**Client-side effort not in the fee:** roughly 6 handler-days for the labelling exercise,
plus a case-system contact in Phase 2.

**Phase 0 is worth buying even if the AI is never built.** It produces a measured human
agreement rate on the firm's own complaint taxonomy — which tells Chleo whether her
categories can be applied consistently by anyone at all. On the public data, they largely
cannot (`classifier/FINDINGS.md`).

## 7. When this stops being marginal

The labour saving alone would cover the running cost at **3,921 complaints a year** —
roughly **530,000 current accounts**, about twice Chleo's assumed size.

This table varies **current accounts only** and holds cards aside, so its complaint counts
are lower than the €2,426 total above and its savings lower than the €4,578 headline. Same
model, narrower slice — not a competing figure.

| Firm size (current accounts) | Current-account complaints/yr | Labour saving | Covers €7,400 running cost? |
|---:|---:|---:|---|
| 250,000 (Chleo, assumed) | ~1,850 | €3,491 | No |
| 530,000 | ~3,921 | €7,400 | Break-even |
| 1,000,000 | ~7,400 | €13,962 | Yes, comfortably |

Two honest readings of this, and Chleo should hear both:

1. If she grows, or if her real complaint volume is higher than the FCA benchmark implies,
   the labour case improves on its own.
2. If it does not, the project should be justified on escalation avoidance and consistency —
   or not done. **"Do not do this yet" is a legitimate outcome of the pilot** and is priced
   into the phasing.

## 8. What would move these numbers most

| Sensitivity | Effect |
|---|---|
| Actual complaint volume | Drives everything. The FCA benchmark is UK reportable complaints; Chleo's real inbox may be materially larger, and Phase 0 measures it |
| Time saved per complaint (3 min) | The softest number here. If assisted triage saves only 1 minute, the saving falls to €1,526 |
| Whether escalations actually fall | The entire ROI case. Untested |
| Model choice | Almost none. €0.29 vs €4.91 a year |

## 9. Honest limitations

- **UK benchmarks for an EU client.** The FCA and FOS are the best public sources with this
  granularity. An EU firm's national scheme differs in fee structure. Directionally sound,
  not exact.
- **Currency.** GBP converted at 1.17, stated rather than hidden.
- **The soft numbers are judgements, not sources.** Triage minutes, on-costs, productive
  hours and platform cost carry no citation and are labelled as judgements in
  `cost_model.py`.
- **No cost of being wrong.** A misrouted complaint that escalates has a cost this model
  does not attempt to price, because Round 1 has no evidence for the rate.
