"""The audit record — one row per human action, in order.

Different grain from the queues on purpose. A queue answers "what is the state of this
item" and shows it once. The log answers "what happened, and in what order" — so an item
someone revisited appears twice. Append-only; nothing here is ever edited.

Written for the auditor rather than the engineer: the columns are what a person did, the
note they left and where they sent it. Reason codes are the system's vocabulary, not an
auditor's, so they sit behind "Technical details" — available, not in the way.
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
for col in ("note", "destination", "reason_code", "proposed"):
    if col not in df.columns:
        df[col] = ""
df[["note", "destination", "reason_code", "proposed"]] = (
    df[["note", "destination", "reason_code", "proposed"]].fillna(""))
df["_day"] = pd.to_datetime(df["at"]).dt.date

with st.container(border=True):
    c = st.columns([1.4, 1, 1, 1, 1.5])
    # A period is the first thing an auditor narrows to — "what happened in June" precedes
    # every other question.
    lo_all, hi_all = df["_day"].min(), df["_day"].max()
    rng = c[0].date_input("Date range", (lo_all, hi_all),
                          min_value=lo_all, max_value=hi_all,
                          help="Actions recorded in this window.")
    caps = c[1].multiselect("Capability", sorted(df["capability"].unique()))
    acts = c[2].multiselect("Action", sorted(df["action"].unique()))
    who = c[3].multiselect("By", sorted(df["by"].unique()))
    term = c[4].text_input("Search", "", placeholder="text in any field")

view = df
if isinstance(rng, tuple) and len(rng) == 2:
    view = view[(view["_day"] >= rng[0]) & (view["_day"] <= rng[1])]
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

# What a person did, what they said about it, and where they sent it. The reason code is the
# system's own vocabulary and lives under Technical details.
sel = st.dataframe(
    view[["at", "capability", "item_id", "proposed", "action", "by", "note", "destination"]],
    width="stretch", hide_index=True, on_select="rerun", selection_mode="single-row",
    column_config={
        "at": st.column_config.TextColumn("When", width="small"),
        "capability": st.column_config.TextColumn("Capability", width="small"),
        "item_id": st.column_config.TextColumn("Item", width="small"),
        "proposed": st.column_config.TextColumn("What it proposed", width="large"),
        "action": st.column_config.TextColumn("Human action", width="small"),
        "by": st.column_config.TextColumn("By", width="small"),
        "note": st.column_config.TextColumn("Note left", width="medium"),
        "destination": st.column_config.TextColumn("Sent to", width="small"),
    })

with st.expander("Technical details — reason codes"):
    st.dataframe(view[["at", "item_id", "reason_code"]], width="stretch", hide_index=True)
    st.caption("The code the guard ladder stopped on, if any. The vocabulary is the system's, "
               "not an auditor's — kept out of the main table on purpose.")

# ------------------------------------------------------------------ open the underlying case
picked = sel.selection.rows
if picked:
    row = view.iloc[picked[0]].to_dict()
    item_id = row["item_id"]
    by_id = {i["item_id"]: i for i in Q.load_triage() + Q.load_anomaly()}
    case = by_id.get(item_id)
    st.divider()
    st.subheader("The case behind this row")
    if not case:
        st.info("This row has no case in the current batch — it is an erasure or a "
                "capability switch rather than an item decision.", icon=":material/info:")
    else:
        a, b = st.columns([3, 2])
        with a:
            when = case.get("raised") or case.get("received") or "—"
            st.markdown(f"**{item_id}** · {when}")
            st.caption(f"pseudonymous reference `{case.get('ref', '—')}`")
            if case.get("narrative"):
                st.markdown("**What the customer wrote**")
                st.info(case["narrative"][:800] + ("…" if len(case["narrative"]) > 800 else ""))
            if case.get("evidence"):
                st.markdown(f"**Quoted sentence:** “{case['evidence']}”")
            if case.get("explanation"):
                st.markdown("**Case note**")
                st.info(case["explanation"])
        with b:
            st.markdown("**Every action on this item**")
            hist = df[df["item_id"] == item_id][["at", "action", "by", "note", "destination"]]
            st.dataframe(hist, width="stretch", hide_index=True)
            st.caption(f"confidence {case.get('confidence', '—')} · {case.get('model', '—')}")

st.download_button("Export as CSV", view.drop(columns="_day").to_csv(index=False).encode(),
                   "decision_log.csv", "text/csv", icon=":material/download:")

# ------------------------------------------------------------------------------- erasure
st.divider()
with st.expander("Erase a data subject's record (GDPR Art. 17)"):
    st.caption("Erasure works on the **pseudonymous reference**, because that is the only "
               "identifier this system holds — no name, no account number, no complaint id "
               "ever reaches it. The log is append-only, so nothing is deleted: the free-text "
               "fields are replaced, the item reference is broken so the rows can no longer "
               "be tied to a subject, and the erasure itself is recorded. This erases from "
               "**this system only** — the client's case system is Phase 2, and a real "
               "request needs both.")
    refs = sorted(set(Q.refs_index().values()))
    ref = st.selectbox("Pseudonymous reference", refs, index=None,
                       placeholder="cx_…")
    if ref:
        touched = [e for e in events if e.get("item_id") in
                   {i for i, r in Q.refs_index().items() if r == ref}]
        st.write(f"**{len(touched)}** recorded action(s) would be redacted.")
        confirm = st.checkbox("I have verified this request and its identity", key="erase_ok")
        if st.button("Erase this subject's record", type="primary", disabled=not confirm,
                     icon=":material/delete_forever:"):
            n = Q.redact_ref(ref, by=st.session_state.get("operator", "unknown"))
            st.success(f"Redacted {n} row(s) and recorded the erasure.")
            st.rerun()
