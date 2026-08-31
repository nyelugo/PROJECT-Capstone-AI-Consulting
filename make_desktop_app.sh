#!/usr/bin/env bash
# Build ONE silent macOS launcher on the Desktop for the whole capstone.
#
# Supersedes the earlier "Capstone Dashboard.app", which only started the Round 1
# dashboard. Round 2 added a second Streamlit app, a presentation, a POC and six
# documents, and hunting for those mid-demo is exactly the wrong thing to be doing in
# front of a panel. One double-click now:
#
#   * starts the Round 1 dashboard  (port 8501)
#   * starts the Round 2 MVP        (port 8502)
#   * opens a launchpad page with everything else one click away
#
# Why an .app and not a .command: a .command file is a Terminal script, so double-clicking
# one always opens a Terminal window. An .app bundle whose executable is a shell script
# does not — which is what you want when the audience is watching your screen.
#
# The launchpad opens IMMEDIATELY and polls the two ports itself, so the buttons go live
# as each server comes up rather than the whole thing hanging for twenty seconds first.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Desktop/Capstone.app"
OLD="$HOME/Desktop/Capstone Dashboard.app"

# Links to things that are not files. Kept here so there is one place to correct them.
N8N_URL="https://ac-ft-26-07-06.n8n.irn.hk/workflow/NkRpklvLHKgcP3Ol"
LS_ORG="bdd29afc-aefb-432d-a118-2ee71dc41429"
LS_PROJECTS="https://eu.smith.langchain.com/o/${LS_ORG}/projects"
LS_EXPERIMENT="https://eu.smith.langchain.com/o/${LS_ORG}/datasets/074b52a4-d07a-46e6-9b10-7aac69b24c79"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Capstone</string>
  <key>CFBundleExecutable</key><string>launcher</string>
  <key>CFBundleIdentifier</key><string>com.ugoahukannah.capstone</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>2.0</string>
  <key>LSUIElement</key><true/>
</dict>
</plist>
PLIST

