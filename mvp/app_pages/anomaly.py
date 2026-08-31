"""UC-2 — the anomaly review queue.

A deterministic detector selects what is unusual; the model only writes the case note. The
queue is standing and keeps handled items, because an analyst's morning is as much about
what was already dismissed as about what is new.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp.capabilities.anomaly import RULES
from mvp.ui import queue_filters, status_chip, ladder_html, action_bar, bulk_bar

st.title("Anomaly review")
st.caption("Ranked by how far a pattern departs from that account's own normal — never by "
           "the amount. A large but ordinary payment on a wealthy account does not outrank "
           "a small impossible one on a modest account.")

items = Q.load_anomaly()
if not items:
    st.warning("The queue has not been built yet. Run `python -m mvp.build_queues`.")
    st.stop()

latest = Q.latest_by_item()
dated, as_at = Q.with_clock(items, "raised")
df = pd.DataFrame([{**it, "status": Q.status_of(it["item_id"], it, latest)} for it in dated])
st.caption(f"Batch as at **{as_at}**. Age is shown because a stale flag is a worse flag — "
           f"but no first-response target applies here: a fraud pattern is not on a "
           f"complaints deadline.")

view = queue_filters(df, extra_facets=[("rule", "Pattern"), ("country", "Country")],
                     date_col="raised")
if view.empty:
    st.info("Nothing matches those filters.")
    st.stop()

table = view[["raised", "age_days", "rule", "times_normal", "amount_eur", "txn_count",
              "status", "reason_code"]]
sel = st.dataframe(
    table, width="stretch", hide_index=True, on_select="rerun", selection_mode="multi-row",
    column_config={
        "raised": st.column_config.DateColumn("Raised", width="small"),
        "age_days": st.column_config.NumberColumn("Age", format="%d d", width="small"),
        "rule": st.column_config.TextColumn("Pattern", width="medium"),
        "times_normal": st.column_config.NumberColumn("× normal", format="%.1f×",
                                                      width="small"),
        "amount_eur": st.column_config.NumberColumn("Amount", format="€%.2f",
                                                    width="small"),
        "txn_count": st.column_config.NumberColumn("Txns", width="small"),
        "status": st.column_config.TextColumn("Status", width="small"),
        "reason_code": st.column_config.TextColumn("Why held", width="medium"),
    })

picked = sel.selection.rows
if len(picked) > 1:
    bulk_bar(view.iloc[picked], capability="anomaly", actions=Q.ANOMALY_ACTIONS)
    st.stop()
if not picked:
    st.caption(f"{len(view)} of {len(df)} candidates shown. Tick one to read the case note, or several to act together.")
    st.stop()

it = view.iloc[picked[0]].to_dict()
st.divider()

left, right = st.columns([3, 2])
with left:
    st.markdown(f"{status_chip(it['status'])} :gray-badge[{it['reason_code']}]")
    st.subheader(it["rule"].replace("_", " ").capitalize())
    st.caption(RULES.get(it["rule"], ""))
    m = st.columns(4)
    m[0].metric("Transactions", int(it["txn_count"]))
    m[1].metric("Total", f"€{it['amount_eur']:,.0f}")
    m[2].metric("Account median", f"€{it['account_median_eur']:,.0f}")
    m[3].metric("Times normal", f"{it['times_normal']:.1f}×")
    if it["explanation"]:
        st.markdown("**Case note:**")
        st.info(it["explanation"])
    if it["next_check"]:
        st.markdown(f"**Fastest check:** {it['next_check']}")

with right:
    with st.container(border=True):
        st.markdown("**Checks**")
        st.html(ladder_html(it["reason_code"]))
        conf = it["confidence"]
        st.caption(f"confidence {conf:.2f} · {it['latency_ms']} ms · {it['model']} · "
                   f"ref {it['ref']}" if pd.notna(conf) else f"ref {it['ref']}")
    st.caption(f"{it['category']} · {it['channel']} · {it['country']}")

action_bar(it, capability="anomaly", actions=Q.ANOMALY_ACTIONS,
           proposed=f"{it['rule']} — {it['times_normal']:.1f}× normal")
