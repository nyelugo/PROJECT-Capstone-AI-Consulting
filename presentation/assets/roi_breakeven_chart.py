"""SOURCE for the chart on the ROI slide of presentation.pptx.

Every number is READ FROM cost_estimation/roi_model.json — nothing here is typed by hand,
so the chart cannot drift from the model the way a retyped figure can. Re-render with:

    python presentation/assets/roi_breakeven_chart.py

It writes presentation/assets/roi_breakeven.png at the deck's content width. Replace the
picture on the ROI slide with the new file; do not redraw it in PowerPoint.

The client's question is "when am I whole", so the y axis is the client's cumulative net
position, not a return percentage. The conservative line is on the same axes on purpose:
the gap between the two lines is exactly what the shadow pilot is built to measure.
"""
import json, pathlib
import matplotlib; matplotlib.use("Agg")
import matplotlib.font_manager
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
M = json.loads((ROOT / "cost_estimation" / "roi_model.json").read_text())

UPFRONT   = M["upfront_full_eur"]
RUN_Y1    = M["annual_running_cost_total_eur"]
RUN_AFTER = M["annual_running_cost_after_handover_eur"]
HANDOVER  = M["oversight_handover_month"]
CENTRAL   = M["scenarios"]["central"]["annual_value_eur"]
CONSERV   = M["scenarios"]["conservative"]["annual_value_eur"]
BREAKEVEN = M["scenarios"]["central"]["break_even_month"]
NET36     = M["scenarios"]["central"]["roi_36m"]["net_benefit_eur"]
ROI36     = M["scenarios"]["central"]["roi_36m"]["roi_pct"]
VALUE_FROM = 7      # value starts month 7; roi_12m earning_months = 6 fixes this

INK, INK2, INK3 = "#1A1A1A", "#4B5C69", "#8496A3"
RULE, BAND      = "#D3DBE1", "#F1F4F6"
GO, GOS         = "#0E6E67", "#E0EFED"
STOP, STOPS     = "#A93B26", "#F7E6E1"

def series(annual):
    xs, ys = [], []
    for m in range(0, 49):
        cost = UPFRONT + RUN_Y1/12*min(m, HANDOVER) + RUN_AFTER/12*max(0, m-HANDOVER)
        ben  = annual/12*max(0, m-(VALUE_FROM-1))
        xs.append(m); ys.append(ben-cost)
    return xs, ys

xc, yc = series(CENTRAL)
xk, yk = series(CONSERV)

# Carlito is the deck's typeface and ships with LibreOffice, which this workflow already
# needs for the PDF export — but it is usually not registered with fontconfig, so matplotlib
# cannot find it by name and silently falls back. That fallback is deterministic and looks
# fine on its own; it just is not the deck's face, so re-rendering on another machine would
# quietly restyle the slide. Register the file directly if it is there.
for _c in ("/Applications/LibreOffice.app/Contents/Resources/fonts/truetype",
           "/usr/share/fonts/truetype/crosextra",
           "C:/Program Files/LibreOffice/share/fonts/truetype"):
    for _f in pathlib.Path(_c).glob("Carlito-*.ttf") if pathlib.Path(_c).is_dir() else []:
        matplotlib.font_manager.fontManager.addfont(str(_f))

plt.rcParams["font.family"] = ["Carlito", "DejaVu Sans"]
fig, ax = plt.subplots(figsize=(11.53, 3.15), dpi=200)
fig.patch.set_facecolor("white"); ax.set_facecolor("white")

ax.fill_between(xc, yc, 0, where=[v < 0 for v in yc], color=STOPS, zorder=1)
ax.fill_between(xc, yc, 0, where=[v >= 0 for v in yc], color=GOS, zorder=1)
ax.plot(xk, yk, color=INK3, lw=2.0, ls=(0, (5, 3)), zorder=3)
ax.plot(xc, yc, color=STOP, lw=3.0, zorder=4)
ax.axhline(0, color=INK, lw=1.6, zorder=5)

ax.axvline(BREAKEVEN, color=GO, lw=1.6, ls=(0, (2, 2)), zorder=3)
ax.plot([BREAKEVEN], [0], "o", ms=9, color=GO, zorder=6)
ax.annotate(f"Break-even — month {BREAKEVEN}", xy=(BREAKEVEN, 0), xytext=(BREAKEVEN-1.4, 5200),
            ha="right", fontsize=15.5, color=GO, fontweight="bold", zorder=7)

i36 = xc.index(36)
ax.plot([36], [yc[i36]], "o", ms=8, color=STOP, zorder=6)
ax.annotate(f"\u2212\u20ac{abs(NET36):,.0f} at 36 months  ({ROI36:.1f}%)".replace("-", "\u2212"),
            xy=(36, yc[i36]), xytext=(37.0, -16500), ha="left",
            fontsize=15.5, color=STOP, fontweight="bold", zorder=7,
            arrowprops=dict(arrowstyle="-", color=STOP, lw=1.2,
                            shrinkA=2, shrinkB=6, connectionstyle="arc3,rad=0"))

ax.annotate("Conservative case never crosses", xy=(30, yk[30]), xytext=(19.5, -30800),
            ha="left", fontsize=14, color=INK3, zorder=7)

ax.annotate(f"\u2212\u20ac{UPFRONT:,.0f} committed\nbefore any value lands", xy=(1.6, -24000),
            xytext=(1.6, -24000), ha="left", va="center", fontsize=14, color=INK2, zorder=7)

ax.set_xlim(0, 52); ax.set_ylim(-41000, 10000)
ax.set_xticks(range(0, 49, 6))
ax.set_yticks(range(-40000, 10001, 10000))
ax.set_xlabel("Months from start", fontsize=13.5, color=INK2, labelpad=6)
ax.yaxis.set_major_formatter(FuncFormatter(
    lambda v, p: ("−" if v < 0 else "") + f"€{abs(v):,.0f}"))
ax.tick_params(labelsize=13, colors=INK2, length=0)
ax.grid(axis="y", color=RULE, lw=0.9)
ax.set_axisbelow(True)
for side in ("top", "right", "bottom", "left"): ax.spines[side].set_visible(False)
fig.tight_layout(pad=0.3)
out = HERE / "roi_breakeven.png"
fig.savefig(out, facecolor="white")
print("wrote", out, "| break-even", BREAKEVEN, "| 36m net", NET36, "| roi", ROI36)
