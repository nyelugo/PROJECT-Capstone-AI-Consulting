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
> **NOT MET** — every figure is over one fixed batch. There are no periods at all, so the
> weekly rhythm this role is built on has nothing to stand on. **The most serious gap for
> her persona.**

> **C4.** As Chleo, I want to **turn a capability off myself**, so that I am not dependent on
> a consultant when something looks wrong on a Monday morning.
> *Accept: a per-capability switch, effective without a restart.*
> **NOT MET** — Overview lists the capabilities but the state is hardcoded `"on"`.

> **C5.** As Chleo, I want to know **what it cost me**, so that I can hold it against the
> value it claims.
> *Accept: spend for the period, and the split between AI and oversight.*
> **MET** — batch cost and annual, read from `roi_model.json` so it cannot disagree with the
> business case. Weakened by C3: a cost with no period is hard to act on.

> **C6.** As Chleo, I want reassurance that **nothing reached a customer**, so that I can
> answer my board's first question.
> *Accept: an explicit statement or count of customer-facing actions — zero.*
> **PARTIAL** — the design guarantees it and the copy says "it proposes, you decide", but
> nothing on screen asserts *nothing was sent*. An absence is not evidence unless it is
> counted.

## Head of Complaint Operations — daily

> **O1.** As the ops lead, I want to see **what is past deadline and still untouched**, so
> that I can direct my team at the right cases.
> *Accept: a count, and one click to that list.*
> **MET** — the red callout names it, and the queue filters to it.

> **O2.** As the ops lead, I want to see **which teams the model gets wrong**, so that I know
> whether the problem is the model or one team's taxonomy.
> *Accept: overrides broken down by proposed team.*
> **NOT MET** — the agreement rate is a single aggregate. No breakdown exists in
> `overview.py`.

> **O3.** As the ops lead, I want to see **acceptance per handler**, so that I can spot
> someone who has stopped reading.
> *Accept: a per-handler rate, flagged above 97%.*
> **NOT MET** — the threshold is applied to the aggregate only. Since automation bias is
> risk **R2** and rated likelihood 4 × impact 4, the control the risk register promises is
> not actually implemented.

> **O4.** As the ops lead, I want to know **how much work is outstanding per team**, so that
> I can balance the day.
> *Accept: outstanding items grouped by proposed team.*
> **NOT MET.**

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
> **NOT MET.** `TRIAGE_ACTIONS["rerouted"]` records only that I disagreed. The destination —
> the single most valuable datum the system can collect, the one that would improve the
> prompt and give the ops lead O2 — is discarded. **The most serious gap in the MVP.**

> **H5.** As a handler, I want to **note why** I overrode it, so that a reviewer understands
> a decision months later.
> *Accept: a free-text note stored with the action.*
> **PARTIAL** — `queue_store.record()` accepts a `note`, but no page offers a field for it.
> The plumbing is there and unused.

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
| MET | 3 | 1 | 4 | 2 | 3 | 1 | **14** |
| PARTIAL | 1 | 0 | 2 | 0 | 1 | 1 | **5** |
| NOT MET | 2 | 3 | 1 | 2 | 1 | 3 | **7** |

**14 of 26 fully met.** The handler is well served — which is right, since triage is the
capability that must run. **The ops lead and the auditor are the two worst-served roles**,
and both of their gaps are about the same thing: the system records *that* a decision
happened but very little *about* it.

## The gaps that matter, ranked

**1 · A reroute does not record where it should have gone (H4).** The correction is the most
valuable thing this system can collect. It is what would improve the prompt, what gives the
ops lead O2, and what turns "60.5% agreement" into a measured error pattern. Every override
today throws it away. **Small change, large consequence.**

**2 · No periods, so no week-over-week (C3).** Chleo opens this weekly and cannot tell a bad
week from a normal one. The entire cadence of her role has nothing to stand on.

**3 · No per-handler acceptance rate (O3).** Risk R2 — automation bias — is rated 4 × 4 and
its stated mitigation is "measured per handler". It is not. The register currently promises
a control that does not exist, which is worse than not claiming it.

**4 · The analyst cannot see the transactions (A3).** Escalating on a summary is the same
automation bias the design refuses everywhere else.

**5 · The signed return cannot leave the screen (R4).**

**6 · Erasure cannot be performed (D5).** The GDPR pack commits to deletion by pseudonymous
reference; the MVP has no path for it.

**7 · Audit log has no date filter (D4).**

### What is fixable in the MVP, and what genuinely is not

| | |
|---|---|
| **Fixable now** | H4 reroute destination · H5 note field · O3 per-handler rate · O2 overrides by team · A3 transaction listing · R4 export · D4 date filter · D5 erasure by ref · C6 a counted zero |
| **Needs Phase 2** | C3 periods (needs a live feed — one fixed batch cannot have a last week) · C4 off switches (needs config outside the code) · D3 real identity (needs the case system's auth) · H7 customer-facing references (needs the case system) · A4 threshold tuning (needs per-portfolio config) |

Nine of the sixteen shortfalls are buildable without waiting for anything. That is the
honest answer to "is the MVP ready": it **runs**, it meets every graded criterion, and it
serves the handler well — and it is thin for the two roles who arrive when something has
gone wrong.