# ---------------------------------------------------------------- the launchpad page
# Written with a quoted heredoc so nothing here is shell-expanded, then the four
# placeholders are substituted. Lives inside the bundle rather than the repo, so the
# repo stays free of machine-specific absolute paths.
cat > "$APP/Contents/Resources/launchpad.html" <<'HTML'
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Capstone — AI Consulting</title>
<style>
  :root{--ink:#1D2A32;--navy:#24343F;--steel:#445A69;--blue:#2A78D6;--ice:#EFF5F9;
        --line:#D9E3EA;--muted:#6B7C88;--bg:#FBFBFD;--card:#FFFFFF}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
  .wrap{max-width:1080px;margin:0 auto;padding:38px 28px 60px}
  h1{font-size:30px;margin:0 0 4px;letter-spacing:-.3px}
  .sub{color:var(--muted);margin:0 0 30px;font-size:14px}
  h2{font-size:12px;letter-spacing:1.6px;text-transform:uppercase;color:var(--steel);
     margin:34px 0 12px;font-weight:700}
  .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fill,minmax(250px,1fr))}
  a.card{display:block;padding:15px 17px;background:var(--card);border:1px solid var(--line);
         border-radius:9px;text-decoration:none;color:inherit;transition:.12s}
  a.card:hover{border-color:var(--blue);transform:translateY(-1px);
               box-shadow:0 3px 12px rgba(42,120,214,.13)}
  a.card.big{background:var(--navy);color:#fff;border-color:var(--navy)}
  a.card.big:hover{background:#2c404e}
  .t{font-weight:700;font-size:15px;margin-bottom:3px}
  .d{font-size:12.5px;color:var(--muted);line-height:1.45}
  a.card.big .d{color:#C6D8E4}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;
       background:#C8CFD5;margin-right:7px;vertical-align:1px}
  .dot.up{background:#3FB950}.dot.down{background:#D9803B}
  .state{font-size:12px;color:#C6D8E4;margin-top:9px}
  footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);
         font-size:12.5px;color:var(--muted)}
  code{background:var(--ice);padding:1.5px 6px;border-radius:4px;font-size:12px}
</style></head><body><div class="wrap">

<h1>Capstone — AI Consulting</h1>
<p class="sub">Ugo Ahukannah · Chleo, mid-size EU retail bank · Rounds 1 and 2</p>

<h2>Live demos</h2>
<div class="grid">
  <a class="card big" href="http://localhost:8502" id="mvp">
    <div class="t"><span class="dot" id="d-mvp"></span>Round 2 — the MVP</div>
    <div class="d">Assist. Triage, reporting and anomaly flagging on one decision spine.</div>
    <div class="state" id="s-mvp">starting…</div></a>
  <a class="card big" href="http://localhost:8501" id="dash">
    <div class="t"><span class="dot" id="d-dash"></span>Round 1 — the dashboard</div>
    <div class="d">16,839 complaints. The business picture, with no model in it.</div>
    <div class="state" id="s-dash">starting…</div></a>
  <a class="card" href="__N8N__">
    <div class="t">The POC — n8n workflow</div>
    <div class="d">Nine nodes on the cohort instance. Needs a login.</div></a>
  <a class="card" href="__LSPROJ__">
    <div class="t">Monitoring — LangSmith</div>
    <div class="d">Tracing projects, EU workspace. <code>capstone-mvp</code> is Round 2.</div></a>
  <a class="card" href="__LSEXP__">
    <div class="t">Evaluation — LangSmith</div>
    <div class="d">The 60-example dataset and the scored experiment.</div></a>
</div>

<h2>Present</h2>
<div class="grid">
  <a class="card" href="file://__REPO__/presentation.pdf">
    <div class="t">Round 2 deck (PDF)</div>
    <div class="d">11 slides + 6 backups. The submitted format.</div></a>
  <a class="card" href="file://__REPO__/presentation.pptx">
    <div class="t">Round 2 deck (PowerPoint)</div>
    <div class="d">Editable, speaker notes on all 18 slides.</div></a>
  <a class="card" href="file://__REPO__/presentation/round2_speaker_notes.md">
    <div class="t">Speaker notes</div>
    <div class="d">What to say, slide by slide, with stage directions.</div></a>
  <a class="card" href="file://__REPO__/presentation/round1_pitch.pptx">
    <div class="t">Round 1 deck</div>
    <div class="d">As delivered on 30 August.</div></a>
</div>

<h2>The consulting package</h2>
<div class="grid">
  <a class="card" href="file://__REPO__/use_case_definition.md">
    <div class="t">Use case definition</div>
    <div class="d">Problem, profile, stakeholders, success criteria, scope.</div></a>
  <a class="card" href="file://__REPO__/roi_risk_assessment.md">
    <div class="t">ROI and risk · 20 pts</div>
    <div class="d">12/36-month ROI, break-even, sensitivity, 12 risks.</div></a>
  <a class="card" href="file://__REPO__/compliance/eu_ai_act_compliance.md">
    <div class="t">EU AI Act · 20 pts</div>
    <div class="d">Step-by-step classification, conformity summary, Annex IV.</div></a>
  <a class="card" href="file://__REPO__/compliance/gdpr_documentation.md">
    <div class="t">GDPR · 10 pts</div>
    <div class="d">Data flow, Art. 30 register, DPIA, rights, transfers.</div></a>
  <a class="card" href="file://__REPO__/strategic_plan.md">
    <div class="t">Strategic plan · 10 pts</div>
    <div class="d">Phases, KPIs, go-to-market, commercialisation.</div></a>
  <a class="card" href="file://__REPO__/poc/poc_documentation.md">
    <div class="t">POC documentation</div>
    <div class="d">Tools, nodes, limits, how to reproduce.</div></a>
  <a class="card" href="file://__REPO__/mvp/mvp_documentation.md">
    <div class="t">MVP documentation</div>
    <div class="d">How to run it, the guard ladder, seven known limits.</div></a>
  <a class="card" href="file://__REPO__/feedback/round1_decision.md">
    <div class="t">Round 1 decision</div>
    <div class="d">KEEP, and why the scope widened to three use cases.</div></a>
</div>

<h2>Orientation</h2>
<div class="grid">
  <a class="card" href="file://__REPO__/README.md">
    <div class="t">README</div>
    <div class="d">Both rounds, every deliverable, what is outstanding.</div></a>
  <a class="card" href="file://__REPO__/STACK.md">
    <div class="t">STACK.md</div>
    <div class="d">The nine moving parts and what each is not.</div></a>
  <a class="card" href="file://__REPO__/classifier/FINDINGS.md">
    <div class="t">FINDINGS.md</div>
    <div class="d">Why 60.5% is agreement and not accuracy.</div></a>
  <a class="card" href="https://github.com/nyelugo/PROJECT-Capstone-AI-Consulting">
    <div class="t">The repository</div>
    <div class="d">github.com/nyelugo · public.</div></a>
</div>

<footer>
  Both apps keep running after you close this page.
  Stop them from a terminal with <code>pkill -f "streamlit run"</code>.<br>
  Rebuild this launcher with <code>./make_desktop_app.sh</code> after moving the project.
</footer>
</div>

<script>
// Liveness probe for the two local servers, so the buttons go live as each comes up
// instead of the launcher blocking for twenty seconds before anything appears.
//
// This uses an <img> and NOT fetch(). This page is opened from file://, whose origin is
// "null"; a cross-origin fetch from there is unreliable and can fail even when the server
// is answering, which would leave the dots amber on a working system — a status light
// that lies is worse than none. Loading an image is not origin-restricted, and Streamlit
// serves a real PNG at /favicon.png, so img.onload is a truthful "this port is answering".
const targets = [
  {id: "mvp",  port: 8502},
  {id: "dash", port: 8501},
];

function probe(port) {
  return new Promise((resolve) => {
    const img = new Image();
    const done = (ok) => { clearTimeout(timer); img.onload = img.onerror = null; resolve(ok); };
    const timer = setTimeout(() => done(false), 2500);
    img.onload  = () => done(true);
    img.onerror = () => done(false);
    img.src = "http://localhost:" + port + "/favicon.png?_=" + Date.now();
  });
}

let secs = 0;
async function tick() {
  secs++;
  let pending = 0;
  for (const t of targets) {
    const dot = document.getElementById("d-" + t.id);
    const st  = document.getElementById("s-" + t.id);
    if (dot.classList.contains("up")) continue;
    if (await probe(t.port)) {
      dot.classList.remove("down"); dot.classList.add("up");
      st.textContent = "ready · localhost:" + t.port;
    } else {
      pending++;
      dot.classList.add("down");
      st.textContent = secs > 75
        ? "did not start — check /tmp/capstone_*.log"
        : "starting… " + secs + "s";
    }
  }
  if (pending && secs < 90) setTimeout(tick, 1000);
}
tick();
</script>
</body></html>
HTML

/usr/bin/sed -i '' \
  -e "s|__REPO__|${REPO}|g" \
  -e "s|__N8N__|${N8N_URL}|g" \
  -e "s|__LSPROJ__|${LS_PROJECTS}|g" \
  -e "s|__LSEXP__|${LS_EXPERIMENT}|g" \
  "$APP/Contents/Resources/launchpad.html"

# ------------------------------------------------------------------- the launcher
cat > "$APP/Contents/MacOS/launcher" <<LAUNCHER
#!/usr/bin/env bash
REPO="$REPO"
HERE="\$(cd "\$(dirname "\$0")/../Resources" && pwd)"

fail() { /usr/bin/osascript -e "display dialog \\"\$1\\" with title \\"Capstone\\" buttons {\\"OK\\"} default button 1 with icon caution"; exit 1; }

cd "\$REPO" 2>/dev/null || fail "Cannot find the project at \$REPO. Has it moved? Re-run make_desktop_app.sh."

# Open the launchpad FIRST. It polls the ports itself, so something appears instantly
# even though the servers take a few seconds. A silent launcher that does nothing
# visible for twenty seconds gets double-clicked again, which starts a second copy.
/usr/bin/open "file://\$HERE/launchpad.html"

for p in "/opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh" \\
         "\$HOME/miniconda3/etc/profile.d/conda.sh" \\
         "/opt/homebrew/Caskroom/miniforge/base/etc/profile.d/conda.sh"; do
  [ -f "\$p" ] && . "\$p" && break
done
conda activate bootcamp-env 2>/dev/null || fail "Could not activate the bootcamp-env conda environment. The documents and the deck still work; the two live apps will not."

# Streamlit prompts for an email on first run and BLOCKS until answered, which would
# hang a double-click launch for ever. An empty credentials file dismisses it for good.
if [ ! -f "\$HOME/.streamlit/credentials.toml" ]; then
  mkdir -p "\$HOME/.streamlit"
  printf '[general]\\nemail = ""\\n' > "\$HOME/.streamlit/credentials.toml"
fi

start() {   # start(port, script, logname) — idempotent, so a second double-click is harmless
  /usr/bin/curl -s -o /dev/null --max-time 2 "http://localhost:\$1" && return 0
  nohup streamlit run "\$2" --server.port "\$1" --server.headless true \\
        --browser.gatherUsageStats false > "/tmp/capstone_\$3.log" 2>&1 &
}

[ -f data/complaints_dashboard.csv ] && start 8501 dashboard/app.py dashboard
[ -f mvp/synth/transactions.csv ]    && start 8502 mvp/app.py       mvp
exit 0
LAUNCHER

chmod +x "$APP/Contents/MacOS/launcher"
touch "$APP"

# The Round 1 launcher only started the dashboard and is now a strictly smaller subset
# of this one. Two shortcuts on a Desktop is the thing this was meant to remove.
[ -d "$OLD" ] && rm -rf "$OLD" && echo "removed superseded: $OLD"

echo "built: $APP"
echo "  double-click it: launchpad opens at once, both apps come up behind it"
echo "  stop the apps later:  pkill -f 'streamlit run'"
