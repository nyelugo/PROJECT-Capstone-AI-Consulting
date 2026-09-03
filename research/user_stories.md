# User Stories, and where the MVP falls short

Author: Ugo Ahukannah
Capstone Round 2 · Companion to [`../use_case_definition.md`](../use_case_definition.md)

**Every status below was checked against the running application, not asserted.** Where a
story is unmet the evidence is named — a file, a control that does not exist, a field that
is not recorded.

---

## The framing that decides everything

**Chleo is the buyer. She is not the user.** She opens this **weekly**. Her complaint
handler lives in it all day, her fraud analyst works a morning batch, her compliance officer
opens it once a quarter, and her DPO only ever arrives after something has gone wrong.

Writing stories only for Chleo would produce a dashboard nobody works in. That was the
original design error in this MVP — one screen built for four different people — and these
stories exist to keep it from recurring.

| Role | Cadence | Accountable for |
|---|---|---|
| **Chleo** — CEO | Weekly | Whether to keep paying for it |
| **Head of Complaint Operations** | Daily | The SLA, and her team's day |
| **Complaint handler** | All day | Routing each complaint correctly |
| **Fraud analyst** | Daily batch | Escalating what matters, ignoring what doesn't |
| **Compliance officer** | Quarterly | A return with her name on it |
| **DPO / internal audit** | On demand | Reconstructing a decision months later |

Status key: **MET** · **PARTIAL** — works, but not enough to rely on · **NOT MET**.

---

## Chleo — CEO, weekly

> **C1.** As Chleo, I want to see whether the system worked this week **without opening a
> single case**, so that I can supervise it in five minutes.
> *Accept: counts of proposed, held and outstanding, above the fold.*
> **MET** — Overview opens on exactly this.

> **C2.** As Chleo, I want to know **how often my people agreed with it**, so that I can tell
> whether it is trusted or merely tolerated.
> *Accept: an agreement rate, measured only over items a person actually decided.*
> **MET** — and it refuses to speak below 20 decisions, which is the honest behaviour.

> **C3.** As Chleo, I want to compare **this week against last**, so that I can tell a bad
> week from a normal one.
> *Accept: week-over-week movement on volume, agreement and refusals.*
> **MET** — Overview opens on “Was this a normal week”, with the last complete week against
> the one before it and a nine-week table beneath. The batch carries nine ISO weeks of real
> receipt dates, so the comparison is measured rather than modelled. What a fixed batch
> still cannot show is *new* work arriving — that is what the Phase 2 feed adds.

> **C4.** As Chleo, I want to **turn a capability off myself**, so that I am not dependent on
> a consultant when something looks wrong on a Monday morning.
> *Accept: a per-capability switch, effective without a restart.*
> **MET** — a toggle per capability on Overview, written to `queues/settings.json` and
> honoured by each page immediately. Switching one is itself recorded in the decision log,
> because turning a capability off is a decision about the system.

> **C5.** As Chleo, I want to know **what it cost me**, so that I can hold it against the
> value it claims.
> *Accept: spend for the period, and the split between AI and oversight.*
> **MET** — batch cost and annual, read from `roi_model.json` so it cannot disagree with the
> business case. Weakened by C3: a cost with no period is hard to act on.

> **C6.** As Chleo, I want reassurance that **nothing reached a customer**, so that I can
> answer my board's first question.
> *Accept: an explicit statement or count of customer-facing actions — zero.*
> **MET** — “Reached a customer: 0 — by design, not by luck” sits beside the other three
> headline figures. An absence is only evidence once it is counted.

## Head of Complaint Operations — daily

> **O1.** As the ops lead, I want to see **what is past deadline and still untouched**, so
> that I can direct my team at the right cases.
> *Accept: a count, and one click to that list.*
> **MET** — the red callout names it, and the queue filters to it.

> **O2.** As the ops lead, I want to see **which teams the model gets wrong**, so that I know
> whether the problem is the model or one team's taxonomy.
> *Accept: overrides broken down by proposed team.*
> **MET** — Operations breaks overrides down by proposed team, with a **Sent instead**
> column showing where handlers actually sent them. That column is the difference between
> fixing a prompt and fixing a taxonomy.

