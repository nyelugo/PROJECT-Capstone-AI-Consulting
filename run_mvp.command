#!/usr/bin/env bash
# Double-clickable launcher for the Round 2 MVP (macOS). Port 8502 so it can run
# alongside the Round 1 dashboard on 8501 — the Round 2 deck demos both.
# Also the thing the Desktop shortcut delegates to, so there is one source of truth.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

echo "Capstone Round 2 — Assist MVP"
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

for f in data/complaints_dashboard.csv mvp/synth/transactions.csv; do
  if [ ! -f "$f" ]; then
    echo "ERROR: $f is missing."
    echo "  complaints:   ./fetch_data.sh then python data_prep.py"
    echo "  transactions: python -m mvp.synth.make_transactions"
    echo; read -r -p "Press Return to close." _; exit 1
  fi
done

# The model key is the one hard requirement. Checked here so a double-click fails with
# a sentence rather than three disabled buttons and no explanation.
if ! grep -qE '^OPENAI_API_KEY=.+' "$HOME/.config/ironhack/.env.local" 2>/dev/null \
   && [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "WARNING: OPENAI_API_KEY not found in ~/.config/ironhack/.env.local"
  echo "The app will load but every capability will be disabled."
  echo
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
pkill -f "streamlit run mvp/app.py" 2>/dev/null && echo "stopped a previous instance" && sleep 1

echo "starting… your browser will open at http://localhost:8502"
echo "leave this window open while presenting; press Ctrl-C here to stop."
echo
streamlit run mvp/app.py --server.port 8502 --browser.gatherUsageStats false

echo
read -r -p "Assist stopped. Press Return to close this window." _
