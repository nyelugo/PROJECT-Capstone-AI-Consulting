# Strategic Deployment and Commercialisation Plan

Author: Ugo Ahukannah
Capstone Round 2 · System: **Assist** — complaint triage, reporting assistance, anomaly flagging
Client: **Chleo**, mid-size EU retail bank

---

## The strategy in one paragraph

The ROI analysis produced an uncomfortable number and it shapes everything below: **a
bespoke build does not pay back for a firm Chleo's size** — −31.0% at 36 months, break-even
in month 69. The capability is sound; the *commercial shape* is wrong. A firm needs about
3,800 complaints a year for a one-off build to pay for itself and Chleo has 2,426. So the
plan is not "build it and hope". It is: **spend €18,200 to reach a decision on the firm's
own data, and structure everything after that so the build is not paid for once by one
firm.** Productised across five mid-size firms the same capability returns +16.9% over 36
months, and +96.6% with oversight brought in-house. That is the strategy — the phases below
are how it gets tested before it gets funded.

## Phase plan

| | **Phase 0 — Discovery and expert labelling** | **Phase 1 — Pilot (60-day shadow run)** | **Phase 2 — Full deployment** | *Phase 3 — Scale (optional)* |
|---|---|---|---|---|
| **Duration** | 4 weeks | 12 weeks | 10 weeks | ongoing |
| **Consultant days** | 8 | 18 | 20 | retainer |
| **Fee** | **€5,600** | **€12,600** | **€14,000** | per-client licence |
| **Cumulative** | €5,600 | **€18,200** | €32,200 | — |
| **What it buys** | The ground truth that does not exist today | Evidence about *this firm*, at no operational risk | The system in daily use, owned by the bank | The same capability at other firms |
| **Runs on** | The firm's own complaint history | Live complaints, shadow mode — handlers do not act on proposals | Live complaints, assistive | — |
| **Exit** | Go / no-go on Phase 1 | **The decision point.** Go / no-go on Phase 2 | Handover complete | — |

### Phase 0 — Discovery and expert labelling (weeks 1–4)

The unusual thing this phase buys: **two of the bank's own handlers independently label 300
complaints, before any AI touches anything.**

That is the ground truth that does not exist today, and it is worth buying even if the bank
never builds this system — inter-annotator agreement between two trained handlers reveals
whether the firm's own categories can be applied consistently *by anybody*. If two experts
agree only 70% of the time, no classifier will do better, and the real problem is the
taxonomy rather than the technology. **That is a finding worth €5,600 on its own.**

Also in Phase 0, and gating everything after it:

- **Legal:** put **[verify-1]** and **[verify-3]** from the AI Act assessment to counsel —
  both concern UC-2, both are cheaper to answer before it is built
- **Data protection:** confirm the model provider's transfer mechanism, execute the DPA,
  complete the Transfer Impact Assessment, enable zero data retention. **No pilot on real
  data starts until this is closed**
- **Baseline measurement:** current triage minutes per complaint, current report preparation
  days, current unauthorised-transaction volumes. *Without these, Phase 1 cannot prove
  anything*

### Phase 1 — Pilot, 60-day shadow run (weeks 5–16)

All three capabilities run **alongside** the existing process. Handlers do their job exactly
as before; the system proposes in parallel and nobody acts on it. Nothing about the
customer's experience changes.

Shadow mode is chosen over a limited live rollout for one reason: it makes the pilot
**measurable without being risky**. Every proposal can be compared against what the handler
actually did, at zero operational exposure.

- Weeks 5–8: build all three capabilities on the shared spine; integrate read-only
- Weeks 9–16: 60-day shadow run, weekly reason-code review
- Week 16: pilot report and the Phase 2 decision

### Phase 2 — Full deployment (weeks 17–26)

Only if the Phase 1 gates below are met, and only under a commercial structure that makes
the numbers work. Case-system write integration with receipt confirmation (closing the
"trace records the decision, not the delivery" gap); handler and analyst training —
**which is also the Art. 4 AI literacy obligation, so it is compliance work, not a nicety**;
monitoring handover to a named internal owner.

### Phase 3 — Scale (optional)

Same capability, other mid-size firms. This is where the economics turn positive, and it is
a commercial decision rather than a technical one — see commercialisation below.

## Timeline and milestones

