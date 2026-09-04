# Working on the deck

`presentation.pptx` is the deliverable; `presentation.pdf` is exported from it. Six things
about this deck are not obvious and each one has already cost a mistake.

## 1 · Edit in place, never regenerate

The deck has been edited by more than one person. Rebuilding it from a script discards
whatever the other author did. For a text change, rewrite the `.pptx` zip copying every part
byte-for-byte and substituting only the slide XML you mean to touch, then diff the parts and
confirm the blast radius before saving. `python-pptx` re-serialises the whole package (71
parts moved when a slide was added), so where you have to use it, verify by **content** — a
text diff of the exported PDF — rather than by counting changed parts.

## 2 · Page numbers are literal text, not fields

Every slide carries its number as a text run at 11.43in, 7.00in. There is no slide-number
field. **Insert or remove a slide and every page number after it is silently wrong.**
Renumber by position, not by shape name — one slide calls that shape `Text 6` where the rest
call it `Text 4`, and a name-based loop skips it without complaining.

Displayed number = slide index − 1. The cover carries none.

## 3 · The speaker notes file is generated

`round2_speaker_notes.md` is produced from the deck's own notes; the regeneration snippet is
at the foot of it. Do not hand-edit it — edit the notes in the `.pptx` and regenerate. It
replaced a draft that had drifted out of step with the deck and was referenced by nothing,
which is how the wrong notes get read on the day.

## 4 · Two slides are generated images, and both sources are here

"The system proposes. A person decides." (slide 4) is a PNG. Edit
[`assets/decision_spine_slide.html`](assets/decision_spine_slide.html) and run:

```bash
python presentation/assets/render_slide.py
```

That re-renders it and swaps only `ppt/media/image1.png` into the deck. It renders to the
deck's content band — full width by 6.95in of the 7.5in page — so the footer rule, footer
line and page number sit beneath the image rather than being covered. Do not redraw the slide
in PowerPoint; the source would then be a lie.

The ROI slide's chart is generated too: `assets/roi_breakeven_chart.py` reads
`cost_estimation/roi_model.json` and writes `assets/roi_breakeven.png`, deriving every point,
so it cannot drift from the model. Re-run it after any model change and replace the picture
on that slide.

It draws in **Carlito**, the deck's own face, which ships with LibreOffice but is usually not
registered with fontconfig — the script now loads the file directly from LibreOffice's bundle
so it does not silently fall back to DejaVu and restyle the slide. The render is deterministic
on one machine but not byte-identical across machines; the copy inside the `.pptx` is the
authoritative one, and `assets/roi_breakeven.png` is gitignored because it is derived.

The screenshots already carry alt text. Keep it that way if you add one.

## 5 · Every money figure is generated, and checked

Nothing in the ROI story is typed by hand. `cost_estimation/roi_model.py` writes
`roi_model.json`; `roi_risk_assessment.md` quotes it; and

```bash
python cost_estimation/check_roi_doc.py
```

fails if the document and the model disagree. **Run it after any change that touches a
number.** The deck, the strategic plan and the README quote the same figures but are *not*
covered by that checker — if a model figure moves, grep for the old value across `*.md` and
the deck's slide text *and* its speaker notes.

Current headline: −18.0% at 36 months, break-even month 46, 3,100 complaints a year needed
against this client's 2,426.

## 6 · Slide budget

pf-05 allows **10–12 slides excluding the title and backups**. The deck has 10 content slides
(2–11) and 4 backups (12–15) — **exactly the lower bound**. One more cut breaches it; there is
room for two more.

All ten prescribed roles are present and in order: title, problem, solution, POC demo,
business case, risk, compliance, deployment plan, MVP demo, conclusion — with the Round 1
bridge on slide 2 and a second solution slide at 4. The standalone problem slide was cut, so
slides 3 and 4 carry problem and solution together.

## After any change

```bash
soffice --headless --convert-to pdf --outdir . presentation.pptx
```

Copy the PDF into place by **explicit name**. A glob once matched two files, the copy failed
silently, and a stale PDF was committed alongside an updated deck.

---

The Round 1 files in this folder — `round1_pitch.pptx`, `speaker_notes.md`,
`master_pitch.md`, `one_minute_pitch.md` — are a finished deliverable from a previous
submission. They quote a different cost model and are correct for what they describe. Leave
them alone.
