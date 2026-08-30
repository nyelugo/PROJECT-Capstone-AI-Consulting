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
| `round1_decision.md` | **Scaffolded** — `feedback/`, filled in after the staff presentation |

## What each part does

`STACK.md` is the high-level map: what each of the seven elements is for, how a complaint
moves through them, why there are two LangSmith artifacts, and where the honest limits are.

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

**And the finding the whole pitch rests on:** the classifier reaches **60.5% agreement**
with the CFPB team labels — **agreement, not accuracy**. Asked the same complaint twice it
answers the same way ~9 times in 10, so it is consistent; it simply disagrees with a label
the *complainant* chose from a dropdown. That label is not expert routing ground truth, so
no accuracy figure exists for this system yet. Creating one is what Phase 0 buys. See
`classifier/FINDINGS.md`.

## Running the dashboard

**For presenting — silent launch, no terminal window:**

```bash
./make_desktop_app.sh          # once; builds "Capstone Dashboard.app" on the Desktop
```

Double-click the app. It starts the dashboard in the background, opens
`http://localhost:8501`, and shows nothing else. A second double-click while it is already
running just reopens the tab. Failures appear as a macOS dialog rather than silence.

A `.command` file cannot do this — macOS always opens Terminal to run one — which is why
the presenting launcher is an `.app` bundle.

**For development — visible logs:**

```bash
./run_dashboard.command        # macOS, or run_dashboard.bat on Windows
# or
conda activate bootcamp-env && streamlit run dashboard/app.py
```

To stop it: `pkill -f "streamlit run dashboard/app.py"`.

## Reproducing the numbers

`evidence_walkthrough.ipynb` recomputes every figure quoted in the pitch from the
committed evidence files and reconciles them against what the deck states. It makes **no
API calls and needs no keys**, so it costs nothing to run.

```bash
conda activate bootcamp-env
jupyter lab evidence_walkthrough.ipynb      # Kernel -> Restart & Run All
```

The last table is the point: 18 figures, computed here versus stated in the deck, with a
MISMATCH flag. It currently reports 0. If a figure ever drifts, that table says so before
a grader does.

It is **not** the live demo — the demo is the Streamlit dashboard plus the n8n and
LangSmith tabs, listed in the notebook's final section.

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
cost_estimation/    cost_model.py (all figures derived) + analysis + timeline + assumptions table
feedback/           round1_decision.md — KEEP or CHANGE, completed after the presentation
presentation/       round1_pitch.pptx + .pdf + speaker_notes.md
evidence_walkthrough.ipynb   recomputes and reconciles every figure in the pitch
data_prep.py        curation, with both data-quality corrections
fetch_data.sh       re-download the raw pull
PLAN.md             locked decisions, rubric weights, open questions
```

## LangSmith monitoring

Experiment `triage-round1-ebb7facb` on the **EU** workspace, 60 traced decisions.
[Dataset](https://eu.smith.langchain.com/o/bdd29afc-aefb-432d-a118-2ee71dc41429/datasets/074b52a4-d07a-46e6-9b10-7aac69b24c79)
· [Experiment](https://eu.smith.langchain.com/o/bdd29afc-aefb-432d-a118-2ee71dc41429/datasets/074b52a4-d07a-46e6-9b10-7aac69b24c79/compare?selectedSessions=148f16a5-714e-42c0-ac94-c37c61f1ca65)

There are two LangSmith artifacts and they live in different places: the **evaluation**
(`triage-round1-ebb7facb`) under Datasets & Experiments, and a **tracing project**
(`capstone-triage-live`) under Tracing, which is what the Monitoring tab charts. See
`langsmith/monitoring_notes.md`.

Both links need workspace access. `langsmith/traces_export.json` and
`langsmith/experiment_summary.json` carry the same records with no login required, and
`langsmith/screenshots/` shows the trace view.

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
