"""UC-2 — the anomaly review queue.

A deterministic detector selects what is unusual; the model only writes the case note. The
queue is standing and keeps handled items, because an analyst's morning is as much about
what was already dismissed as about what is new.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp.capabilities.anomaly import RULES, transactions_for
from mvp.ui import (queue_filters, status_chip, ladder_html, action_bar, bulk_bar,
                    conf_txt)

st.title("Anomaly review")
st.caption("Ranked by how far a pattern departs from that account's own normal — never by "
           "the amount. A large but ordinary payment on a wealthy account does not outrank "
           "a small impossible one on a modest account.")

# An off switch is only real if the page honours it. Chleo can disable this from Overview
# and it takes effect for everyone immediately, without a restart or a developer.
if not Q.is_on("anomaly"):
    st.warning("**Anomaly review is switched off.** Turn it back on from Overview.",
               icon=":material/toggle_off:")
    st.stop()

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
    # The aggregate is the claim; these are the rows it was made from. An analyst who cannot
    # see the transactions is being asked to take the case note on trust.
    txns = transactions_for(it["item_id"])
    noun = "transaction" if len(txns) == 1 else "transactions"
    with st.expander(f"The {len(txns)} {noun} behind this", expanded=True):
        if txns.empty:
            st.caption("No rows found for this candidate in the current batch.")
        else:
            show = txns.assign(date=txns["date"].dt.strftime("%Y-%m-%d %H:%M"))
            cols = [c for c in ["date", "amount_eur", "category", "channel", "country",
                                "device_new", "txn_id"] if c in show.columns]
            st.dataframe(show[cols], width="stretch", hide_index=True,
                         column_config={
                             "date": st.column_config.TextColumn("When", width="small"),
                             "amount_eur": st.column_config.NumberColumn("Amount", format="€%.2f"),
                             "category": st.column_config.TextColumn("Category"),
                             "channel": st.column_config.TextColumn("Channel", width="small"),
                             "country": st.column_config.TextColumn("Country", width="small"),
                             "device_new": st.column_config.CheckboxColumn("New device", width="small"),
                             "txn_id": st.column_config.TextColumn("Transaction", width="small"),
                         })
            st.caption(f"Account median €{it['account_median_eur']:,.2f} — these total "
                       f"€{txns['amount_eur'].sum():,.2f}, {it['times_normal']:.1f}× that median.")

    if it["explanation"]:
        st.markdown("**Case note:**")
        st.info(it["explanation"])
    if it["next_check"]:
        st.markdown(f"**Fastest check:** {it['next_check']}")

with right:
    with st.container(border=True):
        st.markdown("**Checks**")
        st.html(ladder_html(it["reason_code"]))
        st.caption(f"confidence {conf_txt(it['confidence'])} · {it['latency_ms']} ms · "
                   f"{it['model']} · ref {it['ref']}")
    st.caption(f"{it['category']} · {it['channel']} · {it['country']}")

action_bar(it, capability="anomaly", actions=Q.ANOMALY_ACTIONS,
           proposed=f"{it['rule']} — {it['times_normal']:.1f}× normal")
