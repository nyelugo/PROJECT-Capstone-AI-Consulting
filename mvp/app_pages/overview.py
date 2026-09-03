"""Chleo's page. She opens it weekly, so it answers one question: was this a normal week?

Deliberately NOT the Round 1 dashboard, and deliberately not the ops lead's page either.
Chleo supervises; she does not work the queue. Everything here describes the system's own
behaviour, which is true whether the complaints came from her intake or a public corpus —
and that is why it can be honest before Phase 0 has bought any of her data.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp import runtime as R

ROI = Path(__file__).resolve().parents[2] / "cost_estimation" / "roi_model.json"

st.title("Overview")

tri_items, ano_items = Q.load_triage(), Q.load_anomaly()
if not tri_items and not ano_items:
    st.warning("No queues built yet. Run `python -m mvp.build_queues`.")
    st.stop()

tri, ano = Q.summary(tri_items), Q.summary(ano_items)
tri_dated, tri_as_at = Q.with_clock(tri_items, "received")
weeks = Q.by_week(tri_items, "received")
wow = Q.week_on_week(weeks)
latest = Q.latest_by_item()

# A percentage over a handful of decisions is not a measurement. One threshold,
# used by both the weekly figure and the headline rate.
MIN_SAMPLE = 20

# ------------------------------------------------------------------- was it a normal week
st.subheader("Was this a normal week")
if wow:
    cur, prev = wow["current"], wow["previous"]
    c = st.columns(4)
    c[0].metric("Week", cur["week"])
    c[1].metric("Complaints in", cur["items"], f"{wow['items_delta']:+d} on last week")
    c[2].metric("Held for a person", f"{cur['held_pct']:.0f}%",
                f"{wow['held_pct_delta']:+.0f} pts", delta_color="inverse")
    wk_decided = cur.get("agreed", 0) + cur.get("disagreed", 0)
    c[3].metric("Agreement",
                f"{cur['agreement_pct']:.0f}%" if wk_decided >= MIN_SAMPLE else "Not yet",
                f"{wk_decided} of {MIN_SAMPLE} decisions" if wk_decided < MIN_SAMPLE else None,
                delta_color="off",
                help="Only over items a person decided this week, and only once there are "
                     f"{MIN_SAMPLE} of them. A rate over three decisions is not a rate.")
    st.caption(f"Against **{prev['week']}**: {prev['items']} complaints, "
               f"{prev['held_pct']:.0f}% held. Nine weeks of receipts are in this batch, so "
               f"the comparison is measured, not modelled — but no NEW work arrives, which "
               f"is what the Phase 2 feed adds.")
else:
    st.info("Not enough weeks in the batch to compare.", icon=":material/hourglass_empty:")

wf = pd.DataFrame(weeks)
if weeks:
    st.dataframe(wf[["week", "items", "held", "held_pct", "decided"]], width="stretch",
                 hide_index=True,
                 column_config={
                     "week": st.column_config.TextColumn("Week", width="small"),
                     "items": st.column_config.BarChartColumn("Complaints in", y_min=0,
                                                              y_max=int(wf["items"].max())),
                     "held": st.column_config.NumberColumn("Held", width="small"),
                     "held_pct": st.column_config.ProgressColumn("Held %", min_value=0,
                                                                 max_value=100, format="%.0f%%"),
                     "decided": st.column_config.NumberColumn("Decided by a person",
                                                              width="small")})

# ------------------------------------------------------------------------- did it work
st.subheader("Did it work")
total = tri["total"] + ano["total"]
held = tri["held"] + ano["held"]
pending = tri["pending"] + ano["pending"]
pct = lambda n, d: f"{100 * n / d:.0f}%" if d else "—"

c = st.columns(4)
c[0].metric("Items read", total, f"{tri['total']} complaints · {ano['total']} patterns",
            delta_color="off")
c[1].metric("It proposed on", pct(total - held, total), f"{total - held} of {total}",
            delta_color="off")
c[2].metric("It held back on", pct(held, total), f"{held} of {total}", delta_color="off",
            help="The system declined to propose. A correct outcome, not a failure.")
c[3].metric("Reached a customer", "0", "by design, not by luck", delta_color="off",
            help="No capability can contact a customer, route a case or move money. "
                 "Every path ends at a person pressing something.")

reasons = {**{f"triage · {k}": v for k, v in tri["by_reason"].items()},
           **{f"anomaly · {k}": v for k, v in ano["by_reason"].items()}}
if reasons:
    with st.container(border=True):
        st.markdown("**Why it held back** — every refusal carries a code, never a shrug")
        hd = pd.DataFrame({"reason": list(reasons), "items": list(reasons.values())})
        hd["share"] = hd["items"].map(lambda n: f"{100 * n / total:.1f}%")
        st.dataframe(hd.sort_values("items", ascending=False), width="stretch",
                     hide_index=True)

# ------------------------------------------------------------------------- agreement
st.subheader("Do your people agree with it")
agreed, disagreed = tri["agreed"] + ano["agreed"], tri["disagreed"] + ano["disagreed"]
decided = agreed + disagreed
rate = 100 * agreed / decided if decided else None
c = st.columns(3)
enough = rate is not None and decided >= MIN_SAMPLE
c[0].metric("Agreement rate",
            f"{rate:.0f}%" if enough else "Insufficient sample",
            None if enough else f"{decided} of {MIN_SAMPLE} decisions",
            delta_color="off",
            help="Measured only over items a person actually decided on, and only once "
                 f"there are {MIN_SAMPLE} of them. Counting untouched rows as agreement "
                 "would make an unattended queue look like a triumph.")
c[1].metric("Agreed", agreed)
c[2].metric("Overridden", disagreed,
            help="The most valuable rows in the system — where it was wrong and a person "
                 "caught it. Broken down by team on the Operations page.")

if rate is None:
    st.info("No decisions recorded yet.", icon=":material/hourglass_empty:")
elif decided < MIN_SAMPLE:
    st.info(f"{decided} of {MIN_SAMPLE} decisions needed before this rate means anything.",
            icon=":material/hourglass_empty:")
elif rate > 97 and decided >= MIN_SAMPLE:
    st.warning("Above 97%. A warning, not a success — it usually means people have stopped "
               "reading. See acceptance per handler on the Operations page.",
               icon=":material/warning:")
elif rate < 75 and decided >= MIN_SAMPLE:
    st.warning("Below 75%. It is being overridden more than it is trusted.",
               icon=":material/warning:")

# ----------------------------------------------------------- cost, and what is running
st.subheader("What it cost, and what is running")
try:
    roi = json.loads(ROI.read_text())
    A = roi["assumptions"]
    p_in, p_out, eur = (A["price_in_per_1m_usd"]["value"], A["price_out_per_1m_usd"]["value"],
                        A["usd_eur"]["value"])
    spend = lambda n, i, o: n * (i / 1e6 * p_in + o / 1e6 * p_out) * eur
    batch = (spend(tri["total"], 684, 49)
             + spend(ano["total"], A["anomaly_tokens_in"]["value"],
                     A["anomaly_tokens_out"]["value"]))
    annual, ai_share = roi["annual_running_cost_total_eur"], roi["ai_share_of_running_cost_pct"]
except (OSError, KeyError, json.JSONDecodeError):
    batch = annual = ai_share = None

c = st.columns(3)
c[0].metric("This batch cost", f"€{batch:.4f}" if batch is not None else "—",
            f"{total} items", delta_color="off")
c[1].metric("Running cost a year", f"€{annual:,}" if annual else "—",
            "at the modelled volume", delta_color="off")
ai_year = None
try:
    ai_year = sum(v for k, v in roi["annual_running_cost_eur"].items() if "Model calls" in k)
except (TypeError, KeyError):
    pass
if ai_share is None:
    share, sub = "—", "the rest is platform and oversight"
elif ai_share < 0.01:
    share = "<0.01%"
    sub = (f"€{ai_year:.2f} a year — the rest is platform and oversight"
           if ai_year is not None else "the rest is platform and oversight")
else:
    share, sub = f"{ai_share:.1f}%", "the rest is platform and oversight"
c[2].metric("Of which is the AI", share, sub, delta_color="off",
            help="Model calls only. Rounding it to 0.000% next to a real batch cost read as "
                 "a contradiction; it is small, not absent.")

st.markdown("**Switch a capability off**")
st.caption("Takes effect immediately, for everyone, and is written to the decision log. "
           "You do not need anyone's help to do this.")
settings = Q.settings()
cols = st.columns(len(Q.CAPABILITIES))
for col, (key, label) in zip(cols, Q.CAPABILITIES.items()):
    on = col.toggle(label, value=settings[key], key=f"cap_{key}")
    if on != settings[key]:
        Q.set_capability(key, on, by=st.session_state.get("operator", "unknown"))
        st.rerun()

a, b = st.columns(2)
a.markdown(f"Model — {':green-badge[configured]' if R.env('OPENAI_API_KEY') else ':red-badge[missing]'}")
b.markdown(f"Monitoring — {':green-badge[receiving]' if R.env('LANGSMITH_API_KEY') else ':orange-badge[not configured]'}")

st.divider()
st.caption(
    "**Two honest limits.** Sign-in is a name typed into a box — it records who *said* they "
    "decided, not who did; real identity arrives with the case-system integration in Phase "
    "2. And this is demo data: triage and the reporting figures both run on the public "
    "CFPB corpus, anomaly review on synthetic transactions. Phase 0 replaces them with "
    "your own.")
