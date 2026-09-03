"""Chleo's page. She opens it weekly, so it answers one question: was this a normal week?

Deliberately NOT the Round 1 dashboard, and deliberately not the ops lead's page either.
Chleo supervises; she does not work the queue. Everything here describes the system's own
behaviour, which is true whether the complaints came from her intake or a public corpus —
and that is why it can be honest before Phase 0 has bought any of her data.

Charts, not tiles. A supervisor reads shape faster than she reads numbers, and a chart
cannot quietly restate the same figure in two places the way fourteen metrics did. Two
rules hold everywhere below:

  * Weekly buckets are plotted as COUNTS, never rates. Weeks here hold 1-12 items, so a
    weekly percentage is a base-rate artefact — one item is 0% or 100% and neither means
    anything.
  * Nothing modelled appears next to something measured. The payback curve is the most
    CEO-relevant picture in the project and it is deliberately absent: every chart here is
    measured from this batch, and mixing a 69-month projection in would undo that.

Per-team workload is Operations' chart (operations.py), not repeated here.
"""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp.ui import REASON_LABEL, current_operator

ROI = Path(__file__).resolve().parents[2] / "cost_estimation" / "roi_model.json"

# Near-monochrome plus one accent, matching the deck. Holding an item back is the system
# behaving well, so the accent is confident rather than cautionary; red is reserved for the
# one series that must always read zero.
SLATE, ACCENT, ALERT, FAINT = "#64748B", "#14B8A6", "#EF4444", "#94A3B8"
MIN_SAMPLE = 20

st.title("Overview")

tri_items, ano_items = Q.load_triage(), Q.load_anomaly()
if not tri_items and not ano_items:
    st.warning("No queues built yet. Run `python -m mvp.build_queues`.")
    st.stop()

tri, ano = Q.summary(tri_items), Q.summary(ano_items)


def _chart(c, height):
    st.altair_chart(c.properties(height=height).configure_view(strokeWidth=0)
                     .configure_axis(grid=False, domainColor=FAINT, tickColor=FAINT),
                    use_container_width=True)


# ------------------------------------------------------- 1. was this a normal week
st.subheader("Was this a normal week")

rows = {}
for items, key in ((tri_items, "received"), (ano_items, "raised")):
    for w in Q.by_week(items, key):
        r = rows.setdefault(w["week"], {"week": w["week"], "Proposed": 0, "Held for a person": 0})
        r["Proposed"] += w["items"] - w["held"]
        r["Held for a person"] += w["held"]

