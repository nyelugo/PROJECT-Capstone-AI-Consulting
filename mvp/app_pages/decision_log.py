"""The audit record — what was proposed, beside what the person did about it."""
import pandas as pd
import streamlit as st

st.title("Decision log")
st.caption("A proposal with no human action beside it is not a decision. This pairing is "
           "the audit record.")

log = st.session_state.get("log", [])
if not log:
    st.info("Nothing yet. Run something on one of the Assist pages.")
    st.stop()

df = pd.DataFrame(log)
agreed = sum(1 for r in log if r["human"].startswith("accepted"))
m = st.columns(3)
m[0].metric("Decisions recorded", len(df))
m[1].metric("Accepted by the handler", agreed)
m[2].metric("Overridden", len(df) - agreed)

st.dataframe(df, width="stretch", hide_index=True)
st.caption("In production this is the number that matters: not whether the model was "
           "right, but how often a handler agreed with it. An acceptance rate near 100% "
           "is a warning, not a success — it means people have stopped reading.")
