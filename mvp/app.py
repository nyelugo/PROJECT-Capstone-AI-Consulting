"""Assist — the MVP. One application, one decision spine, a person in every loop.

Run:  streamlit run mvp/app.py

This is Chleo's product, and only her product. The Round 1 dashboard is deliberately NOT
in here: it sized an opportunity from public data for a pitch, which is a different job for
a different audience, and a page needing a label telling you which part to ignore belongs
somewhere else. It stays at `dashboard/app.py`, runs standalone, and is shown from the deck.

Overview is therefore an operations view — what the system proposed and what her people did
about it. Every figure on it describes the system's own behaviour, which is true whether the
complaints came from her intake or a public corpus. That is why it can be honest today,
before Phase 0 has bought any of her data.

Triage and anomaly review are standing work queues rather than forms. Work is already sorted
when she arrives, handled items stay visible afterwards, and every human action is appended
to one event log that the queues project and the Decision log page reads in full.
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
        st.Page("app_pages/overview.py", title="Overview",
                icon=":material/insights:", default=True),
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
    # Every recorded action carries a name. An audit record that cannot say who decided is
    # not an audit record — it is a list.
    st.text_input("Signed in as", key="operator", value=st.session_state.get(
        "operator", "U. Ahukannah"), help="Recorded against every decision you take.")
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
