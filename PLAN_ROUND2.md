# Round 2 — Plan

Read from the course pages on 2026-08-31: `unit_9_0_0` (deliverables), `pf-03` rubric
(`unit_8_2_2`), `pf-05` Round 2 presentation guide (`unit_8_2_4`), `pf-01` brief
(`unit_8_2_0`). **This file records the literal spec.** Where the page names a filename, a
folder, a heading or a count, it is copied exactly — not paraphrased.

Round 1 is closed: presented 2026-08-30, decision KEEP, submitted to `project-5`.
Campus identifier for this round: **`final-project`**.

---

## The eight deliverables, at their literal paths

The page's own folder structure puts four documents at the **repo root**, not in a docs
folder. Deviating loses easy points for no gain.

| # | Path (literal) | Weight | Status |
|---|---|---|---|
| 1 | `use_case_definition.md` | 15 (shared with POC) | new |
| 2 | `poc/poc_workflow.json` + `poc/poc_documentation.md` + **demo recording** | 15 (shared) | rehome from `n8n/` |
| 3 | `roi_risk_assessment.md` | **20** | new |
| 4 | `compliance/eu_ai_act_compliance.md` | **20** | new |
| 5 | `compliance/gdpr_documentation.md` | 10 | new |
| 6 | `strategic_plan.md` | 10 | new |
| 7 | `presentation.pdf` *(PDF preferred)* | 10 | new deck |
| 8 | `mvp/` + `mvp_documentation.md` + `requirements.txt` + `.env.example` | **15** | new |

Plus: "Round 1 materials still present in the repo (or linked)" — already satisfied.

## Required contents, verbatim from the page

**1. `use_case_definition.md`** — business problem statement · company profile (industry,
size, current state) · proposed AI solution and system type · key stakeholders and
interests · success criteria (**at least 2 measurable outcomes**) · out-of-scope boundaries
· **note how this evolved from Round 1**.

**2. POC** — workflow export or annotated screenshots · **demo recording (2–5 minutes),
end to end** · `poc_documentation.md` covering tools, steps, AI capability shown, limits vs
production, how to reproduce. n8n is an accepted tool.

**3. `roi_risk_assessment.md`** — upfront costs · ongoing costs · quantified business value
· **ROI for 12 and 36 months using `ROI = (Net Benefit / Total Cost) × 100`** · assumptions
table · break-even note. Risk matrix: **at least 6 risks** across regulatory, technical,
ethical, operational, each with likelihood (1–5), impact (1–5), mitigation.

**4. `eu_ai_act_compliance.md`** — risk classification **+ step-by-step reasoning** ·
mandatory requirements summary (if High or Limited) · **Conformity Assessment Summary
(1–2 pages)** · **Technical Documentation Outline (ToC / skeleton)**.

**5. `gdpr_documentation.md`** — data flow map · processing activities register (purpose,
legal basis, retention, recipients) · **short DPIA for the highest-risk processing** ·
data subject rights support · third-party / cross-border transfers.

**6. `strategic_plan.md`** — phases POC → Pilot → Full deployment · timeline and milestones
· go-to-market (buyers, channel, pricing, differentiator) · stakeholder communication plan
· **KPIs per phase, including what greenlights pilot → full deployment** ·
commercialisation model.

**8. MVP** — functional application users can try · core AI capability actually runs ·
**basic error handling** · `mvp_documentation.md` that "lets someone else start it".

## The presentation is a different deck from Round 1

Round 1's guide wanted a tight pitch; this one prescribes a **10-slide structure** and a
**four-person panel**. Do not adapt the Round 1 deck — build to this.

- **12–15 minutes total** (10 min presenting + 2–5 min Q&A). Round 1 ran ~5.5 min.
- **Max 10–12 slides** excluding title and backup. **Minimum 24pt body text.**
- Panel: **CEO** (worth investing in?) · **Legal/Compliance** (liability?) · **CTO**
  (viable?) · **Operations Manager** (will this disrupt my team?). All four must be served.
- Prescribed slides: 1 Title · 2 The Problem · 3 Proposed AI Solution · 4 **POC Demo** ·
  5 Business Case/ROI · 6 Risk highlights (**top 2–3 only, do not read the matrix**) ·
  7 Compliance Summary · 8 Strategic Deployment Plan · 9 **MVP Demo (required)** ·
  10 Conclusion with a call to action.
