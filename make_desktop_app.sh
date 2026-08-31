#!/usr/bin/env bash
# Build the Desktop launcher for Assist.
#
# It does ONE thing: open the app, ready to demo. An earlier version of this script built
# a launchpad page linking every document in the repo — which was a second copy of the
# README, on a machine-specific path, guaranteed to drift from the real one. The documents
# are for reading and grading, not for presenting. A desktop icon exists for the one
# moment you actually double-click it: you are about to present.
#
# There is one app now. The Round 1 dashboard is a page inside it rather than a second
# server on a second port, because switching ports mid-demo is a seam the audience sees.
#
# Why an .app and not a .command: a .command is a Terminal script, so double-clicking one
# always opens a Terminal window. An .app bundle whose executable is a shell script does
# not — which is what you want when the audience is watching your screen.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Desktop/Assist.app"

rm -rf "$APP" "$HOME/Desktop/Capstone.app" "$HOME/Desktop/Capstone Dashboard.app"
mkdir -p "$APP/Contents/MacOS"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Assist</string>
  <key>CFBundleExecutable</key><string>launcher</string>
  <key>CFBundleIdentifier</key><string>com.ugoahukannah.capstone.assist</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>3.0</string>
  <key>LSUIElement</key><true/>
</dict>
</plist>
PLIST

cat > "$APP/Contents/MacOS/launcher" <<LAUNCHER
#!/usr/bin/env bash
REPO="$REPO"
PORT=8502
LOG="/tmp/assist.log"

fail() { /usr/bin/osascript -e "display dialog \\"\$1\\" with title \\"Assist\\" buttons {\\"OK\\"} default button 1 with icon caution"; exit 1; }

cd "\$REPO" 2>/dev/null || fail "Cannot find the project at \$REPO. Has it moved? Re-run make_desktop_app.sh."

# Already serving? Just show it. Makes a second double-click harmless.
if /usr/bin/curl -s -o /dev/null --max-time 2 "http://localhost:\$PORT"; then
  /usr/bin/open "http://localhost:\$PORT"; exit 0
fi

for p in "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" \\
         "\$HOME/miniconda3/etc/profile.d/conda.sh" \\
         "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"; do
  [ -f "\$p" ] && . "\$p" && break
done
conda activate bootcamp-env 2>/dev/null || fail "Could not activate the bootcamp-env conda environment."
[ -f data/complaints_dashboard.csv ] || fail "data/complaints_dashboard.csv is missing. Run ./fetch_data.sh then python data_prep.py."
[ -f mvp/synth/transactions.csv ]    || fail "mvp/synth/transactions.csv is missing. Run python -m mvp.synth.make_transactions."

# Streamlit prompts for an email on first run and BLOCKS until answered, which would hang
# a double-click launch for ever. An empty credentials file dismisses it permanently.
if [ ! -f "\$HOME/.streamlit/credentials.toml" ]; then
  mkdir -p "\$HOME/.streamlit"
  printf '[general]\\nemail = ""\\n' > "\$HOME/.streamlit/credentials.toml"
fi

nohup streamlit run mvp/app.py --server.port \$PORT --server.headless true \\
      --browser.gatherUsageStats false > "\$LOG" 2>&1 &

# Read the three data files in a throwaway process while Streamlit boots. This does NOT
# warm the server's own caches — those are per-process and fill on first visit to each
# page — but it does pull 12MB of CSV into the OS file cache, so that first visit reads
# from memory instead of disk. Modest, honest, and free.
( python - <<'WARM' >/dev/null 2>&1
import sys; sys.path[:0] = ["dashboard", "classifier"]
try:
    import metrics; metrics.load()
    from mvp.capabilities import reporting, anomaly
    reporting.fact_sheet(); anomaly.detect()
except Exception:
    pass
WARM
) &

for _ in \$(seq 1 40); do
  /usr/bin/curl -s -o /dev/null --max-time 1 "http://localhost:\$PORT" && /usr/bin/open "http://localhost:\$PORT" && exit 0
  sleep 0.5
done
fail "Assist did not start within 20 seconds. See \$LOG."
LAUNCHER

chmod +x "$APP/Contents/MacOS/launcher"
touch "$APP"
echo "built: $APP"
echo "  one app, five pages, sidebar navigation"
echo "  stop it later:  pkill -f 'streamlit run mvp/app.py'"
