# Sector Research — Mid-Size Financial Services

Author: Ugo Ahukannah
Capstone Round 1 · Client: "Chleo", CEO

---

## 1. The client we are pitching

| Attribute | Working assumption |
|---|---|
| Sector | Financial services — retail banking and consumer lending |
| Size | Mid-size: ~500 employees, ~250,000 retail customers, EU-established |
| Products | Current/savings accounts, a credit card portfolio, personal and vehicle lending, payments |
| Stated fear | AI "is simply not transparent" — Chleo cannot say *what the AI is* or *how they would sign up* |
| Regulatory exposure | EU AI Act (in force), GDPR, plus sector supervision (national competent authority) |

These are assumptions, not facts given by Chleo. She left the dinner before giving detail.
Every number downstream that depends on firm size is flagged as an assumption in
`cost_estimation/cost_analysis.md` rather than presented as evidence.

## 2. Why complaint operations is the right place to look first

Chleo's fear is about **transparency**, not capability. The winning first use case is
therefore one where the AI's decision can be shown on a screen and argued with — not one
where it disappears into a score. Complaint handling qualifies:

- Every item is a text document with a human-readable outcome.
- The firm already has a ground-truth label for each one (how it was actually resolved).
- Regulators already require the firm to evidence its handling. Observability is not
  an extra cost here; it is already the job.
- Nothing about it touches creditworthiness, which is where the AI Act's teeth are.

## 3. The public dataset

**Source:** [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/),
US Consumer Financial Protection Bureau, public API, no authentication, no personal data
(the CFPB scrubs narratives before publication). 17,355,295 complaints indexed at time
of pull.

**Why this one:** it is the only large, free, openly licensed corpus of real
consumer-finance complaints *with the free-text narrative attached*. Synthetic complaint
text would not test the hard part of the problem — that real customers write badly,
at length, and about three things at once.

**What was pulled and curated** (`data_prep.py`):

| Step | Result |
|---|---|
| Raw pull, narrative-bearing, 2026-05-01 → 2026-08-01 | 36,022 complaints |
| Restricted to products a mid-size consumer bank actually operates | 19,386 |
| Cut to the window with complete published data (see §4) | **16,839** |

**Scope exclusions and why.** Debt collection (31% of the raw window), mortgage, student
loan and credit reporting were dropped. Those complaints are overwhelmingly filed against
third-party collection agencies, mortgage specialists and the three credit bureaus — not
against a firm of Chleo's shape. Including them would have made the largest category in
the analysis a business she is not in.

## 4. Two data-quality corrections, made before any analysis

Both were found by checking the data rather than trusting it, and both would have produced
a confident wrong answer.

**a) Publication lag masquerading as a collapse in complaints.**
The CFPB publishes a complaint only after the company responds or 15 days elapse, so the
most recent weeks are systematically incomplete. Weekday volume holds at 1,700–2,270/week
through 2026-06-28 and then falls to 607 → 430 → 555 → 418 → 244. Read naively, that is a
73% drop in complaints and a great slide. It is an artifact. **The analysis window is cut
at 2026-06-27**; later records stay in the raw pull and are excluded from every rate and
trend. (Week 2026-W18 is also partial — the window opens mid-week on 1 May — and is
excluded from trend claims.)

**b) A dead metric that looked like an ops SLA.**
"Days from complaint received to sent to company" is **0 for 96% of records**. It measures
CFPB's own routing latency, not any firm's handling speed. It was dropped rather than
shown. A handling-time metric on the dashboard would have to come from the client's
internal system, which we do not have — and the pitch says so.

## 5. What the corpus actually shows

Analysis window **2026-05-01 → 2026-06-27**, 16,839 complaints, 567 firms, 64 issue classes.

### Volume and cost signal by product

| Product | Complaints | Share | Closed with monetary relief |
|---|---:|---:|---:|
| Checking or savings account | 5,835 | 34.7% | 14.0% |
| Credit card | 5,382 | 32.0% | 17.2% |
| Money transfer / virtual currency / money service | 2,551 | 15.1% | 10.6% |
| Vehicle loan or lease | 1,523 | 9.0% | 3.0% |
| Payday / title / personal loan | 1,163 | 6.9% | 3.4% |
| Prepaid card | 385 | 2.3% | 10.9% |

Two thirds of volume sits in deposits and cards, and those are also where money actually
goes out of the door. Credit card complaints end in monetary relief **17.2%** of the time
versus **3.0%** for vehicle lending — a nearly 6x difference. Where a complaint lands
matters financially, which is the argument for getting routing right.

### Issue concentration — the case for triage

| Issue | Complaints | Share |
|---|---:|---:|
| Managing an account | 3,344 | 19.9% |
| Problem with a purchase shown on your statement | 1,887 | 11.2% |
| Problem with a lender or other company charging your account | 949 | 5.6% |
| Fraud or scam | 810 | 4.8% |
| Closing an account | 778 | 4.6% |

**The top 5 of 64 issue classes account for 46.1% of all complaints.** This is the single
most important finding for the pitch: a classifier does not need to be good at 64 things.
It needs to be good at five, and honest about the rest.

### Resolution and service levels

| Measure | Value |
|---|---|
| Timely response rate | 98.0% (335 untimely of 16,839) |
| Closed with any relief | 19.7% |
| Closed with monetary relief | 12.7% |
| Narrative length, median | 1,201 characters |
| Narrative length, 90th percentile | 3,013 characters |

A median complaint is roughly 200 words and the long tail runs to 500+. This is the
workload: a human reads ~1,200 characters, decides which of 64 buckets it belongs in,
and routes it. That is a task a language model does well and a task humans find tedious —
the good quadrant for a first AI deployment.

### Geographic concentration

CA 2,341 · FL 1,692 · TX 1,605 · NY 1,165 · GA 757 · IL 593 · PA 566 · NJ 562.
US geography does not transfer to an EU client and is **not** used as evidence about
Chleo's book. It is reported only to be explicit that this is a US corpus.

## 6. The honest limitation of using this dataset

This is US regulatory-escalation data. Chleo's firm is EU-established and most of its
complaints never reach a regulator at all. So the corpus is used as a proxy for the
**structure** of a complaint inbox — the issue mix, the language, the resolution
patterns — and explicitly **not** as a forecast of her volumes. Any volume figure in the
cost model comes from a stated assumption about her firm, not from this data.

Saying this out loud in the pitch is itself the transparency argument Chleo is asking for.

## 7. Sources

- CFPB Consumer Complaint Database and public API — https://www.consumerfinance.gov/data-research/consumer-complaints/
- CFPB publication policy (complaint published after company response or 15 days)
- Regulation (EU) 2024/1689 (EU AI Act) — classification work deferred to Round 2
- Regulation (EU) 2016/679 (GDPR)
