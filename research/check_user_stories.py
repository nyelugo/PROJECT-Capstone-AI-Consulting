"""Verify the user-stories score table against the stories themselves.

Written because the first version of that table was ASSERTED, not counted: it claimed
26 stories and 14/5/7 when there were 30 and 13/5/12. A summary figure that nobody
recomputes is the same defect as a stale screenshot.

Run:  python research/check_user_stories.py     (exit 0 = the table matches the stories)
"""
import pathlib, re, sys
from collections import Counter

DOC = pathlib.Path(__file__).resolve().parent / "user_stories.md"
t = DOC.read_text()

parts = re.split(r"\n> \*\*([CDOHAR]\d)\.\*\*", t)
pairs = list(zip(parts[1::2], parts[2::2]))
rows, missing = [], []
for sid, body in pairs:
    body = body.split("\n## ")[0].split("\n---")[0]
    m = re.search(r"\*\*(NOT MET|PARTIAL|MET)\.?\*\*", body)
    (rows.append((sid, m.group(1))) if m else missing.append(sid))

fail = []
if missing:
    fail.append(f"stories with no status: {missing}")

by = {}
for sid, st in rows:
    by.setdefault(sid[0], Counter())[st] += 1
tot = Counter()
for k in "COHARD":
    tot += by.get(k, Counter())
n = sum(tot.values())

# the table's own figures
tbl = {}
for line in t.splitlines():
    m = re.match(r"\| (MET|PARTIAL|NOT MET) \|(.+)\| \*\*(\d+)\*\* \|", line)
    if m:
        tbl[m.group(1)] = (int(m.group(3)),
                           [int(x.strip()) for x in m.group(2).split("|")])
for key in ("MET", "PARTIAL", "NOT MET"):
    if key not in tbl:
        fail.append(f"table row missing: {key}")
        continue
    total, per = tbl[key]
    if total != tot[key]:
        fail.append(f"{key}: table says {total}, stories say {tot[key]}")
    actual = [by.get(k, Counter())[key] for k in "COHARD"]
    if per != actual:
        fail.append(f"{key}: per-role {per} vs actual {actual}")

m = re.search(r"\*\*(\d+) of (\d+) fully met\.\*\*", t)
if not m:
    fail.append("the 'N of M fully met' line is missing")
elif (int(m.group(1)), int(m.group(2))) != (tot["MET"], n):
    fail.append(f"'fully met' line says {m.group(1)} of {m.group(2)}, "
                f"counted {tot['MET']} of {n}")

print(f"{n} stories · MET {tot['MET']} · PARTIAL {tot['PARTIAL']} · NOT MET {tot['NOT MET']}")
if fail:
    print("\nMISMATCH:")
    for f in fail:
        print(f"  {f}")
    sys.exit(1)
print("the score table matches the stories")
