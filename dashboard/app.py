"""Complaint Operations — executive view.

Round 1 dashboard for the capstone. Audience is Chleo (CEO) and an ops lead, so every
panel carries a plain-English takeaway rather than a statistical caption.

Run:  streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics as M

# --- palette (validated reference instance: blue slot 1, muted step 250) ----------
BLUE, BLUE_MUTED = "#2a78d6", "#86b6ef"
GOOD, CRITICAL = "#0ca30c", "#d03b3b"
INK, INK_2, INK_MUTED = "#0b0b0b", "#52514e", "#8a8880"
SURFACE, GRID = "#fcfcfb", "#e8e7e3"

st.set_page_config(page_title="Complaint Operations", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown(f"""<style>
 .stApp {{ background:{SURFACE}; }}
 .block-container {{ padding-top:2.2rem; max-width:1280px; }}
 h1,h2,h3 {{ color:{INK}; letter-spacing:-.015em; }}
 .kpi {{ border:1px solid {GRID}; border-radius:10px; padding:1rem 1.15rem; height:100%; }}
 .kpi .label {{ font-size:.74rem; text-transform:uppercase; letter-spacing:.07em;
                color:{INK_MUTED}; font-weight:600; }}
 .kpi .value {{ font-size:2.05rem; font-weight:680; color:{INK}; line-height:1.15;
                margin:.28rem 0 .1rem; }}
 .kpi .note  {{ font-size:.8rem; color:{INK_2}; line-height:1.35; }}
 .takeaway {{ border-left:3px solid {BLUE}; padding:.15rem 0 .15rem .8rem;
              color:{INK_2}; font-size:.9rem; margin:.1rem 0 1.4rem; }}
 .caveat {{ background:#fdf8ec; border:1px solid #f0e2c2; border-radius:10px;
            padding:.85rem 1.1rem; font-size:.85rem; color:{INK_2}; }}
