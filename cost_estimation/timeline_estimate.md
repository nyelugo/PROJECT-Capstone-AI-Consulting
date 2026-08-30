# Timeline Estimate — Complaint Triage

Author: Ugo Ahukannah
Capstone Round 1 · Companion to `cost_analysis.md`

---

## Shape

Three phases with a real decision gate between the pilot and deployment. **~18 weeks from
kickoff to production, if the pilot passes** — and passing is not assumed.

```
Wk 1-2    Phase 0  Discovery + expert labelling        EUR 5,600
Wk 3-5    Phase 1  Pilot build
Wk 6-13   Phase 1  60-day shadow run (live, no-action)   EUR 8,400 (covers wk 3-13)
Wk 14              >>> DECISION GATE <<<
Wk 15-18  Phase 2  Deployment (contingent)             EUR 10,500
```

## Phase 0 — Discovery and expert labelling · weeks 1–2 · 8 days

| Week | Work |
|---|---|
| 1 | Access to a complaint extract; confirm actual volume against the FCA benchmark; map the firm's real teams (replacing this project's 7-team reconstruction) |
| 2 | **Two experienced handlers independently label 300 complaints.** Measure their agreement with each other |

**Exit criteria**
- Real annual complaint volume, measured not benchmarked
- A labelled set that can serve as ground truth
- **A measured human agreement rate** — the actual ceiling any model can be held to

**This phase is worth buying even if no AI is ever built.** If two experienced handlers
disagree substantially on the firm's own categories, the categories are the problem and no
model fixes that. On the public data they largely do disagree
(`classifier/FINDINGS.md`) — so this is a real risk, not a formality.

## Phase 1 — Pilot build and shadow run · weeks 3–13 · 12 days

| Weeks | Work |
|---|---|
| 3–5 | Port the POC to the firm's data; retarget the taxonomy to its real teams; wire monitoring; agree the pilot's success criteria **in writing, before the run** |
| 6–13 | **60-day shadow run.** The system proposes; handlers work as they always have; nothing is routed by the model |

**Why shadow rather than assist first:** a shadow run measures accuracy without any
possibility of harming a customer's complaint, and gives a clean before/after on handling
time. Assist-only goes live at Phase 2, not before.

**Exit criteria**
- Team-level accuracy against the firm's own labels, compared to the Phase 0 human ceiling
- Abstention rate and the reason-code distribution
- Evidence-quote fidelity — the fabricated-justification rate
- Per-segment behaviour: does triage systematically deprioritise any group of customers?
- Measured effect on time-to-first-touch

## Decision gate — week 14

Three outcomes, all legitimate:

| Outcome | When | What happens |
|---|---|---|
| **Proceed** | Accuracy at or near the human ceiling; no adverse segment effect | Phase 2 begins |
| **Iterate** | Close but not there; failures concentrated and fixable | A short extension, re-scoped and re-quoted |
| **Stop** | Accuracy well below the human ceiling, or the taxonomy is the real problem | The engagement ends. Chleo keeps the labelled set, the measured ceiling and the analysis |

**Stop is a real option and is priced in.** Chleo commits €14,000 to reach this gate, not
€24,500. A pilot that cannot fail is not a pilot.

## Phase 2 — Deployment · weeks 15–18 · 15 days · contingent

| Week | Work |
|---|---|
| 15 | Integration with the case management system |
| 16 | Handler training — including how to override, and that overriding is expected |
| 17 | Monitoring, alert thresholds, the quarterly review routine |
| 18 | Handover, runbook, go-live in **assist-only** mode |

Autonomous routing is **not** in scope. It is a separate decision, on evidence from a
period of assisted running, with its own risk assessment.

## What would move the timeline

| Risk | Effect | Mitigation |
|---|---|---|
| Complaint data access takes longer than a week | Pushes everything | Start the access request before Phase 0 opens |
| Handlers cannot be released for labelling | Phase 0 stalls; nothing downstream is measurable | 3 days each, bookable in advance; the single most schedule-critical dependency |
| Case-system integration is harder than expected | Phase 2 only | Deployment is deliberately last and separately quoted |
| The 60-day run shows a seasonal artifact | Wrong conclusion from a real measurement | Compare against the same window in the prior year |
| The firm's own taxonomy proves inconsistent | Whole basis of the project | Found in Phase 0, before serious money is spent — which is why it is first |

## Two deliberate scheduling choices

**The labelling exercise is first, not last.** Every accuracy number in the project depends
on ground truth that does not currently exist. Building a model before there is anything to
measure it against is how a project arrives at week 12 with a demo and no evidence.

**The shadow run is 60 days, not two weeks.** At ~47 complaints a week, a fortnight yields
under 100 — enough to see a system work, not enough to trust a per-segment accuracy figure.
Two months gives roughly 400 complaints, which is a defensible sample.
