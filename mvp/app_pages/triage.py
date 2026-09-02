"""UC-1 — the complaint triage queue.

A standing work list, not a form. The AI has been through the batch before anyone opens
the page, so work is already sorted when a handler arrives, and handled items stay visible
afterwards rather than vanishing — an inbox that empties tells you nothing about what was
decided this morning.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp.ui import (queue_filters, status_chip, sla_chip, ladder_html,
                    action_bar, bulk_bar, conf_txt)

st.title("Complaint triage")
st.caption("Every complaint in today's batch, already read. It proposes a team and must "
           "quote the sentence that decided it — a guard checks that sentence is really "
           "in the complaint.")

# An off switch is only real if the page honours it. Chleo can disable this from Overview
# and it takes effect for everyone immediately, without a restart or a developer.
if not Q.is_on("triage"):
    st.warning("**Complaint triage is switched off.** Turn it back on from Overview.",
               icon=":material/toggle_off:")
    st.stop()

items = Q.load_triage()
if not items:
    st.warning("The queue has not been built yet. Run `python -m mvp.build_queues`.")
    st.stop()

latest = Q.latest_by_item()
dated, as_at = Q.with_clock(items, "received")
df = pd.DataFrame([{**it, "status": Q.status_of(it["item_id"], it, latest)} for it in dated])

breached = int((df["sla"] == Q.BREACHED).sum())
due = int((df["sla"] == Q.DUE_SOON).sum())
c1, c2, c3 = st.columns(3)
c1.metric("Queue as at", as_at)
c2.metric("Past the target", breached, help=f"Older than {Q.SLA_DAYS} days")
c3.metric("Due within 5 days", due)
st.caption(f"Target is **{Q.SLA_DAYS} days** to first response — an assumption; your own "
           f"target is set in Phase 0. This batch is a historical sample spanning "
           f"{int(df['age_days'].max())} days of intake, so a large share of it reads as "
           f"past target. That is the sample's spread, not an operational failure.")

view = queue_filters(df, extra_facets=[("product", "Product"),
                                       ("proposed_team", "Proposed team"),
                                       ("sla", "Deadline")])
if view.empty:
    st.info("Nothing matches those filters.")
    st.stop()

table = view[["received", "age_days", "days_left", "sla", "product", "proposed_team",
              "confidence", "status", "reason_code"]]
sel = st.dataframe(
    table, width="stretch", hide_index=True, on_select="rerun", selection_mode="multi-row",
    column_config={
        "received": st.column_config.DateColumn("Received", width="small"),
        "age_days": st.column_config.NumberColumn("Age", format="%d d", width="small"),
        "days_left": st.column_config.NumberColumn("Left", format="%d d", width="small",
                                                   help="Days to the first-response target"),
        "sla": st.column_config.TextColumn("Deadline", width="small"),
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
    st.markdown(f"{status_chip(it['status'])} {sla_chip(it['sla'], it['days_left'])} "
                f":gray-badge[{it['reason_code']}]")
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
        st.caption(f"confidence {conf_txt(it['confidence'])} · {it['latency_ms']} ms · "
                   f"{it['model']} · ref {it['ref']}")

action_bar(it, capability="triage", actions=Q.TRIAGE_ACTIONS,
           proposed=f"{it['proposed_team']} — {it['proposed_queue']}")
