"""Assist — the MVP. One application, one decision spine, a person in every loop.

Run:  streamlit run mvp/app.py

Why the Round 1 dashboard is a page in here rather than a second app on a second port.
Two ports is a seam the audience sees, and it quietly contradicts the thing the deck
claims: that this is one system. Chleo would never experience it as two products, so the
demo should not either.

What must survive that merge is the distinction the dashboard exists to make. It has NO
model in it — the figures are arithmetic over public data. Navigation is a flat list of
five, so that distinction is carried on the Overview page itself rather than by a section
heading, where it cannot be scrolled past or lost in a redesign.

`dashboard/app.py` is reused, not copied, and still runs standalone as the Round 1
deliverable it is.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Assist", page_icon=":material/shield_person:",
                   layout="wide", initial_sidebar_state="expanded")

from mvp import runtime as R                                    # noqa: E402
from mvp.ui import init_state                                   # noqa: E402
import mvp.capabilities.triage                                  # noqa: E402,F401  (sets sys.path for classifier/, dashboard/)

# Tells dashboard/app.py it is running as a page here, so it skips its own
# set_page_config. Set before st.navigation so it is in place when the page runs.
st.session_state["_shell"] = True
init_state()

nav = st.navigation(
    [
        st.Page("../dashboard/app.py", title="Overview",
                icon=":material/insights:", url_path="overview", default=True),
        st.Page("app_pages/triage.py", title="Complaint triage",
                icon=":material/alt_route:"),
        st.Page("app_pages/anomaly.py", title="Anomaly review",
                icon=":material/travel_explore:"),
        st.Page("app_pages/reporting.py", title="Reporting assistance",
                icon=":material/description:"),
        st.Page("app_pages/decision_log.py", title="Decision log",
                icon=":material/history:"),
    ],
    position="sidebar",
)

with st.sidebar:
    st.divider()
    ok_model = R.env("OPENAI_API_KEY") is not None
    st.caption(
        f"{':green-badge[model]' if ok_model else ':red-badge[model]'} "
        f"{':green-badge[monitoring]' if R.env('LANGSMITH_API_KEY') else ':orange-badge[monitoring]'}")
    if not ok_model:
        st.error("OPENAI_API_KEY is not set. Add it to ~/.config/ironhack/.env.local, "
                 "then reload. The overview still works; the three Assist pages do not.")
    st.caption("It proposes. You decide. Triage, anomaly review and reporting "
               "all run the same six checks — only the evidence changes.")

nav.run()
