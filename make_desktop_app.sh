#!/usr/bin/env bash
# Build a silent macOS launcher for the dashboard on the Desktop.
#
# A .command file is a Terminal script, so double-clicking one always opens a Terminal
# window. An .app bundle whose executable is a shell script does not — which is what you
# want when the dashboard is a live demo and the audience is watching your screen.
#
# The app starts Streamlit detached, waits for the port, opens the browser and exits.
# Nothing visible on success; failures surface as a normal macOS dialog.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Desktop/Capstone Dashboard.app"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Capstone Dashboard</string>
  <key>CFBundleExecutable</key><string>launcher</string>
  <key>CFBundleIdentifier</key><string>com.ugoahukannah.capstone.dashboard</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>LSUIElement</key><true/>
</dict>
</plist>
PLIST

cat > "$APP/Contents/MacOS/launcher" <<LAUNCHER
#!/usr/bin/env bash
REPO="$REPO"
PORT=8501
LOG="/tmp/capstone_dashboard.log"

fail() { /usr/bin/osascript -e "display dialog \\"\$1\\" with title \\"Capstone Dashboard\\" buttons {\\"OK\\"} default button 1 with icon caution"; exit 1; }

cd "\$REPO" 2>/dev/null || fail "Cannot find the project at \$REPO. Has it moved?"

# Already serving? Just show it.
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

# headless: Streamlit neither prompts for an email nor opens its own browser tab.
nohup streamlit run dashboard/app.py --server.port \$PORT --server.headless true \\
      --browser.gatherUsageStats false > "\$LOG" 2>&1 &

for _ in \$(seq 1 40); do
  /usr/bin/curl -s -o /dev/null --max-time 1 "http://localhost:\$PORT" && /usr/bin/open "http://localhost:\$PORT" && exit 0
  sleep 0.5
done
fail "The dashboard did not start within 20 seconds. See \$LOG."
LAUNCHER

chmod +x "$APP/Contents/MacOS/launcher"
touch "$APP"
echo "built: $APP"
echo "to stop the dashboard later:  pkill -f 'streamlit run dashboard/app.py'"
