"""UC-1 — the complaint triage queue.

A standing work list, not a form. The AI has been through the batch before anyone opens
the page, so work is already sorted when a handler arrives, and handled items stay visible
afterwards rather than vanishing — an inbox that empties tells you nothing about what was
decided this morning.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp.ui import queue_filters, status_chip, ladder_html, action_bar, bulk_bar

st.title("Complaint triage")
st.caption("Every complaint in today's batch, already read. It proposes a team and must "
           "quote the sentence that decided it — a guard checks that sentence is really "
           "in the complaint.")

items = Q.load_triage()
if not items:
    st.warning("The queue has not been built yet. Run `python -m mvp.build_queues`.")
    st.stop()

latest = Q.latest_by_item()
rows = []
for it in items:
    rows.append({**it, "status": Q.status_of(it["item_id"], it, latest)})
df = pd.DataFrame(rows)

view = queue_filters(df, extra_facets=[("product", "Product"),
                                       ("proposed_team", "Proposed team")])
if view.empty:
    st.info("Nothing matches those filters.")
    st.stop()

table = view[["received", "product", "proposed_team", "confidence", "status", "reason_code"]]
sel = st.dataframe(
    table, width="stretch", hide_index=True, on_select="rerun", selection_mode="multi-row",
    column_config={
        "received": st.column_config.DateColumn("Received", width="small"),
        "product": st.column_config.TextColumn("Product", width="medium"),
        "proposed_team": st.column_config.TextColumn("Proposed team", width="medium"),
        "confidence": st.column_config.ProgressColumn(
            "Confidence", min_value=0, max_value=1, format="%.2f", width="small"),
        "status": st.column_config.TextColumn("Status", width="small"),
        "reason_code": st.column_config.TextColumn("Why held", width="medium"),
    })

picked = sel.selection.rows
if len(picked) > 1:
    bulk_bar(view.iloc[picked], capability="triage", actions=Q.TRIAGE_ACTIONS)
    st.stop()
if not picked:
    st.caption(f"{len(view)} of {len(df)} complaints shown. Tick one to read it, or several to act on them together.")
    st.stop()

it = view.iloc[picked[0]].to_dict()
st.divider()

left, right = st.columns([3, 2])
with left:
    st.markdown(f"{status_chip(it['status'])} :gray-badge[{it['reason_code']}]")
    st.subheader(f"Route to {it['proposed_team']}"
                 if it["proposed_queue"] else "No team proposed")
    if it["proposed_queue"]:
        st.caption(f"Queue: {it['proposed_queue']}")
    st.caption(it["reason"])
    if it["evidence"]:
        st.markdown("**Because the customer wrote:**")
        st.info(f"“{it['evidence']}”")
    with st.expander("The full complaint"):
        st.write(it["narrative"])

with right:
    with st.container(border=True):
        st.markdown("**Checks**")
        st.html(ladder_html(it["reason_code"]))
        st.caption(f"confidence {it['confidence']:.2f} · {it['latency_ms']} ms · "
                   f"{it['model']} · ref {it['ref']}")

action_bar(it, capability="triage", actions=Q.TRIAGE_ACTIONS,
           proposed=f"{it['proposed_team']} — {it['proposed_queue']}")
