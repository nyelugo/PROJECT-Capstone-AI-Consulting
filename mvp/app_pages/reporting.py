"""UC-3 — draft report prose, grounded in figures this system computed."""
import streamlit as st

from mvp.capabilities.reporting import Reporting, SECTIONS
from mvp.ui import fire, show, model_ready

st.title("Draft a report section")
st.caption("It may only use figures this system computed. Every number in the draft is "
           "checked against them, so an invented figure never reaches you.")

with st.form("report"):
    c1, c2 = st.columns(2)
    section = c1.selectbox("Section", list(SECTIONS))
    audience = c2.text_input("Audience", "the board risk committee")
    st.caption(f"Covers: {SECTIONS[section]['brief']}")
    go = st.form_submit_button("Draft it", type="primary", disabled=not model_ready(),
                               icon=":material/description:")

if go:
    fire(Reporting(), {"section": section, "audience": audience}, "report")

show("report", accept_label="Accept into the report", review_label="Reject the draft")
