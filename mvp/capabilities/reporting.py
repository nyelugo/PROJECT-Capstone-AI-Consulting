"""UC-3 — Reporting assistance. Drafts report prose, grounded in figures we computed.

The failure everyone fears from a language model writing a regulatory report is a
confident invented number. So the grounding rule here is arithmetic rather than textual:

    every number that appears in the drafted prose must be a figure this repo computed

The model is handed a fact sheet built by `dashboard/metrics.py` — the same module the
Round 1 dashboard and every document read from, so a figure cannot say one thing in a
report and another on a slide. It may use those figures and no others. A number in the
narrative that is not on the sheet is caught by a scan of the prose itself, not by trusting
the model's own list of what it used, because a model that invents a figure will also
invent the citation for it.

Two distinct rejections, at two different stages, because they are different faults:
  REJECT_METRIC_NOT_PUBLISHED  the model asked for a metric this system does not compute
  REJECT_FIGURE_NOT_COMPUTED   a number appeared in the prose that is on no sheet
"""
from __future__ import annotations

import re
from functools import lru_cache

from . import _shared  # noqa: F401  (path setup)

import metrics as M

from ..runtime import pseudonymise
from ..spine import parse_json_object

MODEL = "gpt-4o-mini"
THRESHOLD = 0.70

# Which figures each section is allowed to talk about. A section is a scope boundary, not
# a formatting choice: it stops the model reaching for a number that is real but
# irrelevant, which is how misleading-but-true reporting gets written.
SECTIONS: dict[str, dict] = {
    "Volume and concentration": {
        "keys": ["complaints", "firms", "issue_classes", "top5_share_pct",
                 "top_issue_1_name", "top_issue_1_share_pct", "top_issue_2_name",
                 "top_issue_2_share_pct", "largest_product_name", "largest_product_share_pct"],
        "brief": "how much arrived, and how concentrated it is",
    },
    "Outcomes and redress": {
        "keys": ["complaints", "any_relief_pct", "monetary_pct", "no_resolution_n",
                 "highest_relief_product_name", "highest_relief_product_pct",
                 "lowest_relief_product_name", "lowest_relief_product_pct"],
        "brief": "how cases ended and how often money was paid back",
    },
    "Timeliness": {
        "keys": ["complaints", "timely_pct", "untimely_n", "no_resolution_n"],
        "brief": "whether responses met the deadline, and what was never resolved",
    },
    "Complaint content": {
        "keys": ["complaints", "median_chars", "p90_chars", "issue_classes",
                 "top_issue_1_name", "top_issue_1_share_pct"],
        "brief": "what customers actually write, and how long it is",
    },
}


@lru_cache(maxsize=1)
def fact_sheet() -> dict[str, dict]:
    """Every figure this system is willing to publish, computed from the real data.

    Cached because a Streamlit rerun must not re-read a 3.7MB CSV, and because the whole
    point is that the numbers are stable — two calls in one session cannot disagree.
    """
    df = M.load()
    h = M.headline(df)
    issues = M.top_issues(df, n=5)
    prods = M.by_product(df).sort_values("monetary_pct", ascending=False)
    big = M.by_product(df).iloc[0]

    f: dict[str, dict] = {
        "complaints": {"v": h["complaints"], "unit": "count", "label": "complaints in the window"},
        "firms": {"v": h["firms"], "unit": "count", "label": "firms named"},
        "issue_classes": {"v": h["issue_classes"], "unit": "count", "label": "distinct issue categories"},
        "timely_pct": {"v": h["timely_pct"], "unit": "%", "label": "responded to on time"},
        "untimely_n": {"v": h["untimely_n"], "unit": "count", "label": "not responded to on time"},
        "any_relief_pct": {"v": h["any_relief_pct"], "unit": "%", "label": "closed with relief of some kind"},
        "monetary_pct": {"v": h["monetary_pct"], "unit": "%", "label": "closed with money paid back"},
        "no_resolution_n": {"v": h["no_resolution_n"], "unit": "count", "label": "with no resolution recorded"},
        "top5_share_pct": {"v": h["top5_share_pct"], "unit": "%", "label": "share held by the top 5 issues"},
        "median_chars": {"v": h["median_chars"], "unit": "characters", "label": "median complaint length"},
        "p90_chars": {"v": h["p90_chars"], "unit": "characters", "label": "90th percentile complaint length"},
        "largest_product_name": {"v": big["short"], "unit": "text", "label": "product with the most complaints"},
        "largest_product_share_pct": {"v": 100 * big["complaints"] / h["complaints"], "unit": "%",
                                      "label": "that product's share of all complaints"},
        "highest_relief_product_name": {"v": prods.iloc[0]["short"], "unit": "text",
                                        "label": "product most likely to end in money paid back"},
        "highest_relief_product_pct": {"v": prods.iloc[0]["monetary_pct"], "unit": "%",
                                       "label": "its monetary-relief rate"},
        "lowest_relief_product_name": {"v": prods.iloc[-1]["short"], "unit": "text",
                                       "label": "product least likely to end in money paid back"},
        "lowest_relief_product_pct": {"v": prods.iloc[-1]["monetary_pct"], "unit": "%",
                                      "label": "its monetary-relief rate"},
        "window_start": {"v": M.WINDOW_START, "unit": "date", "label": "reporting window opens"},
        "window_end": {"v": M.WINDOW_END, "unit": "date", "label": "reporting window closes"},
    }
    for i, row in enumerate(issues.itertuples(), start=1):
        f[f"top_issue_{i}_name"] = {"v": row.Issue, "unit": "text", "label": f"#{i} issue category"}
        f[f"top_issue_{i}_share_pct"] = {"v": row.share_pct, "unit": "%", "label": f"#{i} issue's share"}
    return f


