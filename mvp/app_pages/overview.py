"""Chleo's page. What the system did, and what her people did with it.

Deliberately NOT the Round 1 dashboard. That sized an opportunity from public data; this
reports an operation. Every number here describes the system's own behaviour, which is a
true fact whether the underlying complaints came from this firm's intake or a public
corpus — which is exactly why it is the right home screen and the complaint-book analysis
is not.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp import runtime as R

st.title("Overview")
st.caption("What the system proposed, and what your people did about it.")

tri = Q.summary(Q.load_triage())
ano = Q.summary(Q.load_anomaly())
events = Q.events()

if not tri["total"] and not ano["total"]:
    st.warning("No queues built yet. Run `python -m mvp.build_queues`.")
    st.stop()

# ---------------------------------------------------------------- did it work today
st.subheader("Did it work")
c = st.columns(4)
c[0].metric("Complaints read", tri["total"], f"{tri['proposed']} proposed")
c[1].metric("Patterns raised", ano["total"], f"{ano['proposed']} with a case note")
c[2].metric("Held for a person", tri["held"] + ano["held"],
            help="The system declined to propose. This is a correct outcome, not a failure.")
c[3].metric("Waiting on someone", tri["pending"] + ano["pending"],
            delta=f"{tri['handled'] + ano['handled']} handled", delta_color="off")

held = {**{f"triage · {k}": v for k, v in tri["by_reason"].items()},
        **{f"anomaly · {k}": v for k, v in ano["by_reason"].items()}}
if held:
    with st.container(border=True):
        st.markdown("**Why it held back** — every refusal carries a code, never a shrug")
        hd = (pd.DataFrame({"reason": list(held), "items": list(held.values())})
              .sort_values("items", ascending=False))
        st.dataframe(hd, width="stretch", hide_index=True,
                     column_config={"reason": st.column_config.TextColumn("Reason", width="large"),
                                    "items": st.column_config.NumberColumn("Items", width="small")})

# ------------------------------------------------------- do my people agree with it
st.subheader("Do your people agree with it")
agreed = tri["agreed"] + ano["agreed"]
disagreed = tri["disagreed"] + ano["disagreed"]
decided = agreed + disagreed
rate = 100 * agreed / decided if decided else None

c = st.columns(3)
c[0].metric("Agreement rate", f"{rate:.0f}%" if rate is not None else "—",
            help="Measured only over items a person actually decided on. Counting "
                 "untouched rows as agreement would make an unattended queue look like a "
                 "triumph.")
c[1].metric("Agreed", agreed)
c[2].metric("Overridden", disagreed,
            help="The most valuable rows in the system — where it was wrong and a person "
                 "caught it.")

# A rate computed over three decisions is not a rate. Warning on it would train the reader
# to ignore the banner, which is the opposite of what a supervision signal is for.
MIN_SAMPLE = 20

if rate is None:
    st.info("No decisions recorded yet. Work an item in either queue and this fills in.",
            icon=":material/hourglass_empty:")
elif decided < MIN_SAMPLE:
    st.info(f"{decided} of {MIN_SAMPLE} decisions needed before this rate means anything. "
            "Shown so you can watch it move, not so you can act on it yet.",
            icon=":material/hourglass_empty:")
elif rate > 97:
    st.warning("Above 97%. That is a warning, not a success — it usually means people have "
               "stopped reading rather than that the system got better.",
               icon=":material/warning:")
elif rate < 75:
    st.warning("Below 75%. The system is being overridden more than it is trusted; look at "
               "the disagreements before it is relied on.", icon=":material/warning:")

if events:
    st.markdown("**Recent activity**")
    ev = pd.DataFrame(events).sort_values("at", ascending=False).head(12)
    st.dataframe(ev[["at", "capability", "action", "proposed", "by"]], width="stretch",
                 hide_index=True,
                 column_config={"at": st.column_config.TextColumn("When", width="small"),
                                "capability": st.column_config.TextColumn("Capability", width="small"),
                                "action": st.column_config.TextColumn("Action", width="small"),
                                "proposed": st.column_config.TextColumn("What it proposed", width="large"),
                                "by": st.column_config.TextColumn("By", width="small")})
    st.caption("A trend line appears once decisions span more than one day.")

# --------------------------------------------------------------- what is on, and cost
st.subheader("What is running")
with st.container(border=True):
    rows = [
        {"capability": "Complaint triage", "state": "on", "items": tri["total"],
         "waiting": tri["pending"]},
        {"capability": "Anomaly review", "state": "on", "items": ano["total"],
         "waiting": ano["pending"]},
        {"capability": "Reporting assistance", "state": "on", "items": "on demand",
         "waiting": "—"},
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True,
                 column_config={"capability": st.column_config.TextColumn("Capability", width="medium"),
                                "state": st.column_config.TextColumn("State", width="small"),
                                "items": st.column_config.TextColumn("In queue", width="small"),
                                "waiting": st.column_config.TextColumn("Waiting on you", width="small")})
    a, b = st.columns(2)
    a.markdown(f"Model — {':green-badge[configured]' if R.env('OPENAI_API_KEY') else ':red-badge[missing]'}")
    b.markdown(f"Monitoring — {':green-badge[receiving]' if R.env('LANGSMITH_API_KEY') else ':orange-badge[not configured]'}")
    st.caption("An off switch per capability is Phase 2 work — it needs the case-system "
               "integration. Listed here so it is visible as missing rather than absent.")

st.caption("Demo data: triage runs on the public CFPB corpus and anomaly review on "
           "synthetic transactions. Phase 0 replaces both with this firm's own.")
