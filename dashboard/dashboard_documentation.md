# Dashboard Documentation — Complaint Operations

Author: Ugo Ahukannah
Capstone Round 1 · Deliverable 3 of 7

---

## What this is

An executive view of complaint operations at a mid-size financial services firm, built
for one specific audience: **Chleo, a CEO who does not trust AI because she cannot see
what it does.** Every panel therefore carries a plain-English takeaway instead of a
statistical caption, and the dashboard ends with a panel stating what the data is *not*.

Built in **Python** (Streamlit + Plotly). The brief allows PowerBI, Tableau or Python;
Python was chosen because the Round 2 MVP is a Python application, so this dashboard
becomes the shell the complaint classifier plugs into rather than an artifact that gets
rebuilt. It also means the figures shown here and the figures quoted in the research
documents are computed by the same module and cannot drift apart.

## How to run it

```bash
conda activate bootcamp-env
streamlit run dashboard/app.py
```

Opens on `http://localhost:8501`. No API keys, no network access, no credentials —
it reads `data/complaints_dashboard.csv`, which is committed.

## Files

| File | Role |
|---|---|
| `dashboard/app.py` | The view — layout, charts, takeaways |
| `dashboard/metrics.py` | **Single source of truth for every number shown** |
| `dashboard/screenshots/` | `dash-top.png`, `dash-mid.png`, `dash-bottom.png` |

`metrics.py` is deliberately separate. Every figure in `README.md`,
`research/sector_research.md` and this document is produced by
`python dashboard/metrics.py`, so a number cannot say one thing on a slide and something
else in a document. That is a defect this project is explicitly designed to prevent.

## The six metrics, and why each one earns its place

The rubric asks for 5–7 stakeholder-relevant metrics. Each is justified below by the
decision it supports — a metric that does not change what Chleo would do is not on here.

### 1. Complaint volume, weekly · *"How many complaints arrive each week"*
**Value:** 1,487–2,488 per week, averaging 2,045, no trend across the period.
**Why a CEO cares:** it establishes that this is a continuous, absorbable workload rather
than a seasonal spike. That distinction decides whether you automate or hire temporarily.
**Form:** line chart. Single series, so no legend — the title names it.
**Caveat rendered honestly:** the weekly figure moves around by up to a third between
weeks. The takeaway says so rather than calling it "steady".

### 2. Timely response rate · *"Answered on time"*
**Value:** 98.0%, with 335 complaints answered late.
**Why a CEO cares:** it is already a reported regulatory measure. Putting it on screen
signals that the AI conversation starts from her existing obligations, not from a
technology.
**Honest framing:** 98.0% leaves almost no headline room. The pitch does **not** claim
AI will improve it. The win offered is cost and consistency.

### 3. Monetary relief rate · *"Cost money to resolve"*
**Value:** 12.7% closed with money paid out; 19.7% needed some remedy.
**Why a CEO cares:** this is the only metric on the dashboard denominated in her money.

### 4. Volume vs. cost by product · *two charts, never one*
**Values:** Checking/savings 5,835 complaints, credit card 5,382 — but credit card pays
out 17.2% of the time against 3.0% for vehicle lending, **5.7× higher**.
**Why a CEO cares:** it proves that volume and cost are different pictures, which is the
entire argument for investing in accurate routing.
**Design note:** these are two separate charts on purpose. A count and a percentage on one
dual-axis chart is the most common way to mislead with a business dashboard, and the two
scales here differ by three orders of magnitude.

### 5. Issue concentration · *"What people actually complain about"*
**Value:** the top 5 of 64 issue categories are **46.1%** of all complaints.
**Why a CEO cares:** this is the load-bearing metric of the whole pitch. It converts
"AI could help" into "the model needs to be good at five things and honest about the
rest", which is a scope she can approve and a risk she can bound.
**Design note:** one hue, two steps — the top five in the full series blue, the remainder
in a lighter step of the same ramp. Ordinal encoding, not a second category.

### 6. Reading load · *"How much reading that is"*
**Value:** median 1,201 characters (~200 words); 90th percentile 3,013.
**Why a CEO cares:** it is the closest thing to a labour cost the public data supports.
It is what a person actually does with each complaint, and therefore what any saving
would come from.

### Supporting: resolution mix · *"How complaints end"*
**Value:** 79.7% resolved with an explanation, 12.7% money back, 7.0% put right another
way, 0.6% no resolution recorded.
Shown because "four in five need only an explanation" is the fact that makes triage
worth doing — most complaints do not need a decision-maker, they need routing.

## A field collision that had to be fixed

The CFPB carries two different timeliness measures and putting both on one screen
unlabelled produced an apparent contradiction:

| Field | Meaning | Count |
|---|---|---:|
| `Timely response? = No` | Firm missed the response deadline | 335 (2.0%) |
| `Company response = "Untimely response"` | No resolution was ever recorded | 99 (0.6%) |

They are not the same thing — of the 335 late responses, 214 still closed with an
explanation, 19 with monetary relief and 3 with non-monetary relief. A reader seeing
"98.0% answered on time" beside a bar labelled "Untimely response 0.6%" would reasonably
conclude one of them was wrong.

**Fix:** the outcome category is relabelled **"No resolution recorded"** — which is what
it actually means — and the takeaway states plainly that the two are different fields and
are not averaged together.

## What is deliberately not on the dashboard

| Not shown | Why |
|---|---|
| Handling time / response-speed SLA | The available field is 0 for 96% of records — it measures the CFPB's own routing, not any firm's speed. Showing it would have been a confident, wrong ops metric |
| The most recent weeks of data | The CFPB publishes a complaint only after the firm responds or 15 days pass. Including them would have shown a 73% fall in complaints that never happened |
| Geographic breakdown | The corpus is US; Chleo's firm is EU. Charting US states would imply the data says something about her book. It does not |
| Any predicted or modelled figure | Round 1 shows what is measured. Nothing on this dashboard is an estimate |

## Design decisions

- **Palette:** a validated categorical palette — blue as the primary series, a lighter step
  of the same ramp for de-emphasis, and reserved status colours for the good/critical KPI
  tiles only. Status colours are never reused as a series colour.
- **No dual-axis charts anywhere.** Two measures of different scale become two charts.
- **Legends omitted for single-series charts**; the title names the series.
- **Direct labels, selectively** — value labels sit on bars, not on every point of the
  line chart.
- **Recessive grid and axes**; the data is the darkest thing on screen.
- **A table view** is available under "See the underlying numbers as a table", so no
  finding depends on reading a colour.
- **Hover tooltips** on every mark, giving the exact count behind any bar or point.

## Verification

The dashboard was run and visually inspected at 1440px, not merely executed without
error. Two defects were found by looking at it and fixed: the timeliness field collision
above, and an over-claim in the volume takeaway that described a 1,487–2,488 range as
"steady". Screenshots in `dashboard/screenshots/` are of the corrected build.

Reproduce every figure quoted here:

```bash
python dashboard/metrics.py
```
