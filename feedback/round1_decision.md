# Round 1 Decision

Author: Ugo Ahukannah
Presented: 2026-08-30 · to the teaching staff, with the class standing in for Chleo's room

---

## Feedback summary

- **The pitch landed.** Feedback was positive overall; no objection to the framing, the
  evidence, or the staged ask.
- **The rest of the project was accepted as scoped** — research, dashboard, POC,
  monitoring, cost model and phasing all stand as presented.
- **One substantive recommendation: build all three use cases**, rather than carrying
  complaint triage alone into Round 2 with anomaly flagging and reporting assistance held
  back as later options.
- _(Add any further specifics from the room here — what was clearest, what was
  unconvincing, and the answers to the three questions the closing slide asked.)_

## Decision

**KEEP** — industry and use case both hold up.

Sector stays financial services, mid-size. Complaint triage stays the lead use case. The
recommendation does not change direction; it **widens Round 2's build scope** from one use
case to three.

## Why

Nothing in the feedback challenged the sector, the client profile, the choice of triage as
the lead, or the honesty position — that 60.5% is agreement rather than accuracy and that
Phase 0 must create expert labels before any accuracy claim exists. Changing direction now
would discard evidence that was accepted rather than questioned.

The exclusions also stand: the customer-facing chatbot and creditworthiness scoring remain
out, and the guardrail that a predicted payout never orders the routing queue remains in.
The recommendation was to build the three *proposed* use cases, not to revisit the two
refusals.

## If CHANGE: what changes

_Record what changed (industry / sector / size / use case / approach) and why._

Not applicable — this is a KEEP. The scope change is recorded under Round 2 focus below.

## Round 2 focus

- **POC improvements:** extend the existing n8n workflow so the same validate → propose →
  human-confirms spine serves all three use cases, rather than building three separate
  demos.
- **MVP scope (the one capability that must run):** complaint triage, end to end, remains
  the capability that must actually work. The other two are built on the same spine — see
  the note below on how all three are covered without putting the MVP at risk.
- **Compliance / ROI / strategy priorities:** the consulting package now covers all three
  use cases. Each needs its own AI Act reasoning (anomaly flagging and reporting assistance
  have different human-decision boundaries from triage), its own GDPR data-flow entry, and
  its own line in the ROI and risk work.

---

## Note on building all three, and the rubric tension

The recommendation is adopted. It is worth recording how, because taken naively it
conflicts with the Round 2 rubric, which states plainly that **a small MVP that runs scores
above an ambitious one that does not** — and weights the working MVP at 15 points.

Three separate products would put that at risk. Three capabilities on one shared spine does
not, and is a stronger architecture story:

| Layer | Shared across all three |
|---|---|
| Input validation | Same boundary checks, same `REJECT_INVALID_INPUT` |
| Decision guards | Same five guards and reason-code vocabulary (`classifier/decide.py`) |
| Human boundary | The system proposes; a person decides. Never routes, flags or files alone |
| Observability | Same trace record, same reason codes, one monitoring project |

What differs per use case is the prompt, the data and the output — not the control
structure. That is the point worth making in the Round 2 presentation: adding a use case
costs a prompt and a schema, not a new system, because the safety and observability
machinery was built once.

**Build order, riskiest last:**

1. **Complaint triage** — already runs. Hardened into the MVP first, so the 15-point
   requirement is satisfied before anything speculative starts.
2. **Reporting assistance** — cheapest of the three. Generates the narrative sections of a
   complaint report from `data/complaints_dashboard.csv` via the existing metrics module.
   New data: none.
3. **Anomaly flagging** — most work. Needs synthetic transaction data, which the brief
   permits, and a different detection approach. Built last, and descoped to a documented
   design if time runs short rather than shipped half-working.

Recorded so the Round 2 write-up can be honest about the order and the reason for it.