if rows:
    wk = pd.DataFrame(sorted(rows.values(), key=lambda r: r["week"]))
    latest = wk["week"].iloc[-1]
    prior = wk.iloc[:-1]
    long = wk.melt("week", var_name="outcome", value_name="items")

    # The latest bar is outlined rather than recoloured — "this week" should stand out
    # without implying it is a different kind of thing from the eight before it.
    is_latest = f"datum.week === '{latest}'"
    _chart(alt.Chart(long).mark_bar(size=26).encode(
        x=alt.X("week:O", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("items:Q", title="Items received", stack="zero"),
        color=alt.Color("outcome:N", title=None,
                        scale=alt.Scale(domain=["Proposed", "Held for a person"],
                                        range=[SLATE, ACCENT]),
                        legend=alt.Legend(orient="top", offset=4)),
        order=alt.Order("outcome:N", sort="descending"),
        opacity=alt.condition(is_latest, alt.value(1.0), alt.value(0.55)),
        tooltip=["week", "outcome", "items"]), 230)

    now, held_now = int(wk.iloc[-1][["Proposed", "Held for a person"]].sum()), int(wk.iloc[-1]["Held for a person"])
    avg = prior[["Proposed", "Held for a person"]].sum(axis=1).mean() if len(prior) else float("nan")
    st.caption(f"**{latest}: {now} in, {held_now} held for a person.** "
               + (f"The {len(prior)} weeks before it averaged {avg:.1f} in. " if len(prior) else "")
               + "Counts, not rates — a week this small cannot support a percentage. "
               + f"{len(wk)} weeks of receipts are in this batch, so the comparison is "
                 "measured; no *new* work arrives until the Phase 2 feed.")

# ------------------------------------------------------- 2. what it did with what it read
st.subheader("What it did with what it read")

did = pd.DataFrame([
    {"capability": "Complaint triage", "outcome": "Proposed", "n": tri["proposed"]},
    {"capability": "Complaint triage", "outcome": "Held for a person", "n": tri["held"]},
    {"capability": "Complaint triage", "outcome": "Reached a customer", "n": 0},
    {"capability": "Anomaly review", "outcome": "Proposed", "n": ano["proposed"]},
    {"capability": "Anomaly review", "outcome": "Held for a person", "n": ano["held"]},
    {"capability": "Anomaly review", "outcome": "Reached a customer", "n": 0},
])
# "Reached a customer" is carried at zero on purpose. It renders no bar, so the legend swatch
# beside an empty row is the claim: not "we saw none this week" but "this cannot happen".
_chart(alt.Chart(did).mark_bar(size=30).encode(
    x=alt.X("n:Q", stack="normalize", title=None,
            axis=alt.Axis(format="%", tickCount=5)),
    y=alt.Y("capability:N", title=None, sort=["Complaint triage", "Anomaly review"]),
    color=alt.Color("outcome:N", title=None,
                    scale=alt.Scale(domain=["Proposed", "Held for a person", "Reached a customer"],
                                    range=[SLATE, ACCENT, ALERT]),
                    legend=alt.Legend(orient="top", offset=4)),
    order=alt.Order("outcome:N", sort="descending"),
    tooltip=["capability", "outcome", "n"]), 170)

tot = tri["total"] + ano["total"]
st.caption(f"**{tot} items read · {tri['proposed'] + ano['proposed']} proposed · "
           f"{tri['held'] + ano['held']} held for a person · 0 reached a customer.** "
           "The red series is empty by design, not by luck — nothing leaves this system "
           "without a person. Reporting has no queue; it is measured by sections signed "
           "off, in the decision log.")

# ------------------------------------------------------- 3. why it held back
st.subheader("Why it held back")

merged = {}
for src in (tri["by_reason"], ano["by_reason"]):
    for code, n in src.items():
        merged[REASON_LABEL.get(code, code)] = merged.get(REASON_LABEL.get(code, code), 0) + n

if merged:
    rs = pd.DataFrame(sorted(({"reason": k, "n": v} for k, v in merged.items()),
                             key=lambda r: -r["n"]))
    base = alt.Chart(rs).encode(
        y=alt.Y("reason:N", title=None, sort="-x",
                axis=alt.Axis(labelLimit=320)),
        x=alt.X("n:Q", title=None, axis=None))
    _chart(base.mark_bar(size=20, color=ACCENT)
           + base.mark_text(align="left", dx=6, color=FAINT).encode(text="n:Q"),
           max(90, 34 * len(rs)))
    st.caption(f"**{sum(merged.values())} refusals, {len(merged)} distinct reasons.** Every one "
               "is a named check the item failed, not a shrug. The codes behind these labels "
               "are in the decision log under *Technical details*.")
else:
    st.caption("Nothing has been held back in this batch.")

# ------------------------------------------------------- 4. do your people agree with it
st.subheader("Do your people agree with it")

agreed = tri["agreed"] + ano["agreed"]
overridden = tri["disagreed"] + ano["disagreed"]
decided = agreed + overridden

ev = pd.DataFrame([{"k": "Agreed", "n": agreed}, {"k": "Overridden", "n": overridden}])
# Scaled to the threshold, not to the data. The empty space to the right of the bar IS the
# message; a rate quoted off nine decisions would look like evidence and would not be any.
_chart((alt.Chart(ev).mark_bar(size=34).encode(
            x=alt.X("n:Q", stack="zero", title="Decisions recorded",
                    scale=alt.Scale(domain=[0, MIN_SAMPLE + 2], nice=False),
                    axis=alt.Axis(values=[0, 5, 10, 15, MIN_SAMPLE])),
            color=alt.Color("k:N", title=None,
                            scale=alt.Scale(domain=["Agreed", "Overridden"], range=[ACCENT, SLATE]),
                            legend=alt.Legend(orient="top", offset=4)),
            order=alt.Order("k:N"), tooltip=["k", "n"])
        + alt.Chart(pd.DataFrame({"x": [MIN_SAMPLE]})).mark_rule(
            strokeDash=[4, 4], color=FAINT).encode(x="x:Q")
        + alt.Chart(pd.DataFrame({"x": [MIN_SAMPLE], "t": [f"{MIN_SAMPLE} needed"]})).mark_text(
            align="right", dx=-6, dy=-38, color=FAINT, fontSize=11).encode(
                x="x:Q", text="t:N")), 150)

if decided >= MIN_SAMPLE:
    st.caption(f"**{agreed} of {decided} proposals accepted as offered "
               f"({agreed / decided:.0%}).** {overridden} overridden. Past the dashed line, "
               "so this rate now means something.")
else:
    st.caption(f"**{decided} of the {MIN_SAMPLE} decisions needed before an agreement rate "
               f"means anything.** {agreed} agreed, {overridden} overridden so far — too few "
               "to quote a rate, so none is shown. The dashed line is the threshold.")

# ------------------------------------------------------- 5. what a year costs
st.subheader("What a year costs")

try:
    comp = json.loads(ROI.read_text())["annual_running_cost_eur"]
except (OSError, ValueError, KeyError):
    comp = {}

if comp:
    ai = sum(v for k, v in comp.items() if "Model calls" in k)
    cost = pd.DataFrame([
        {"band": "Human oversight", "eur": sum(v for k, v in comp.items() if "oversight" in k)},
        {"band": "Platform", "eur": sum(v for k, v in comp.items() if "Platform" in k)},
        {"band": f"AI — model calls (€{ai:,.2f})", "eur": ai}])
    _chart(alt.Chart(cost).mark_bar(size=34).encode(
        x=alt.X("eur:Q", stack="zero", title=None,
                axis=alt.Axis(format="~s", tickCount=4)),
        color=alt.Color("band:N", title=None, sort=None,
                        scale=alt.Scale(range=[SLATE, "#A8B3C2", ACCENT]),
                        legend=alt.Legend(orient="top", offset=4, columns=3)),
        order=alt.Order("eur:Q", sort="descending"),
        tooltip=[alt.Tooltip("band:N"), alt.Tooltip("eur:Q", format=",.2f")]), 110)
    total = sum(comp.values())
    st.caption(f"**€{total:,.0f} a year at the modelled volume.** The model itself is "
               f"€{ai:,.2f} of it — {ai / total:.4%}, too small to draw. What this costs is "
               "platform and people, which is also what you would be deciding to stop paying "
               "for. Volumes are modelled; the per-item token cost behind the AI band is "
               "measured from this batch.")

# ------------------------------------------------------- the one control on the page
st.divider()
st.markdown("**Switch a capability off**")
st.caption("Takes effect immediately, for everyone, and is written to the decision log. "
           "You do not need anyone's help to do this.")
settings = Q.settings()
cols = st.columns(len(Q.CAPABILITIES))
for col, (key, label) in zip(cols, Q.CAPABILITIES.items()):
    on = col.toggle(label, value=settings[key], key=f"cap_{key}")
    if on != settings[key]:
        Q.set_capability(key, on, by=current_operator())
        st.rerun()

st.caption(
    "**Two honest limits.** Sign-in is a name typed into a box — it records who *said* they "
    "decided, not who did; real identity arrives with the case-system integration in Phase "
    "2. And this is demo data: triage and the reporting figures both run on the public "
    "CFPB corpus, anomaly review on synthetic transactions. Phase 0 replaces them with "
    "your own.")
