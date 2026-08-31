"""Make the Round 1 classifier modules importable without copying them.

`classifier/prompt.py`, `decide.py` and `teams.py` are flat-imported by the Round 1 code
and by `n8n/build_workflow.py`. The MVP reads the SAME files rather than a fork of them,
so the POC, the monitoring and the product cannot describe the same decision differently.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in (ROOT / "classifier", ROOT / "dashboard"):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))
