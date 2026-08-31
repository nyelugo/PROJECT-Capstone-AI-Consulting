# Capstone Plan — AI Consulting Pitch

Author: Ugo Ahukannah

## Locked scenario (Week 8 Day 3)

| Field | Value |
|---|---|
| Sector | Financial services |
| Company size | Mid-size |
| Client persona | "Chleo", CEO — afraid of AI, believes it is not transparent, keeps asking *what "the AI" is* and *how they would sign up* |

Sector and size are a starting point. They may change after the Round 1
presentation to teaching staff; that is explicitly allowed and unpenalised.

## Round 1 — required artifacts (100 pts)

| # | Artifact | Where | Rubric weight |
|---|---|---|---|
| 1 | Sector research, opportunities/risks, 2–3 use cases | `research/` | 20 |
| 2 | Dashboard (**Python** — Streamlit + Plotly), 6 stakeholder metrics + docs | `dashboard/` | 25 |
| 3 | n8n POC + docs, and LangSmith monitoring sample | `n8n/`, `langsmith/` | 25 |
| 4 | Cost + timeline estimate with assumptions table | `cost_estimation/` | 15 |
| 5 | Presentation to teaching staff + `round1_decision.md` | `presentation/`, `feedback/` | 15 |

## Round 2 — required artifacts (100 pts)

use_case_definition.md · stronger POC + 2–5 min demo · roi_risk_assessment.md
(12/36-mo ROI, break-even, >=6 risks) · eu_ai_act_compliance.md · gdpr_documentation.md
· strategic_plan.md · presentation.pdf · **working MVP** + mvp_documentation.md

Weights: ROI/risk 20 · EU AI Act 20 · use case+POC 15 · MVP 15 · GDPR 10 · strategy 10 · presentation 10

## Standing constraints from the brief

- Public or synthetic data only. No real personal data.
- A small MVP that runs scores above an ambitious one that does not.
- Compliance *reasoning* scores; a bare risk-class label does not.
- Campus identifiers: Round 1 -> `project-5`, Round 2 -> `final-project`.

## Locked decisions

| Decision | Value | Where argued |
|---|---|---|
| Use cases | UC-1 complaint triage · UC-2 anomaly flagging · UC-3 reporting assistance | `research/use_cases.md` |
| Dataset | CFPB Consumer Complaint Database, public API, 16,839 curated records | `research/sector_research.md` |
| MVP capability | UC-1 (triage) must run end to end. Staff recommended all 3 use cases; built on one shared spine, riskiest last — see `feedback/round1_decision.md` | `research/use_cases.md` |
| BI tool | **Python** (Streamlit + Plotly) | `dashboard/dashboard_documentation.md` |

**Python instead of PowerBI/Tableau.** Confirmed with the instructor that Python is an
accepted option. Chosen so the Round 1 dashboard becomes the shell the Round 2 MVP plugs
into, and so dashboard figures and document figures share one module.

## Open decisions