```
 Week    1    4    8   12   16   20   24   26
         │    │    │    │    │    │    │    │
 P0      ████████                                Discovery + 300 expert labels
         ▲    ▲
         │    └── M1  Inter-annotator agreement known · legal + DPA cleared
         └─────── kickoff

 P1           ████████████████████              Build, then 60-day shadow run
                   ▲         ▲    ▲
                   │         │    └── M4  ★ GO / NO-GO on Phase 2
                   │         └─────── M3  Mid-pilot review (week 12)
                   └───────────────── M2  All three capabilities running in shadow

 P2                              █████████████  Deployment, if M4 passes
                                       ▲     ▲
                                       │     └── M6  Handover complete, owner named
                                       └──────── M5  First live assisted routing

 Value                                       ●──────►  benefits accrue from month 7
```

| # | Milestone | Week | Gate |
|---|---|---:|---|
| M1 | Expert labels complete; legal and DPA cleared | 4 | **If inter-annotator agreement < 70%, stop.** The problem is the taxonomy, not the AI |
| M2 | Three capabilities running in shadow | 8 | All guards firing; monitoring populated |
| M3 | Mid-pilot review | 12 | Course-correct, or stop early if acceptance is very low |
| M4 | **Pilot report — go / no-go** | 16 | The gates below |
| M5 | First live assisted routing | 22 | Handlers trained; rollback tested |
| M6 | Handover; internal owner named | 26 | Monitoring owned internally |

## KPIs per phase

### Phase 0

| KPI | Target | Why it matters |
|---|---|---|
| Complaints labelled by two handlers independently | 300 | The sample that makes everything else measurable |
| **Inter-annotator agreement** | **Report it, do not target it** | The ceiling on any classifier. **Below 70% → stop and fix the taxonomy** |
| Baseline triage minutes per complaint | Measured | The ROI model assumes 6. If it is 3, the labour case halves |
| Legal and transfer questions closed | 5 of 5 | Hard gate on Phase 1 with real data |

### Phase 1 — and these are the numbers that greenlight Phase 2

| # | KPI | **Greenlight threshold** | Measured from |
|---|---|---|---|
| **G1** | **Team-level accuracy against expert labels** | **≥80%** | Shadow proposals vs. Phase 0 labels |
| **G2** | **Handler acceptance rate** | **≥75% and ≤97%** | The decision log |
| **G3** | **Ungrounded outputs reaching a handler** | **Zero** | Guard rejection counts |
| **G4** | **Correct abstention** | ≥95% of low-confidence items go to a person rather than being guessed | Reason-code distribution |
| **G5** | Triage time on accepted proposals | ≥40% reduction vs. the Phase 0 baseline | Timed sample |
| **G6** | Anomaly precision on analyst disposition | ≥30% of raised candidates judged worth investigating | Analyst outcomes |
| **G7** | Oversight effort | ≤3 days per quarter, annualised | Time recorded |

**G2 has an upper bound, and it is deliberate.** An acceptance rate above 97% does not mean
the system is excellent — it means handlers have stopped reading. That is risk R2
(automation bias), and it is a **failure condition, not a success**. It is the one KPI here
that a vendor would never propose.

**Any of G1, G2 or G3 missed → do not proceed to Phase 2.** G3 is absolute: one ungrounded
output reaching a handler is a design failure, not a tuning problem.

**If G6 fails but G1–G5 pass: deploy UC-1 and UC-3, drop UC-2.** The architecture allows
that — one capability can be switched off without touching the others — and the AI Act
assessment already identifies UC-2 as the one carrying classification risk.

### Phase 2

| KPI | Target |
|---|---|
| Proposals delivered and confirmed received by the case system | 100% — closes the delivery gap |
| Handler acceptance rate, 90-day rolling | Stable in 75–97%; investigate any drift |
| Reason-code distribution vs. pilot | No unexplained shift |
| Time to first draft of the quarterly report | ≥50% reduction |
| Staff trained (Art. 4 AI literacy) | 100% of handlers and analysts |
| Cost per complaint, all-in | ≤ the Phase 1 measured figure |

## Go-to-market

**Who buys this.** Not "banks". **EU financial services firms with 2,000–15,000 complaints a
year** — roughly 200,000 to 1,500,000 retail customers. Below that, complaint volume does not
justify any build. Above it, the firm has a dedicated triage desk and buys a platform. The
band is narrow and it is where the pain is real and unserved.

