"""Chleo's page. What the system did, and what her people did with it.

Deliberately NOT the Round 1 dashboard. That sized an opportunity from public data for a
pitch; this reports an operation. Every figure here describes the system's own behaviour,
which is true whether the complaints came from her intake or a public corpus — and that is
exactly why it can be honest before Phase 0 has bought any of her data.
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
ano_dated, ano_as_at = Q.with_clock(ano_items, "raised")
events = Q.events()
latest = Q.latest_by_item()

oldest = max((d["age_days"] for d in tri_dated if d["age_days"] is not None), default=0)
st.caption(f"One batch, received **{tri_as_at}** and back {oldest} days. Not a rolling "
           f"period — a rolling view arrives with the case-system integration in Phase 2, "
           f"and every figure below is over this batch only.")

# ------------------------------------------------------------- what needs her today
breached_open = [d for d in tri_dated
                 if d["sla"] == Q.BREACHED
                 and Q.status_of(d["item_id"], d, latest) in Q.PENDING_STATUSES]
held_open = [d for d in tri_dated + ano_dated
             if d.get("decision") != "PROPOSE_TO_HANDLER"
             and Q.status_of(d["item_id"], d, latest) in Q.PENDING_STATUSES]

if breached_open:
    st.error(f"**{len(breached_open)} complaints are past the first-response target and "
             f"nobody has worked them.** Oldest is "
             f"{max(d['age_days'] for d in breached_open)} days. Start there.",
             icon=":material/priority_high:")
elif held_open:
    st.warning(f"**{len(held_open)} items the system would not propose on** are waiting for "
               f"a person. That is the queue it cannot clear for you.",
               icon=":material/pending_actions:")
else:
    st.success("Nothing is past target and nothing is waiting on a decision.",
               icon=":material/check_circle:")

# ------------------------------------------------------------------------ did it work
st.subheader("Did it work")
total = tri["total"] + ano["total"]
held = tri["held"] + ano["held"]
pending = tri["pending"] + ano["pending"]


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "—"


c = st.columns(4)
c[0].metric("Items read", total, f"{tri['total']} complaints · {ano['total']} patterns",
            delta_color="off")
c[1].metric("It proposed on", f"{pct(total - held, total)}",
            f"{total - held} of {total}", delta_color="off")
c[2].metric("It held back on", f"{pct(held, total)}", f"{held} of {total}",
            delta_color="off",
            help="The system declined to propose. A correct outcome, not a failure.")
c[3].metric("Still waiting on a person", f"{pct(pending, total)}",
            f"{total - pending} of {total} handled", delta_color="off",
            help="This is a fixed demo batch nobody has worked through, not a backlog.")

reasons = {**{f"triage · {k}": v for k, v in tri["by_reason"].items()},
           **{f"anomaly · {k}": v for k, v in ano["by_reason"].items()}}
if reasons:
    with st.container(border=True):
        st.markdown("**Why it held back** — every refusal carries a code, never a shrug")
        hd = pd.DataFrame({"reason": list(reasons), "items": list(reasons.values())})
        hd["share of all items"] = hd["items"].map(lambda n: f"{100 * n / total:.1f}%")
        st.dataframe(hd.sort_values("items", ascending=False), width="stretch",
                     hide_index=True,
                     column_config={"reason": st.column_config.TextColumn("Reason", width="large"),
                                    "items": st.column_config.NumberColumn("Items", width="small")})

# --------------------------------------------------------------- deadlines (triage only)
st.subheader("Deadlines")
sla_counts = pd.Series([d["sla"] for d in tri_dated]).value_counts().to_dict()
c = st.columns(3)
c[0].metric("Past target", sla_counts.get(Q.BREACHED, 0),
            f"{pct(sla_counts.get(Q.BREACHED, 0), tri['total'])} of complaints",
            delta_color="off")
c[1].metric("Due within 5 days", sla_counts.get(Q.DUE_SOON, 0), delta_color="off")
c[2].metric("On track", sla_counts.get(Q.ON_TRACK, 0), delta_color="off")
st.caption(f"Target is {Q.SLA_DAYS} days to first response — an assumption; yours is set in "
           f"Phase 0. This batch is a historical sample spanning {oldest} days of intake, "
           f"so much of it reads as past target. That is the sample's spread, not an "
           f"operational failure. Anomaly flags carry an age but no target — a fraud "
           f"pattern is not on a complaints deadline.")

# ------------------------------------------------------- do my people agree with it
st.subheader("Do your people agree with it")
agreed, disagreed = tri["agreed"] + ano["agreed"], tri["disagreed"] + ano["disagreed"]
decided = agreed + disagreed
rate = 100 * agreed / decided if decided else None

c = st.columns(3)
c[0].metric("Agreement rate", f"{rate:.0f}%" if rate is not None else "—",
            help="Measured only over items a person actually decided on. Counting "
                 "untouched rows as agreement would make an unattended queue look like "
                 "a triumph.")
c[1].metric("Agreed", agreed)
c[2].metric("Overridden", disagreed,
            help="The most valuable rows in the system — where it was wrong and a person "
                 "caught it.")

# A rate over three decisions is not a rate. Warning on it trains the reader to ignore the
# banner, which is the opposite of what a supervision signal is for.
MIN_SAMPLE = 20
if rate is None:
    st.info("No decisions recorded yet. Work an item in either queue and this fills in.",
            icon=":material/hourglass_empty:")
elif decided < MIN_SAMPLE:
    st.info(f"{decided} of {MIN_SAMPLE} decisions needed before this rate means anything. "
            "Shown so you can watch it move, not so you can act on it yet.",
            icon=":material/hourglass_empty:")
elif rate > 97:
    st.warning("Above 97%. A warning, not a success — it usually means people have stopped "
               "reading rather than that the system got better.", icon=":material/warning:")
elif rate < 75:
    st.warning("Below 75%. It is being overridden more than it is trusted; read the "
               "disagreements before relying on it.", icon=":material/warning:")

if events:
    st.markdown("**Recent activity**")
    ev = pd.DataFrame(events).sort_values("at", ascending=False).head(10)
    st.dataframe(ev[["at", "capability", "action", "proposed", "by"]], width="stretch",
                 hide_index=True,
                 column_config={"at": st.column_config.TextColumn("When", width="small"),
                                "capability": st.column_config.TextColumn("Capability", width="small"),
                                "action": st.column_config.TextColumn("Action", width="small"),
                                "proposed": st.column_config.TextColumn("What it proposed", width="large"),
                                "by": st.column_config.TextColumn("By", width="small")})
    st.caption("A trend line appears once decisions span more than one day.")

# ------------------------------------------------------------- what it cost, what is on
st.subheader("What it cost, and what is running")
try:
    roi = json.loads(ROI.read_text())
    A = roi["assumptions"]
    price_in = A["price_in_per_1m_usd"]["value"]
    price_out = A["price_out_per_1m_usd"]["value"]
    eur = A["usd_eur"]["value"]

    def spend(n, tin, tout):
        return n * (tin / 1e6 * price_in + tout / 1e6 * price_out) * eur

    batch_cost = (spend(tri["total"], 684, 49)
                  + spend(ano["total"], A["anomaly_tokens_in"]["value"],
                          A["anomaly_tokens_out"]["value"]))
    annual = roi["annual_running_cost_total_eur"]
    ai_share = roi["ai_share_of_running_cost_pct"]
except (OSError, KeyError, json.JSONDecodeError):
    batch_cost = annual = ai_share = None

c = st.columns(3)
c[0].metric("This batch cost", f"€{batch_cost:.4f}" if batch_cost is not None else "—",
            f"{total} items", delta_color="off")
c[1].metric("Running cost a year", f"€{annual:,}" if annual else "—",
            "at the modelled volume", delta_color="off")
# 0.0035% rounds to "0.0%", which reads as a rounding artefact or a bug and destroys the
# very point the number exists to make. Show enough precision that it is legibly tiny.
share_txt = ("—" if ai_share is None
             else f"{ai_share:.3f}%" if ai_share < 0.1 else f"{ai_share:.1f}%")
c[2].metric("Of which is the AI", share_txt,
            "the rest is platform and oversight", delta_color="off")
st.caption("Model prices and the annual figure come from `cost_estimation/roi_model.json`, "
           "the same model the ROI document reads — so a cost cannot say one thing here "
           "and another in the business case.")

with st.container(border=True):
    st.dataframe(pd.DataFrame([
        {"capability": "Complaint triage", "state": "on", "in queue": tri["total"],
         "waiting on you": tri["pending"]},
        {"capability": "Anomaly review", "state": "on", "in queue": ano["total"],
         "waiting on you": ano["pending"]},
        {"capability": "Reporting assistance", "state": "on", "in queue": "on demand",
         "waiting on you": "—"},
    ]), width="stretch", hide_index=True)
    a, b = st.columns(2)
    a.markdown(f"Model — {':green-badge[configured]' if R.env('OPENAI_API_KEY') else ':red-badge[missing]'}")
    b.markdown(f"Monitoring — {':green-badge[receiving]' if R.env('LANGSMITH_API_KEY') else ':orange-badge[not configured]'}")

st.divider()
st.caption(
    "**Two honest limits.** Sign-in is a name typed into a box — it identifies who *said* "
    "they decided, not who did; real identity arrives with the case-system integration in "
    "Phase 2, and until then the audit trail is only as good as the name in the sidebar. "
    "And this is demo data: triage runs on the public CFPB corpus, anomaly review on "
    "synthetic transactions. Phase 0 replaces both with your own. "
    "An off switch per capability is also Phase 2 — listed here so it reads as missing "
    "rather than absent.")
