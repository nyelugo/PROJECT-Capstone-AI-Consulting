#!/usr/bin/env bash
# Double-click this to sign the demo recorder in to n8n.
#
# It has to be run by you rather than by the assistant for the ordinary reason: somebody has
# to type a password, and that is not something to hand to an agent. Everything else about
# the recording is automated — this is the one human step.
#
# If no window appears, the full headed Chromium is missing (Playwright ships the headless
# shell separately). Fix with:  python -m playwright install --force chromium
#
# A window titled "Chrome for Testing" opens on the n8n workflow. Sign in. The script
# detects the session itself and closes; you do not need to close anything.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

echo "Signing the demo recorder in to n8n"
echo "repo: $(pwd)"
echo

for p in "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" \
         "$HOME/miniconda3/etc/profile.d/conda.sh" \
         "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"; do
  [ -f "$p" ] && . "$p" && break
done
conda activate bootcamp-env 2>/dev/null || {
  echo "ERROR: could not activate the bootcamp-env conda environment."
  read -r -p "Press Return to close." _; exit 1; }

python -m demo.generate_demo poc --login
status=$?

echo
if [ $status -eq 0 ]; then
  echo "Done. Tell Claude, and the POC recording can be generated."
else
  echo "No session was established. Run this again and complete the sign-in."
fi
read -r -p "Press Return to close this window." _
