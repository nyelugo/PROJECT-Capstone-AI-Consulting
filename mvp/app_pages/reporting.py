"""UC-3 — the complaints return for a chosen period, drafted section by section.

Not a queue, because this is a periodic document worked by one person, not a daily
stream. The period is selected rather than assumed: a return is written FOR a quarter or a
month, and the figures, citations and grounding all follow that choice. But the same spine and the same human step: every section is proposed, every
figure in it is checked against what this system actually computed, and a named person
signs each one.

The staleness rule is the important part. A drafted section is stored WITH the request
that produced it, and is only rendered when the request still matches. An earlier version
kept the last result and showed it under whatever the form said now — so the page could
display a draft of one section while the selector read another, with nothing to say they
disagreed. A page that silently shows the wrong thing is worse than one that shows nothing.
"""
import streamlit as st

from mvp import queue_store as Q
from mvp.capabilities.reporting import (Reporting, SECTIONS, fact_sheet, periods,
                                        period_for)
from mvp.runtime import call_model
from mvp.spine import run, PROPOSE
from mvp.ui import conf_txt, ladder_html, model_ready, status_chip

st.title("Reporting assistance")

# An off switch is only real if the page honours it. Chleo can disable this from Overview
# and it takes effect for everyone immediately, without a restart or a developer.
if not Q.is_on("reporting"):
    st.warning("**Reporting assistance is switched off.** Turn it back on from Overview.",
               icon=":material/toggle_off:")
    st.stop()

if "report" not in st.session_state:
    st.session_state.report = {"audience": None, "period": None, "sections": {}}
store = st.session_state.report

# A return is written FOR a period, so the period is chosen rather than assumed. What can be
# offered is bounded by the batch: whole calendar months it covers, plus the batch itself.
p1, p2 = st.columns(2)
period = p1.selectbox("Which period is this return for?", [p[0] for p in periods()],
                      help="Bounded by the batch. A quarter the data cannot fill is not offered.")
audience = p2.text_input("Who is this return for?", "the board risk committee",
                         help="The same figures read differently to a board and a regulator.")

lo, hi = period_for(period)
sheet = fact_sheet(lo, hi)
st.caption(f"The complaints return for **{lo}** to **{hi}** — {sheet['complaints']['v']:,} "
           f"complaints. Every section is drafted from figures this system computed for that "
           f"period; a number that is not on the fact sheet never reaches the page. The batch "
           f"is the public CFPB corpus, not this firm's book.")

# The request a stored draft must still match. Change the period or the audience and the
# drafts are not stale-but-shown, they are gone.
if (store["audience"] is not None
        and (store["audience"] != audience or store.get("period") != period)):
    store["sections"] = {}
    store["audience"] = None
    store["period"] = None

c1, c2 = st.columns([1, 3])
if c1.button("Draft the return", type="primary", disabled=not model_ready(),
             icon=":material/edit_note:"):
    prog = st.progress(0.0, "Drafting…")
    drafted = {}
    for i, name in enumerate(SECTIONS, start=1):
        prog.progress(i / len(SECTIONS), f"Drafting “{name}”…")
        d = run(Reporting(), {"section": name, "audience": audience, "period": period},
                call=call_model)
        drafted[name] = {
            "decision": d.decision, "reason_code": d.reason_code, "reason": d.reason,
            "narrative": d.payload.get("narrative", ""), "confidence": d.confidence,
            "grounding": d.grounding_detail, "citations": d.citations,
            "latency_ms": d.latency_ms, "model": d.model,
        }
    prog.empty()
    store.update({"audience": audience, "period": period, "sections": drafted})
    st.rerun()

if not store["sections"]:
    st.info("Nothing drafted yet. Press **Draft the return** — it writes all "
            f"{len(SECTIONS)} sections, then you sign each one.",
            icon=":material/description:")
    st.stop()

latest = Q.latest_by_item()
signed = sum(1 for name in store["sections"]
             if latest.get(f"report-{name}", {}).get("action") == "accepted")
c2.metric("Sections signed off", f"{signed} of {len(store['sections'])}")
st.caption(f"Drafted for **{store['audience']}** · period **{store['period']}**.")
st.divider()

for name, sec in store["sections"].items():
    item_id = f"report-{name}"
    prior = latest.get(item_id)
    ok = sec["decision"] == PROPOSE

    with st.container(border=True):
        head, side = st.columns([3, 1])
        head.subheader(name)
        head.caption(SECTIONS[name]["brief"])
        side.markdown(f"{status_chip(prior['action'] if prior else ('proposed' if ok else 'held'))}"
                      f" :gray-badge[{sec['reason_code']}]")

        if ok:
            st.write(sec["narrative"])
        else:
            st.warning(f"Not offered for signature — {sec['reason']}. "
                       f"{sec['grounding']}", icon=":material/block:")
            if sec["narrative"]:
                with st.expander("What it wrote, and why it was stopped"):
                    st.write(sec["narrative"])

        a, b = st.columns([3, 2])
        with a:
            if sec["citations"]:
                with st.expander(f"The {len(sec['citations'])} figures it used"):
                    for cite in sec["citations"]:
                        st.markdown(f"- `{cite}`")
            if ok:
                st.caption(f"Grounding check — {sec['grounding']}")
        with b:
            with st.expander("Checks"):
                st.html(ladder_html(sec["reason_code"]))
                st.caption(f"confidence {conf_txt(sec['confidence'])} · {sec['latency_ms']} ms · "
                           f"{sec['model']}")

        if prior:
            st.success(f"**{prior['action'].title()}** by {prior['by']} at "
                       f"{prior['at'].replace('T', ' ')}")
        with st.container(horizontal=True):
            if st.button("Sign off this section", key=f"acc_{item_id}", type="primary",
                         disabled=not ok, icon=":material/draw:"):
                Q.record(item_id, "accepted", capability="reporting",
                         by=st.session_state.get("operator", "unknown"),
                         proposed=name, reason_code=sec["reason_code"])
                st.rerun()
            if st.button("Reject", key=f"rej_{item_id}", icon=":material/close:"):
                Q.record(item_id, "rerouted", capability="reporting",
                         by=st.session_state.get("operator", "unknown"),
                         proposed=name, reason_code=sec["reason_code"],
                         note="section rejected by the reviewer")
                st.rerun()