**The economic buyer is the CEO or COO, not the CIO.** The purchase is triggered by a
regulatory or reputational event, not a technology roadmap. The blocker is almost always
trust rather than budget — Chleo's objection was transparency, and she raised it before price.

**Channel.**

1. **Direct consulting** for the first three to five clients. Phase 0 is the wedge: it is
   small, it is genuinely useful standing alone, and it produces the evidence that sells
   Phase 1.
2. **Compliance-led referral** thereafter. The AI Act and GDPR packs are reusable artifacts;
   firms in this band are actively looking for a defensible position on both.
3. **Not a marketplace or a reseller.** The differentiator does not survive being sold by
   someone who cannot explain it.

**Pricing.**

| | Model | Price |
|---|---|---|
| Phase 0 | Fixed fee | €5,600 |
| Phase 1 | Fixed fee | €12,600 |
| Phase 2 | Fixed fee | €14,000 |
| **From client 2 onward** | **Licence + implementation** | **€6,440 implementation + €7,200/yr licence** |

Fixed fee per phase throughout, never time and materials. The client's problem is
uncertainty; an open-ended commitment adds to it.

**Differentiator: the refusal is the product.** Every competitor demonstrates a correct
answer. This system demonstrates *a wrong answer being caught* — four fabricated quotations
in a sample of sixty, each one stopped and named. For a buyer whose stated objection is that
AI cannot be seen, a system that shows its own failures by name is a different category of
thing from one that shows accuracy. Two supporting differentiators: an honest number
(56.8% presented as agreement, not accuracy) buys more trust from a sceptical buyer than a
polished one; and the compliance packs come with the build rather than being commissioned
separately afterwards.

## Commercialisation model

**A licensed product implemented by consulting — not SaaS, not a bespoke build.**

Ruled out, with reasons:

| Model | Why not |
|---|---|
| **Bespoke build per client** | **The ROI analysis says no.** −31% over 36 months for a firm this size. It is what was pitched and the numbers refuse it |
| **Multi-tenant SaaS** | Would require processing complaint narratives from many banks in one platform. The transfer and controller analysis becomes far harder, and it is the opposite of the trust position. Wrong product for this buyer |
| **Open-source with paid support** | Gives away the only durable asset — the guard and reason-code design — for a support business at this scale |

**How it works:** the client deploys in their own tenancy and remains sole controller. They
licence the decision spine, guards, reason-code vocabulary, prompts and compliance templates.
The consultant implements, tunes the taxonomy to that firm, and runs the first year of
oversight before handing it to a named internal owner.

**Why it works, in one line:** the build is paid for once and implemented many times — per
client €6,440 rather than €32,200 — which turns a −31% return into +16.9%, and +96.6% once
the client owns oversight. **The technology does not change at all. Only who pays for the
build.**

## Stakeholder communication plan

| Stakeholder | Cares about | Cadence | Format | The message that lands |
|---|---|---|---|---|
| **Chleo (CEO)** | Whether this is real, and whether she can explain it to her board | Phase gates: M1, M4, M6 | 20-minute session, live system, one page | "Here is every check it ran, and here is the one it failed." Never a dashboard of accuracy |
| **Head of Complaint Operations** | Her team's day, and her SLA | Weekly during the pilot | 15-minute standup | "Your handlers stay the decision-maker. If they stop reading, that is our failure condition, and we measure it" |
| **Compliance / DPO** | Liability | M1, then monthly | Written; the AI Act and GDPR packs | "Not high-risk, and here is the step-by-step reasoning — including the two questions I need you to answer" |
| **CTO / IT** | What they will own at 2am | M2, M5, M6 | Technical walkthrough + repo | "No training pipeline, no new platform. Prompts and guards in version control. Swapping model provider is a config change" |
| **Complaint handlers** | Whether this is about replacing them | Before shadow starts, then fortnightly | Small group, hands-on | "It proposes, you decide, and we record when you disagree — because that is how we find out where it is wrong" |
| **Works council** | Handler acceptance logging (PA-5) | Before Phase 2 | Formal consultation | "Calibration only. Written into the GDPR register as a purpose limitation, and using it for performance management would breach two regimes at once" |
| **Board / Audit** | Regulatory exposure | Quarterly from Phase 2 | Reason-code distribution + acceptance trend | "Every decision has a reason code and a named human action beside it" |

**The one rule across all of them:** lead with what the system *refused* to do and why,
before what it got right. That is the sequence that built trust in Round 1, and it is the
sequence that keeps it.
