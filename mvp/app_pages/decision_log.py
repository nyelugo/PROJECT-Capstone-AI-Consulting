"""The audit record — one row per human action, in order.

Different grain from the queues on purpose. A queue answers "what is the state of this
item" and shows it once. The log answers "what happened, and in what order" — so an item
someone revisited appears twice. Append-only; nothing here is ever edited.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q

st.title("Decision log")
st.caption("Every proposal beside the human action taken on it. This pairing is the audit "
           "record — a proposal with nobody's decision next to it is a suggestion nobody owns.")

events = Q.events()
if not events:
    st.info("Nothing recorded yet. Act on an item in either queue and it appears here.")
    st.stop()

df = pd.DataFrame(events).sort_values("at", ascending=False)

with st.container(border=True):
    c = st.columns([1, 1, 1, 1.5])
    caps = c[0].multiselect("Capability", sorted(df["capability"].unique()))
    acts = c[1].multiselect("Action", sorted(df["action"].unique()))
    who = c[2].multiselect("By", sorted(df["by"].unique()))
    term = c[3].text_input("Search", "", placeholder="text in any field")

view = df
if caps:
    view = view[view["capability"].isin(caps)]
if acts:
    view = view[view["action"].isin(acts)]
if who:
    view = view[view["by"].isin(who)]
if term:
    view = view[view.astype(str).agg(" ".join, axis=1).str.lower().str.contains(
        term.lower(), regex=False)]

m = st.columns(3)
m[0].metric("Actions recorded", len(view))
m[1].metric("Items touched", view["item_id"].nunique())
revisited = int((view.groupby("item_id").size() > 1).sum())
m[2].metric("Items revisited", revisited,
            help="Someone changed their mind. Both decisions are kept.")

st.dataframe(view[["at", "capability", "item_id", "proposed", "reason_code", "action", "by"]],
             width="stretch", hide_index=True,
             column_config={
                 "at": st.column_config.TextColumn("When", width="small"),
                 "capability": st.column_config.TextColumn("Capability", width="small"),
                 "item_id": st.column_config.TextColumn("Item", width="small"),
                 "proposed": st.column_config.TextColumn("What it proposed", width="large"),
                 "reason_code": st.column_config.TextColumn("Reason code", width="medium"),
                 "action": st.column_config.TextColumn("Human action", width="small"),
                 "by": st.column_config.TextColumn("By", width="small"),
             })

st.download_button("Export as CSV", view.to_csv(index=False).encode(),
                   "decision_log.csv", "text/csv", icon=":material/download:")