> **O3.** As the ops lead, I want to see **acceptance per handler**, so that I can spot
> someone who has stopped reading.
> *Accept: a per-handler rate, flagged above 97%.*
> **MET** — acceptance per handler on Operations, flagged above 97% over ten or more
> decisions. Risk **R2** named *measured per handler* as its mitigation; until this existed
> the register promised a control that did not exist.

> **O4.** As the ops lead, I want to know **how much work is outstanding per team**, so that
> I can balance the day.
> *Accept: outstanding items grouped by proposed team.*
> **MET** — with how many of each team's outstanding items are already past target.

## Complaint handler — all day

> **H1.** As a handler, I want the day's complaints **already read and sorted**, so that I am
> not typing into a box something that already arrived in the case system.
> *Accept: a standing queue, populated before I arrive.*
> **MET.**

> **H2.** As a handler, I want to see **why it proposed that team**, so that I can check it in
> seconds rather than re-reading the whole complaint.
> *Accept: the customer's own sentence, plus every check that ran.*
> **MET** — the quote and the guard ladder, both on screen.

> **H3.** As a handler, I want to **clear the obvious ones together**, so that I am not
> trained to click without reading.
> *Accept: multi-select and a bulk action.*
> **MET** — and this exists *because* of R2, not despite it.

> **H4.** As a handler, when the system is wrong I want to say **where it should have gone**,
> so that my correction is worth something.
> *Accept: a reroute records the destination team.*
> **MET** — rerouting asks which team it should have gone to, drawn from
> `classifier/teams.py` so a correction cannot name a team the system does not have. The
> destination is stored on the event and surfaced on Operations.

> **H5.** As a handler, I want to **note why** I overrode it, so that a reviewer understands
> a decision months later.
> *Accept: a free-text note stored with the action.*
> **MET** — an optional note sits beside the destination selector and is shown against the
> recorded decision.

> **H6.** As a handler, I want to filter to **what needs me**, so that handled work does not
> clutter my list.
> *Accept: default to pending; handled reachable in one click.*
> **MET** — plus a Disagreements filter, which is the review view.

> **H7.** As a handler, I want to **find one specific complaint**, so that I can act on a
> customer's chase-up call.
> *Accept: lookup by the reference the customer quotes.*
> **PARTIAL** — free-text search exists, but references are pseudonymous (`cx_…`), so the
> number a customer reads down the phone matches nothing. A real integration resolves this;
> today it is a dead end.

## Fraud analyst — daily batch

> **A1.** As an analyst, I want candidates **ranked by how unusual they are for that account**,
> so that I spend my morning on the right ones.
> *Accept: ranked by departure from the account's own baseline, never by amount.*
> **MET** — and the guardrail is enforced in `detect()`, not just documented.

> **A2.** As an analyst, I want to **record what I decided**, so that precision can eventually
> be measured against my judgement rather than against planted labels.
> *Accept: escalate / dismiss / needs-more, all recorded.*
> **MET** — and this is the data that would finally replace the self-agreement figure.

> **A3.** As an analyst, I want to see **the individual transactions** behind a flag, so that I
> can judge it rather than take the summary on trust.
> *Accept: the transactions in the candidate, listed.*
> **NOT MET** — only aggregates are shown: count, total, the account median, times-normal.
> The `txn_ids` are on the record and never rendered. Asking an analyst to escalate on a
> summary is asking for exactly the automation bias the design elsewhere refuses.

> **A4.** As an analyst, I want to **tune a threshold** when a rule is too noisy, so that the
> queue stays worth reading.
> *Accept: thresholds adjustable without a code change.*
> **NOT MET** — `SPIKE_RATIO`, `BURST_MIN` and the structuring window are module constants.

## Compliance officer — quarterly

> **R1.** As the compliance officer, I want **the whole return drafted**, not one section at a
> time, so that I review a document rather than assemble one.
> *Accept: all sections drafted in one action.*
> **MET.**

> **R2.** As the compliance officer, I want **every figure traceable to how it was computed**,
> so that I can defend it to a regulator.
> *Accept: each figure resolves to its source.*
> **PARTIAL** — the figures used are listed as text (`complaints = 16839`). Nothing links
> to the computation, the window, or the query behind it. Enough to spot-check, not enough
> to defend.

