# Capstone — AI Consulting Pitch (Round 1)

**Author:** Ugo Ahukannah
**Client scenario:** "Chleo", CEO of a mid-size EU financial services firm who believes
AI is not transparent and cannot say what "the AI" would be or how she would sign up.

**The pitch in one line:** start with complaint triage — the one AI use case in her
business whose reasoning you can watch happen on a screen.

---

## Status

| Round 1 deliverable | State |
|---|---|
| Sector research, opportunities/risks, 2–3 use cases | **Done** — `research/` |
| Curated public dataset | **Done** — `data/`, 16,839 records |
| Dashboard + docs | **Done** — `dashboard/`, Streamlit + Plotly, 6 metrics |
| n8n POC + docs | **Done** — `n8n/`, run on the cohort instance, both branches verified |
| LangSmith monitoring sample | **Done** — `langsmith/`, 60 traced decisions, EU workspace |
| Cost + timeline estimate | **Done** — `cost_estimation/`, model + assumptions table |
| Round 1 presentation deck | **Done** — `presentation/`, 14 slides + speaker notes |
| `round1_decision.md` | After the staff presentation — `feedback/` |

## The data

**Source:** [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)
— public API, no authentication, no personal data (narratives are scrubbed by the CFPB
before publication). Public data only, per the brief.

| File | What it is | Committed |
|---|---|---|
| `data/raw/cfpb_2026Q2.csv` | Raw pull, 36,022 narrative complaints, 62 MB | No — run `./fetch_data.sh` |
| `data/complaints_dashboard.csv` | Curated, no narratives — feeds the dashboard | Yes |
| `data/complaints_triage.csv.gz` | Curated, with narratives — feeds the classifier | Yes |

**Two corrections were applied before any analysis**, both documented in
`data_prep.py` and `research/sector_research.md`:

1. **Publication lag.** The CFPB publishes a complaint only after the company responds or
   15 days pass, so recent weeks are incomplete. Weekly volume holds at 1,700–2,270 through
   2026-06-28 then falls to 607 → 430 → 555 → 418 → 244. That cliff is an artifact, not a
   drop in complaints. The analysis window is cut at **2026-06-27**.
2. **A dead metric.** "Days to company" is 0 for 96% of records — it measures CFPB routing,
   not any firm's handling speed. Dropped rather than shown.

## Headline findings

- **16,839** complaints, **567** firms, **64** issue classes, 2026-05-01 → 2026-06-27.
- **The top 5 of 64 issue classes carry 46.1% of volume** — a classifier needs to be good
  at five things and honest about the rest.
- Credit card complaints close with monetary relief **17.2%** of the time vs **3.0%** for
  vehicle lending. Routing has money attached to it.
- Median narrative **1,201 characters** (90th pct 3,013) — the actual human workload.
- Timely response **98.0%**, any relief **19.7%**, monetary relief **12.7%**.

## Setup

```bash
conda activate bootcamp-env        # pandas 3.0.3, Python 3.12
./fetch_data.sh                    # ~62 MB from the CFPB public API
python data_prep.py                # rebuilds both curated files + prints all figures
```

`.env.example` lists the keys needed later for the POC and monitoring. Copy it to
`.env.local` and fill it in. Never commit real values.

## Structure

```
research/           sector_research.md · opportunities_risks.md · use_cases.md
data/               curated slices (raw/ is gitignored, reproducible)
dashboard/          app.py · metrics.py (single source of truth) · docs · screenshots
n8n/                POC workflow export + documentation
langsmith/          traced experiment, export, monitoring notes, screenshots
classifier/         prompt, taxonomy, team map, decision codes, FINDINGS.md
cost_estimation/    cost_model.py (all figures derived) + analysis + timeline
feedback/           round1_decision.md — KEEP or CHANGE, after the staff presentation
presentation/       round1_pitch.pptx + .pdf + speaker_notes.md
data_prep.py        curation, with both data-quality corrections
fetch_data.sh       re-download the raw pull
PLAN.md             locked decisions, rubric weights, open questions
```

## The dashboard

```bash
conda activate bootcamp-env
streamlit run dashboard/app.py
```

Python (Streamlit + Plotly) — confirmed with the instructor as an accepted option
alongside Tableau and PowerBI. Chosen because the Round 2 MVP is a Python application,
so this dashboard becomes the shell the classifier plugs into rather than a dead end.
Every figure comes from `dashboard/metrics.py`, so the numbers here and the numbers in
the research docs cannot drift apart.

Six metrics, each justified by the decision it supports, in
`dashboard/dashboard_documentation.md`. Screenshots in `dashboard/screenshots/`.

## What this pitch deliberately refuses to propose

A customer-facing chatbot, and credit scoring. The first fails in public in the customer's
voice; the second is Annex III high-risk under the EU AI Act. Both are named in
`research/use_cases.md` with the reasoning — telling a sceptical CEO what *not* to buy is
the fastest way to earn the meeting.
