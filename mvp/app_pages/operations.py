"""The ops lead's page. She opens it daily and owns the SLA and her team's day.

Separate from Overview on purpose. Chleo asks "was this a normal week"; the ops lead asks
"where do I point my team this morning, and where is the model letting them down". Those
are different questions on different rhythms, and one screen serving both was this MVP's
original design error.
"""
import pandas as pd
import streamlit as st

from mvp import queue_store as Q

st.title("Operations")
st.caption("Where the work is, where the model is wrong, and whether anyone has stopped "
           "reading.")

items = Q.load_triage()
if not items:
    st.warning("No queue built yet. Run `python -m mvp.build_queues`.")
    st.stop()

dated, as_at = Q.with_clock(items, "received")
latest = Q.latest_by_item()

# ------------------------------------------------------------------ what needs directing
breached_open = [d for d in dated if d["sla"] == Q.BREACHED
                 and Q.status_of(d["item_id"], d, latest) in Q.PENDING_STATUSES]
due_open = [d for d in dated if d["sla"] == Q.DUE_SOON
            and Q.status_of(d["item_id"], d, latest) in Q.PENDING_STATUSES]

c = st.columns(3)
c[0].metric("Queue as at", as_at)
c[1].metric("Past target, untouched", len(breached_open),
            f"oldest {max((d['age_days'] for d in breached_open), default=0)} days",
            delta_color="off")
c[2].metric("Due within 5 days", len(due_open), delta_color="off")

if breached_open:
    st.error(f"**{len(breached_open)} complaints are past the first-response target and "
             f"nobody has worked them.** Start there — Complaint triage, filter Deadline "
             f"to “breached”.", icon=":material/priority_high:")

# ------------------------------------------------------------- where the work is sitting
st.subheader("What is outstanding, by team")
out = Q.outstanding_by_team(dated)
if out:
    st.dataframe(pd.DataFrame(out), width="stretch", hide_index=True,
                 column_config={
                     "team": st.column_config.TextColumn("Proposed team", width="medium"),
                     "waiting": st.column_config.NumberColumn("Waiting", width="small"),
                     "past_target": st.column_config.NumberColumn("Of which past target",
                                                                  width="small")})
    st.caption("Grouped by the team the system proposed, which is where the work would land "
               "if every proposal were accepted as it stands.")
else:
    st.success("Nothing outstanding.", icon=":material/check_circle:")

# ------------------------------------------------------- where the model gets it wrong
st.subheader("Where the model is wrong")
teams = Q.by_proposed_team(dated)
tf = pd.DataFrame(teams)
decided_any = tf["decided"].sum() if not tf.empty else 0
st.dataframe(tf[["team", "items", "decided", "agreed", "overridden", "override_pct",
                 "sent_instead"]], width="stretch", hide_index=True,
             column_config={
                 "team": st.column_config.TextColumn("Proposed team", width="medium"),
                 "items": st.column_config.NumberColumn("In queue", width="small"),
                 "decided": st.column_config.NumberColumn("Decided", width="small"),
                 "agreed": st.column_config.NumberColumn("Agreed", width="small"),
                 "overridden": st.column_config.NumberColumn("Overridden", width="small"),
                 "override_pct": st.column_config.ProgressColumn(
                     "Override rate", min_value=0, max_value=100, format="%.0f%%"),
                 "sent_instead": st.column_config.TextColumn("Sent instead", width="large")})

if not decided_any:
    st.info("Nothing decided yet, so there is no error pattern to show. Work some items in "
            "Complaint triage and this fills in.", icon=":material/hourglass_empty:")
else:
    st.caption("**“Sent instead” is the column that matters.** A high override rate tells "
               "you the model is wrong about a team; where handlers sent those complaints "
               "instead tells you *how* — and that is the difference between fixing a prompt "
               "and fixing a taxonomy. It fills in as handlers reroute.")

# ------------------------------------------------------------------- automation bias
st.subheader("Is anyone rubber-stamping")
handlers = Q.by_handler()
if not handlers:
    st.info("No decisions recorded yet.", icon=":material/hourglass_empty:")
else:
    hf = pd.DataFrame(handlers)
    st.dataframe(hf[["handler", "decisions", "agreed", "overridden", "acceptance_pct",
                     "flag"]], width="stretch", hide_index=True,
                 column_config={
                     "handler": st.column_config.TextColumn("Handler", width="medium"),
                     "decisions": st.column_config.NumberColumn("Decisions", width="small"),
                     "agreed": st.column_config.NumberColumn("Agreed", width="small"),
                     "overridden": st.column_config.NumberColumn("Overrode", width="small"),
                     "acceptance_pct": st.column_config.ProgressColumn(
                         "Acceptance", min_value=0, max_value=100, format="%.0f%%"),
                     "flag": st.column_config.TextColumn("", width="medium")})
    flagged = [h["handler"] for h in handlers if h["flag"]]
    if flagged:
        st.warning(f"**{', '.join(flagged)}** accepted more than 97% of proposals over at "
                   f"least ten decisions. That is the automation-bias warning, not a "
                   f"performance one — it usually means the queue stopped being read, and "
                   f"the response is to look at the work, not at the person.",
                   icon=":material/warning:")
    else:
        st.caption("A rate above 97% over ten or more decisions raises a flag here. It is "
                   "risk **R2** in the register — the mitigation is *measured per handler*, "
                   "and this is that measurement.")

st.divider()
st.caption("Acceptance is measured only over items someone actually decided. This data is "
           "for calibrating the system, never for evaluating a person — using it for "
           "performance management would breach purpose limitation under GDPR and move the "
           "system into Annex III(4) of the AI Act at the same time.")