_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def _numbers_in(text: str) -> list[float]:
    out = []
    for m in _NUM.finditer(text or ""):
        try:
            out.append(float(m.group(0).replace(",", "")))
        except ValueError:
            pass
    return out


def _allowed_numbers(keys: list[str], sheet: dict) -> set[float]:
    """Numbers the prose may contain: the section's own figures, plus the window dates.

    Dates are admitted because a report legitimately names its period, and a date's parts
    are numbers like any other. Nothing else is admitted — no round numbers, no counts the
    model might reasonably infer. Inference is exactly what must not happen here.
    """
    allowed: set[float] = set()
    for k in keys:
        v = sheet.get(k, {}).get("v")
        if isinstance(v, (int, float)):
            allowed.add(float(v))
    for k in ("window_start", "window_end"):
        allowed |= set(_numbers_in(str(sheet[k]["v"])))
    return allowed


def _unmatched(cited: float, allowed: set[float]) -> bool:
    """A cited number is fine if some allowed figure rounds to it.

    Tolerance is the width of one rounding step at the precision written, so 46.1 may be
    written "46.1" or "46", and 60.53 may be written "61" — but 47 is a different number
    and is caught.
    """
    tol = 0.55 if float(cited).is_integer() else 0.055
    return not any(abs(a - cited) <= tol for a in allowed)


class Reporting:
    name = "reporting"
    title = "Reporting assistance"
    threshold = THRESHOLD
    model = MODEL

    def ref(self, request: dict) -> str:
        return pseudonymise(f"report:{request.get('section','?')}")

    def validate(self, request: dict) -> str | None:
        if request.get("section") not in SECTIONS:
            return f"'{request.get('section')}' is not a section this system reports on"
        audience = (request.get("audience") or "").strip()
        if len(audience) < 3:
            return "an audience is required — the same figures read differently to a board and a regulator"
        return None

    def messages(self, request: dict) -> list[dict]:
        sheet = fact_sheet()
        keys = SECTIONS[request["section"]]["keys"]
        lines = []
        for k in keys:
            e = sheet[k]
            v = f"{e['v']:.1f}" if isinstance(e["v"], float) else e["v"]
            lines.append(f"- {k} = {v} ({e['unit']}) — {e['label']}")
        system = (
            "You draft sections of a retail bank's complaints report. You do not decide "
            "anything and you do not publish. A compliance officer reviews every word.\n\n"
            "You are given a fact sheet. It is the ONLY source of numbers you may use.\n\n"
            "Rules:\n"
            "- Every number in your prose must come from the fact sheet. Copy it, do not "
            "recompute it, do not add it up, do not estimate anything.\n"
            "- Never state a number that is not on the sheet. If the point you want to "
            "make needs a figure you were not given, make a different point.\n"
            "- Do not describe a trend, a rise or a fall. The sheet is one window; it "
            "contains no comparison period.\n"
            "- Write 3 to 5 sentences of plain prose. No bullet points, no headings.\n"
            "- List every fact-sheet key you used in figures_used.\n"
            "- confidence is how sure you are that the section is accurate and complete "
            "given only these figures.\n\n"
            'Respond with JSON only:\n'
            '{"narrative": "<3-5 sentences>", "figures_used": ["<key>", ...], '
            '"confidence": <number 0-1>}')
        user = (f"Section: {request['section']} — {SECTIONS[request['section']]['brief']}\n"
                f"Audience: {request['audience']}\n"
                f"Reporting window: {sheet['window_start']['v']} to {sheet['window_end']['v']}\n\n"
                f"Fact sheet:\n" + "\n".join(lines))
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def parse(self, text: str) -> dict:
        o = parse_json_object(text)
        if not str(o.get("narrative", "")).strip():
            raise ValueError("model returned an empty narrative")
        used = o.get("figures_used") or []
        return {"narrative": str(o.get("narrative", "")).strip(),
                "figures_used": [str(k) for k in used] if isinstance(used, list) else [],
                "confidence": o.get("confidence")}

    def scope_check(self, parsed: dict, request: dict) -> str | None:
        allowed = set(SECTIONS[request["section"]]["keys"])
        if any(k not in allowed for k in parsed["figures_used"]):
            return "REJECT_METRIC_NOT_PUBLISHED"
        return None

    def grounding_check(self, parsed: dict, request: dict) -> tuple[str | None, str]:
        sheet = fact_sheet()
        allowed = _allowed_numbers(SECTIONS[request["section"]]["keys"], sheet)
        bad = [n for n in _numbers_in(parsed["narrative"]) if _unmatched(n, allowed)]
        if bad:
            shown = ", ".join(f"{b:g}" for b in bad[:4])
            return ("REJECT_FIGURE_NOT_COMPUTED",
                    f"{len(bad)} figure(s) in the draft were not computed from the data: {shown}")
        n = len(_numbers_in(parsed["narrative"]))
        return None, f"all {n} figure(s) in the draft trace to the fact sheet"

    def summarise(self, parsed: dict, request: dict) -> str:
        return f"Draft '{request.get('section')}' for {request.get('audience')}"

    def citations(self, parsed: dict) -> list[str]:
        sheet = fact_sheet()
        out = []
        for k in parsed.get("figures_used", []):
            e = sheet.get(k)
            if e:
                v = f"{e['v']:.1f}" if isinstance(e["v"], float) else e["v"]
                out.append(f"{k} = {v}")
        return out