</style>""", unsafe_allow_html=True)


def style(fig, height=330, xtitle="", ytitle=""):
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, showlegend=False,
        font=dict(family="Inter, -apple-system, Segoe UI, sans-serif",
                  size=13, color=INK_2),
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=GRID),
        xaxis=dict(title=xtitle, showgrid=False, zeroline=False,
                   linecolor=GRID, tickcolor=GRID),
        yaxis=dict(title=ytitle, gridcolor=GRID, zeroline=False, linecolor=GRID),
    )
    return fig


df = M.load()
h = M.headline(df)

# --- header ----------------------------------------------------------------------
st.title("Complaint Operations")
st.markdown(
    f"<p style='color:{INK_2};font-size:1.02rem;margin-top:-.5rem'>"
    f"Mid-size financial services · {M.WINDOW_START} to {M.WINDOW_END} · "
    f"{h['complaints']:,} complaints across {h['firms']} firms</p>",
    unsafe_allow_html=True)

# --- KPI row ---------------------------------------------------------------------
tiles = [
    ("Complaints handled", f"{h['complaints']:,}",
     f"across {h['issue_classes']} issue categories", INK),
    ("Answered on time", f"{h['timely_pct']:.1f}%",
     f"{h['untimely_n']} missed the deadline", GOOD),
    ("Cost money to resolve", f"{h['monetary_pct']:.1f}%",
     f"{h['any_relief_pct']:.1f}% needed some form of remedy", CRITICAL),
    ("Could be auto-sorted", f"{h['top5_share_pct']:.0f}%",
     f"sit in just {M.TOP_N_ISSUES} of {h['issue_classes']} categories", BLUE),
]
for col, (label, value, note, colour) in zip(st.columns(4), tiles):
    col.markdown(
        f"<div class='kpi'><div class='label'>{label}</div>"
        f"<div class='value' style='color:{colour}'>{value}</div>"
        f"<div class='note'>{note}</div></div>", unsafe_allow_html=True)

st.markdown("<div style='height:1.9rem'></div>", unsafe_allow_html=True)

# --- 1. weekly volume ------------------------------------------------------------
st.subheader("How many complaints arrive each week")
w = M.weekly_volume(df)
fig = go.Figure(go.Scatter(
    x=w["week"], y=w["complaints"], mode="lines+markers",
    line=dict(color=BLUE, width=2), marker=dict(size=8, color=BLUE),
    hovertemplate="Week %{x}<br><b>%{y:,} complaints</b><extra></extra>"))
fig.update_yaxes(rangemode="tozero")
st.plotly_chart(style(fig, 300, ytitle="Complaints"), width='stretch')
st.markdown(
    f"<div class='takeaway'>Between {w['complaints'].min():,} and "
    f"{w['complaints'].max():,} complaints a week, averaging "
    f"{w['complaints'].mean():,.0f}, with no trend up or down across the period. Week to "
    f"week it moves around — one quiet week sits a third below the busiest — but this is "
    f"a continuous workload to be absorbed, not a spike to staff around.</div>",
    unsafe_allow_html=True)

# --- 2 & 3. volume vs cost by product (two charts, never a dual axis) -------------
left, right = st.columns(2)
p = M.by_product(df)

with left:
    st.subheader("Where complaints come from")
    f1 = go.Figure(go.Bar(
        x=p["complaints"], y=p["short"], orientation="h",
        marker=dict(color=BLUE, cornerradius=4),
        text=[f"{v:,}" for v in p["complaints"]], textposition="outside",
        textfont=dict(color=INK_2, size=12),
        hovertemplate="%{y}<br><b>%{x:,} complaints</b><extra></extra>"))
    f1.update_yaxes(autorange="reversed")
    f1.update_xaxes(showticklabels=False, range=[0, p["complaints"].max() * 1.18])
    st.plotly_chart(style(f1, 320), width='stretch')

with right:
    st.subheader("Where they cost money")
    q = p.sort_values("monetary_pct", ascending=False)
    f2 = go.Figure(go.Bar(
        x=q["monetary_pct"], y=q["short"], orientation="h",
        marker=dict(color=CRITICAL, cornerradius=4),
        text=[f"{v:.1f}%" for v in q["monetary_pct"]], textposition="outside",
        textfont=dict(color=INK_2, size=12),
        hovertemplate="%{y}<br><b>%{x:.1f}% closed with money paid out</b><extra></extra>"))
    f2.update_yaxes(autorange="reversed")
    f2.update_xaxes(showticklabels=False, range=[0, q["monetary_pct"].max() * 1.2])
    st.plotly_chart(style(f2, 320), width='stretch')

cc, cv = p.iloc[p["monetary_pct"].argmax()], q.iloc[-1]
st.markdown(
    f"<div class='takeaway'>Volume and cost are not the same picture. "
    f"{cc['short']} complaints end with money paid out {cc['monetary_pct']:.1f}% of the "
    f"time against {cv['monetary_pct']:.1f}% for {cv['short']} — "
    f"{cc['monetary_pct']/cv['monetary_pct']:.1f} times higher. Which queue a complaint "
    f"lands in has money attached to it.</div>", unsafe_allow_html=True)

# --- 4. issue concentration ------------------------------------------------------
st.subheader("What people actually complain about")
t = M.top_issues(df, 10)
f3 = go.Figure(go.Bar(
    x=t["complaints"], y=t["Issue"], orientation="h",
    marker=dict(color=[BLUE if v else BLUE_MUTED for v in t["in_top5"]], cornerradius=4),
    text=[f"{v:.1f}%" for v in t["share_pct"]], textposition="outside",
    textfont=dict(color=INK_2, size=12),
    hovertemplate="%{y}<br><b>%{x:,} complaints</b><extra></extra>"))
f3.update_yaxes(autorange="reversed")
f3.update_xaxes(showticklabels=False, range=[0, t["complaints"].max() * 1.18])
st.plotly_chart(style(f3, 380), width='stretch')
st.markdown(
    f"<div class='takeaway'>The {M.TOP_N_ISSUES} darker bars are "
    f"<b>{h['top5_share_pct']:.1f}% of everything that arrives</b>, out of "
    f"{h['issue_classes']} possible categories. A sorting assistant does not need to "
    f"understand {h['issue_classes']} things well — it needs to understand five, and "
    f"say “I'm not sure” about the rest.</div>", unsafe_allow_html=True)

# --- 5. resolution mix -----------------------------------------------------------
left2, right2 = st.columns([1.15, 1])

with left2:
    st.subheader("How complaints end")
    r = M.resolution_mix(df)
    f4 = go.Figure(go.Bar(
        x=r["complaints"], y=r["outcome"], orientation="h",
        marker=dict(color=BLUE, cornerradius=4),
        text=[f"{v:.1f}%" for v in r["share_pct"]], textposition="outside",
        textfont=dict(color=INK_2, size=12),
        hovertemplate="%{y}<br><b>%{x:,} complaints</b><extra></extra>"))
    f4.update_yaxes(autorange="reversed")
    f4.update_xaxes(showticklabels=False, range=[0, r["complaints"].max() * 1.2])
    st.plotly_chart(style(f4, 300), width='stretch')

with right2:
    st.subheader("How much reading that is")
    f5 = go.Figure(go.Histogram(
        x=df.loc[df["narrative_chars"] <= 6000, "narrative_chars"],
        nbinsx=45, marker=dict(color=BLUE_MUTED, line=dict(width=0)),
        hovertemplate="%{x} characters<br><b>%{y:,} complaints</b><extra></extra>"))
    f5.add_vline(x=h["median_chars"], line=dict(color=BLUE, width=2, dash="dot"),
                 annotation_text=f"  median {h['median_chars']:,.0f} chars",
                 annotation_position="top right",
                 annotation_font=dict(color=INK_2, size=12))
    st.plotly_chart(style(f5, 300, xtitle="Characters in the complaint"),
                    width='stretch')

st.markdown(
    f"<div class='takeaway'>Four in five complaints are resolved with an explanation "
    f"alone — no money changes hands. But someone still has to read every one: a typical "
    f"complaint runs {h['median_chars']:,.0f} characters, roughly 200 words, and the "
    f"longest tenth run past {h['p90_chars']:,.0f}. That reading is the cost.<br><br>"
    f"“No resolution recorded” ({h['no_resolution_n']}) is not the same measure as the "
    f"{h['untimely_n']} answered late in the tile above — most late answers still reached "
    f"a resolution. Two different fields, deliberately not averaged together.</div>",
    unsafe_allow_html=True)

# --- honesty panel ---------------------------------------------------------------
st.markdown(f"""<div class='caveat'>
<b>What this data is, and what it is not.</b>
Source: the US Consumer Financial Protection Bureau's public complaint database —
open data, no personal information, narratives scrubbed before publication.
It is used here as a proxy for the <i>shape</i> of a complaint inbox: the mix of issues,
the language customers use, how cases end. <b>It is not a forecast of your volumes.</b><br><br>
Two things were corrected before anything above was calculated. The most recent weeks
were dropped, because the CFPB only publishes a complaint once the firm has responded —
leaving them in would have shown a 73% fall in complaints that never happened. And a
handling-time metric was removed, because it turned out to measure the regulator's own
routing rather than anyone's response speed. Both are documented in the repository.
</div>""", unsafe_allow_html=True)

with st.expander("See the underlying numbers as a table"):
    st.dataframe(
        p[["Product", "complaints", "monetary_pct"]].rename(columns={
            "complaints": "Complaints", "monetary_pct": "Closed with money paid (%)"}
        ).style.format({"Closed with money paid (%)": "{:.1f}"}),
        width='stretch', hide_index=True)
    st.dataframe(t[["Issue", "complaints", "share_pct"]].rename(columns={
        "complaints": "Complaints", "share_pct": "Share of all complaints (%)"}
    ).style.format({"Share of all complaints (%)": "{:.1f}"}),
        width='stretch', hide_index=True)