- **Bridge from Round 1**: one slide or 30 seconds on what changed after the staff
  presentation. Ours is the widened use-case scope.
- **Backup recordings for both demos.** The guide: "A live failure with no fallback costs
  you the easiest points in the deck."
- Submit slides **before the slot, Week 9 Day 5**.

Q&A the guide says to expect — all six are answerable from existing repo evidence, and the
prep is knowing them without reading: AI Act reasoning walkthrough · where the hours-saved
number came from · who is liable when output is wrong · handling a deletion request · why
not an off-the-shelf tool · what you'd do differently.

---

## The scope tension, stated plainly

Staff recommended building all three use cases. Three separate documents say the opposite
about the **MVP** specifically:

> "Keep the MVP small on purpose. One capability that runs end to end beats four
> half-wired screens." — brief
>
> "Scope the MVP to one capability you can finish rather than a product you can only
> describe" — brief, Scope and Constraints
>
> "A small MVP that runs scores above an ambitious one that does not." — rubric, item 2

The MVP is worth 15 points and the criterion is binary-ish: *runs, core AI capability
works, basic error handling, someone else can start it*. Three working capabilities score
the same 15 as one. There is **no marginal grade upside** to building three, and a real
downside if the third is half-wired on presentation day.

Where all three genuinely pay is the **consulting package**, which is worth 60 points and
is graded on breadth and honesty: three use cases give the AI Act doc three classifications
to reason through, the GDPR doc three data flows, the ROI model three value streams, and
the strategic plan a real sequencing argument. That is where the recommendation is worth
honouring in full.

**DECIDED 2026-08-31 (Ugo): build all three.** The staff recommendation is followed
literally — all three use cases are implemented in the MVP, not just documented. My reading
of the brief was that one runnable capability is the safer play; Ugo's call is to honour the
room's advice, and the risk it carries is managed rather than avoided:

| Risk the brief warns about | How this build answers it |
|---|---|
| "four half-wired screens" | One shared spine, three thin capabilities on top. The control structure is built and tested once |
| A capability that does not run on the day | Triage is hardened and banked **first**, before either new one starts. It already runs |
| Anomaly flagging has no data | Synthetic transaction data, which the brief permits explicitly under Scope and Constraints |
| Time competing with 60 points of documents | The documents get *easier*, not harder — each describes something that actually runs |

**The shared spine, which is the architecture argument for the deck:**

```
validate input → LLM proposes → guards verify the proposal is grounded → human confirms
```

Every capability is the same shape — a model proposes something, guards check it is grounded
in evidence that actually exists, and a person decides. What differs is only what "grounded"
means:

| | UC-1 Triage | UC-3 Reporting | UC-2 Anomaly |
|---|---|---|---|
| Proposes | A routing queue | A report narrative | An explanation of a flag |
| Grounded in | A verbatim quote from the complaint | Figures computed by `dashboard/metrics.py` | The transaction's own values |
| Guard checks | The quote appears in the text | Every number cited was computed, not invented | Every figure cited matches the record |
| Human confirms | The routing | The report | The escalation |

One reason-code vocabulary, one trace path, one error-handling story. Adding a capability
costs a prompt and a guard, not a new system — which is a stronger thing to say to a CTO
than "I built one thing."

Standing guardrail, unchanged: **a predicted payout never orders the queue.**

## Build order

Highest weight first, and the MVP banked before anything speculative.

1. `use_case_definition.md` — cheap, and it fixes the scope every other document inherits.
2. **MVP** (`mvp/`) — triage end to end, with error handling. Banks the 15.
3. `roi_risk_assessment.md` (20).
4. `compliance/eu_ai_act_compliance.md` (20).
5. `compliance/gdpr_documentation.md` (10).
6. `strategic_plan.md` (10).
7. POC rehome to `poc/` + `poc_documentation.md` + **record the 2–5 min demo**.
8. `presentation.pdf` to the 10-slide structure + **record the MVP demo backup**.
9. Order within step 2: triage hardened and banked first, then reporting assistance (no new
   data), then anomaly flagging (synthetic transaction data, generated first).

## Open

- **Presentation slot** — "Week 9 Day 5, instructor sets the slot". Date not yet confirmed
  in this repo; it sets everything above.
