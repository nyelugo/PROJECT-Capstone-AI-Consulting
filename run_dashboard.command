#!/usr/bin/env bash
# Double-clickable launcher for the Round 1 complaint dashboard (macOS).
# Also the thing the Desktop shortcut delegates to, so there is one source of truth.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

echo "Capstone Round 1 — complaint dashboard"
echo "repo: $(pwd)"
echo

# conda lives in different places depending on how it was installed
for p in \
  "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" \
  "$HOME/miniconda3/etc/profile.d/conda.sh" \
  "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"; do
  [ -f "$p" ] && . "$p" && break
done

if ! conda activate bootcamp-env 2>/dev/null; then
  echo "ERROR: could not activate the bootcamp-env conda environment."
  echo "Open a terminal and run:  conda activate bootcamp-env"
  echo; read -r -p "Press Return to close." _; exit 1
fi

if [ ! -f data/complaints_dashboard.csv ]; then
  echo "ERROR: data/complaints_dashboard.csv is missing."
  echo "Run ./fetch_data.sh then python data_prep.py to rebuild it."
  echo; read -r -p "Press Return to close." _; exit 1
fi

# Streamlit prompts for an email on first run and BLOCKS until you answer, which would
# hang a double-click launch. Writing an empty credentials file dismisses it permanently.
if [ ! -f "$HOME/.streamlit/credentials.toml" ]; then
  mkdir -p "$HOME/.streamlit"
  printf '[general]\nemail = ""\n' > "$HOME/.streamlit/credentials.toml"
  echo "dismissed Streamlit's first-run email prompt"
fi

# Stop any earlier instance so the dashboard always lands on the same port.
# Without this Streamlit silently moves to 8502 and a pre-opened tab shows stale data.
pkill -f "streamlit run dashboard/app.py" 2>/dev/null && echo "stopped a previous instance" && sleep 1

echo "starting… your browser will open at http://localhost:8501"
echo "leave this window open while presenting; press Ctrl-C here to stop."
echo
streamlit run dashboard/app.py --server.port 8501 --browser.gatherUsageStats false

echo
read -r -p "Dashboard stopped. Press Return to close this window." _
