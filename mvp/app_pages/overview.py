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

The ops lead's page was folded in here (2026-09-03). Its own docstring called one screen
serving both personas the MVP's original design error; the counter-argument that won is that
Chleo and the ops lead were reading the same system, and two pages meant two places for the
same figure to drift. Stories O1-O4 are served by the workload and agreement sections below.
"""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from mvp import queue_store as Q
from mvp.ui import REASON_LABEL

ROI = Path(__file__).resolve().parents[2] / "cost_estimation" / "roi_model.json"


# Near-monochrome plus one accent, matching the deck. Holding an item back is the system
# behaving well, so the accent is confident rather than cautionary; red is reserved for the
# one series that must always read zero.
SLATE, ACCENT, ALERT, FAINT = "#64748B", "#14B8A6", "#EF4444", "#94A3B8"
MIN_SAMPLE = 20                        # decisions before an agreement rate is quoted at all
MIN_PER_GROUP = Q.FLAG_MIN_DECISIONS   # ...and before any per-team or per-handler rate is

st.title("Overview")

tri_items, ano_items = Q.load_triage(), Q.load_anomaly()
if not tri_items and not ano_items:
    st.warning("No queues built yet. Run `python -m mvp.build_queues`.")
    st.stop()

tri, ano = Q.summary(tri_items), Q.summary(ano_items)
dated, as_at = Q.with_clock(tri_items, "received")
latest_action = Q.latest_by_item()


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
    {"capability": "Complaint triage", "outcome": "Reached a customer",
     "n": Q.reached_customer()},
    {"capability": "Anomaly review", "outcome": "Proposed", "n": ano["proposed"]},
    {"capability": "Anomaly review", "outcome": "Held for a person", "n": ano["held"]},
    {"capability": "Anomaly review", "outcome": "Reached a customer", "n": 0},  # same count
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
           f"{tri['held'] + ano['held']} held for a person · {Q.reached_customer()} "
           "reached a customer.** "
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

# ------------------------------------------------------- 4. where the work is sitting
st.subheader("What is waiting, and what is past target")

breached_open = [d for d in dated if d["sla"] == Q.BREACHED
                 and Q.status_of(d["item_id"], d, latest_action) in Q.PENDING_STATUSES]
out = Q.outstanding_by_team(dated)

if out:
    wl = pd.DataFrame(out)
    wl["Within target"] = wl["waiting"] - wl["past_target"]
    wl = wl.rename(columns={"past_target": "Past target"})
    order = list(wl.sort_values(["Past target", "waiting"], ascending=False)["team"])
    _chart(alt.Chart(wl.melt("team", value_vars=["Within target", "Past target"],
                             var_name="state", value_name="n")).mark_bar(size=18).encode(
        x=alt.X("n:Q", stack="zero", title="Complaints",
                axis=alt.Axis(tickMinStep=1, format="d", tickCount=6)),
        y=alt.Y("team:N", title=None, sort=order,
                axis=alt.Axis(labelLimit=320, labelOverlap=False)),
        color=alt.Color("state:N", title=None,
                        scale=alt.Scale(domain=["Within target", "Past target"],
                                        range=[SLATE, ALERT]),
                        legend=alt.Legend(orient="top", offset=4)),
        order=alt.Order("state:N"),
        tooltip=["team", "state", "n"]), max(190, 34 * len(wl)))

# The corpus arrives pre-aged: these complaints were filed before this batch was ever loaded,
# so the clock measures the age of the DATA, not how long anyone sat on it. Saying "nobody has
# worked them" without that reads as an operational failure and is the same defect this page
# was rebuilt to remove.
aged = sum(1 for d in dated if d["sla"] == Q.BREACHED)
st.caption(f"**{len(breached_open)} complaints are past the {Q.SLA_DAYS}-day first-response "
           f"target and untouched**, oldest "
           f"{max((d['age_days'] for d in breached_open), default=0)} days. Read that as a "
           f"demonstration of age-ranking, not as a backlog: {aged} of {len(dated)} arrived "
           "already past target, because this is a historical corpus rather than a live "
           "feed. Phase 2 makes the clock real. Triage only — anomaly candidates carry no "
           "team or target.")

if breached_open:
    # Telling someone where to click is not the same as taking them there. This presets the
    # triage filters and opens the queue already narrowed to exactly these rows.
    if st.button(f"Work the {len(breached_open)} past-target complaints",
                 type="primary", icon=":material/arrow_forward:"):
        st.session_state["show_received"] = "Needs you"
        st.session_state["f_sla_received"] = [Q.BREACHED]
        st.session_state["st_received"] = []
        st.session_state["q_received"] = ""
        st.switch_page("app_pages/triage.py")

# ------------------------------------------------------- 5. do your people agree with it
st.subheader("Do your people agree with it")

agreed = tri["agreed"] + ano["agreed"]
overridden = tri["disagreed"] + ano["disagreed"]
decided = agreed + overridden

ev = pd.DataFrame([{"k": "Accepted", "n": agreed},
                   {"k": "Overridden", "n": overridden}])
# Scaled to the threshold, not to the data. The empty space to the right of the bar IS the
# message; a rate quoted off nine decisions would look like evidence and would not be any.
_chart((alt.Chart(ev).mark_bar(size=34).encode(
            x=alt.X("n:Q", stack="zero", title="Decisions",
                    scale=alt.Scale(domain=[0, MIN_SAMPLE + 2], nice=False),
                    axis=alt.Axis(values=[0, 5, 10, 15, MIN_SAMPLE])),
            color=alt.Color("k:N", title=None,
                            scale=alt.Scale(domain=["Accepted", "Overridden"],
                                            range=[ACCENT, ALERT]),
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
               f"means anything.** {agreed} accepted, {overridden} overridden so far — too "
               "few "
               "to quote a rate, so none is shown. The dashed line is the threshold.")

# ------------------------------------------------------- 6. where the model is wrong
st.subheader("Where the model is wrong")

teams = [r for r in Q.by_proposed_team(dated) if r["decided"]]
if teams:
    tm = pd.DataFrame(teams)
    order = list(tm.sort_values(["overridden", "decided"], ascending=False)["team"])
    tm = tm.rename(columns={"agreed": "Accepted", "overridden": "Overridden"})
    _chart(alt.Chart(tm.melt("team", value_vars=["Accepted", "Overridden"],
                             var_name="k", value_name="n")).mark_bar(size=18).encode(
        x=alt.X("n:Q", stack="zero", title="Decisions",
                axis=alt.Axis(tickMinStep=1, format="d")),
        y=alt.Y("team:N", title=None, sort=order,
                axis=alt.Axis(labelLimit=320, labelOverlap=False)),
        color=alt.Color("k:N", title=None,
                        scale=alt.Scale(domain=["Accepted", "Overridden"],
                                        range=[ACCENT, ALERT]),
                        legend=alt.Legend(orient="top", offset=4)),
        order=alt.Order("k:N"), tooltip=["team", "k", "n"]), max(230, 44 * len(tm)))

    # Counts, never rates. One team has a single decision on it, and a 100% override rate off
    # one decision is the same base-rate artefact the weekly charts avoid.
    rated = [r for r in teams if r["decided"] >= MIN_PER_GROUP]
    reroutes = [f"{r['team']} → {r['sent_instead']}" for r in teams if r["sent_instead"]]
    st.caption(
        f"**{sum(r['decided'] for r in teams)} decisions across {len(teams)} teams — too few "
        f"to rate any of them.** No team has reached {MIN_PER_GROUP} decisions, so counts are "
        "shown and no override rate is quoted; a rate off one or two decisions would say more "
        "about the sample than the model. "
        + (f"Where handlers sent complaints instead: {'; '.join(reroutes)}. That is the "
           "column that matters — a high override rate says the model is wrong about a team, "
           "where it was rerouted says *how*, and that is the difference between fixing a "
           "prompt and fixing a taxonomy."
           if reroutes else "No complaint has been rerouted yet, so there is no error "
                            "pattern to read.")
        if not rated else
        "Rates are quoted only for teams past the "
        f"{MIN_PER_GROUP}-decision floor.")
else:
    st.caption("Nothing decided yet, so there is no error pattern to show. Work items in "
               "Complaint triage and this fills in.")

# ------------------------------------------------------- 7. automation bias
st.subheader("Is anyone rubber-stamping")

handlers = Q.by_handler()
if handlers:
    hd = pd.DataFrame(handlers)
    hd["enough"] = hd["decisions"] >= MIN_PER_GROUP
    _chart((alt.Chart(hd).mark_bar(size=22).encode(
                x=alt.X("acceptance_pct:Q", title="% accepted as offered",
                        scale=alt.Scale(domain=[0, 100], nice=False),
                        axis=alt.Axis(format="d",
                                      values=[0, 25, 50, 75, Q.FLAG_ACCEPTANCE])),
                y=alt.Y("handler:N", title=None, sort="-x",
                        axis=alt.Axis(labelLimit=320, labelOverlap=False)),
                color=alt.condition(
                    f"datum.acceptance_pct > {Q.FLAG_ACCEPTANCE} && datum.enough",
                    alt.value(ALERT), alt.value(SLATE)),
                opacity=alt.condition("datum.enough", alt.value(1.0), alt.value(0.5)),
                tooltip=["handler", "decisions", "agreed", "overridden",
                         alt.Tooltip("acceptance_pct:Q", format=".1f")])
            + alt.Chart(pd.DataFrame({"x": [Q.FLAG_ACCEPTANCE]})).mark_rule(
                strokeDash=[4, 4], color=FAINT).encode(x="x:Q")), max(130, 34 * len(hd)))

    flagged = [h["handler"] for h in handlers if h["flag"]]
    thin = [h["handler"] for h in handlers if h["decisions"] < MIN_PER_GROUP]
    if flagged:
        st.caption(f"**{', '.join(flagged)} accepted more than {Q.FLAG_ACCEPTANCE}% of "
                   f"proposals over at least "
                   f"{MIN_PER_GROUP} decisions.** That is the automation-bias warning, not a "
                   "performance one — it usually means the queue stopped being read, and the "
                   "response is to look at the work, not at the person.")
    else:
        st.caption(f"**Nobody is above the {Q.FLAG_ACCEPTANCE}% line** (the dashed rule) over "
                   f"{MIN_PER_GROUP} or more decisions. This is the measured mitigation for "
                   "risk **R2** in the register."
                   + (f" Faded bars — {', '.join(thin)} — are below the {MIN_PER_GROUP}-"
                      "decision floor and are not flagged either way." if thin else ""))
else:
    st.caption("No decisions recorded yet.")

st.caption("Acceptance is measured only over items someone actually decided. This data is "
           "for calibrating the system, never for evaluating a person — using it for "
           "performance management would breach purpose limitation under GDPR and move the "
           "system into Annex III(4) of the AI Act at the same time.")

# ------------------------------------------------------- 8. what a year costs
st.subheader("What a year of running it costs")

try:
    _roi = json.loads(ROI.read_text())
    comp = _roi["annual_running_cost_eur"]
except (OSError, ValueError, KeyError):
    _roi, comp = {}, {}

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
    ass = _roi.get("assumptions", {})
    days = ass.get("review_days_per_quarter", {}).get("value")
    perm = ass.get("platform_eur_month", {}).get("value")
    vol = _roi.get("break_even_volume", {}).get("this_client_complaints_per_year")
    inh = _roi.get("oversight_inhouse_day_eur")
    rate = _roi.get("consultant_day_rate_eur")
    st.caption(
        f"**€{total:,.0f} a year to keep running** — what stops if you stop. The one-off "
        "build is not in it. "
        f"**No complaint data feeds the two large bands.** Oversight is {days} review-days a "
        f"quarter at a €{rate} consultant day rate and platform is €{perm} a month "
        "for hosting, monitoring and logging; both are judgement estimates, and neither "
        f"moves with volume — the bill is the same at {vol:,} complaints a year or ten times "
        f"that, so cost per complaint falls as volume rises. Only the AI band is measured "
        f"from this batch: €{ai:,.2f}, {ai / total:.4%}, too small to draw. Oversight run "
        f"in-house rather than by a consultant is about €{days * 4 * inh:,.0f}, which is the "
        "largest single lever here."
        if days and perm and vol and inh and rate else
        f"**€{total:,.0f} a year to keep running.** The model itself is €{ai:,.2f} of it.")

st.divider()
st.caption(
    "**Two honest limits.** Sign-in is a name typed into a box — it records who *said* they "
    "decided, not who did; real identity arrives with the case-system integration in Phase "
    "2. And this is demo data: triage and the reporting figures both run on the public "
    "CFPB corpus, anomaly review on synthetic transactions. Phase 0 replaces them with "
    "your own.")