> **R3.** As the compliance officer, I want to **sign each section**, so that responsibility
> is recorded per section rather than for the document as a whole.
> *Accept: per-section sign-off, with a name and time.*
> **MET.**

> **R5.** As the compliance officer, I want to **choose the period the return covers**, so
> that I produce a return for a quarter rather than for whatever the system was pointed at.
> *Accept: a period control, and figures that change with it.*
> **MET** — a period selector offers the whole batch and each calendar month it covers, and
> every figure, citation and grounding check is recomputed for the chosen range. Periods the
> batch cannot fill are not offered, and switching period discards the drafts rather than
> showing them under the wrong heading. This story was missing from the first version of this
> document — the audit was run against the running app and still did not notice the control
> was absent, which is its own lesson about auditing what is there rather than what should be.

> **R4.** As the compliance officer, I want to **export the signed return**, so that I can put
> it where returns live.
> *Accept: a download of the accepted sections.*
> **NOT MET** — there is no export on the reporting page at all. The document is drafted,
> reviewed and signed, and then cannot leave the screen.

## DPO / internal audit — on demand

> **D1.** As an auditor, I want to **reconstruct a decision months later**, so that I can
> answer an ombudsman.
> *Accept: from a log row, reach what the system saw and proposed.*
> **PARTIAL** — the log records the item id, the proposal and the reason code, but nothing
> links back to the item, and the queue holds no history. Reconstruction is manual.

> **D2.** As an auditor, I want to **export the record**, so that it can go into an evidence
> pack.
> **MET** — CSV export on the decision log.

> **D3.** As an auditor, I want to know **who actually decided**, so that the record means
> something.
> *Accept: an authenticated identity.*
> **NOT MET** — "Signed in as" is a free-text box. It records who *said* they decided.

> **D4.** As an auditor, I want to **filter the log by date**, so that I can isolate a period.
> *Accept: a date range filter.*
> **NOT MET** — filters are capability, action, person and free text. No date control, which
> is the first thing anyone reaches for in an audit log.

> **D5.** As an auditor, I want to **honour an erasure request**, so that the firm can meet
> Article 17.
> *Accept: delete every record for one subject reference.*
> **NOT MET** — `queue_store` has no delete path for a single subject. The GDPR pack
> promises deletion by pseudonymous ref; the MVP cannot perform it.

---

## Score

| | Chleo | Ops lead | Handler | Analyst | Compliance | Audit | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| MET | 6 | 4 | 6 | 2 | 3 | 1 | **22** |
| PARTIAL | 0 | 0 | 1 | 0 | 1 | 1 | **3** |
| NOT MET | 0 | 0 | 0 | 2 | 1 | 3 | **6** |

**22 of 31 fully met.** Chleo and the ops lead are at **100%** — that was the scope
decision and it is done. The handler is one story short, and that one waits on the case
system. What is left belongs to the analyst, the compliance officer and the auditor.

## What is left

**Chleo and the ops lead are fully served — every story in both sets is met.** That was the
scope decision, and it is done. The remaining shortfalls belong to the three roles outside
it.

**1 · The analyst cannot see the transactions (A3).** Only aggregates are shown; `txn_ids`
is on the record and never rendered. Asking an analyst to escalate on a summary invites
exactly the automation bias the design refuses everywhere else.

**2 · The signed return cannot leave the screen (R4).** Drafted, reviewed, signed — and then
nowhere to go.

**3 · Erasure cannot be performed (D5).** The GDPR pack commits to deletion by pseudonymous
reference; there is no path for it.

**4 · The audit log has no date filter (D4).** The first control anyone reaches for.

**5 · A log row does not link back to its item (D1).** Reconstruction is manual.

**6 · Figures in the return are not traceable to their computation (R2).** Listed as text —
enough to spot-check, not enough to defend.

| | |
|---|---|
| **Fixable now** | A3 transaction listing · R4 export · D5 erasure by ref · D4 date filter · D1 link a log row to its item · R2 figure provenance |
| **Needs Phase 2** | D3 real identity (case-system auth) · H7 customer-facing references · A4 per-portfolio thresholds |

Six of the nine remaining shortfalls need nothing but work. The three that genuinely wait
are blocked on the same thing: an integration that does not exist yet.
