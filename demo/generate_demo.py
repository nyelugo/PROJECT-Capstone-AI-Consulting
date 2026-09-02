"""Generate a narrated screen recording of a demo. No hand-timing, no drift.

    python -m demo.generate_demo mvp
    python -m demo.generate_demo poc --headed

How the two halves stay in step. Each cue names what is said and what happens on screen.
The narration is synthesised first, so its exact duration is known before the browser
starts. The recorder then performs the cue's action, and holds the frame for precisely that
duration. Whatever the action itself cost — a page load, a model call — is measured and the
same amount of silence is laid in front of that cue's audio afterwards. The soundtrack is
therefore assembled to fit the video that actually happened, rather than the video being
nudged to fit an assumed soundtrack.

Text-to-speech is lifted from PROJECT-Podcast-Studio (`src/tts_generator.py`, by Adam,
Anand and Ugo) — same OpenAI model and streaming-to-disk approach, kept deliberately
recognisable rather than rewritten.

Needs: playwright (with a chromium build), ffmpeg, and OPENAI_API_KEY.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from demo.cues import SCRIPTS                                    # noqa: E402
from mvp.runtime import env                                      # noqa: E402

HERE = Path(__file__).resolve().parent
WORK = HERE / "build"
OUT = HERE / "recordings"
PROFILE = HERE / ".browser-profile"      # gitignored; holds the n8n session, never a key

TTS_MODEL = "tts-1"
VOICE = "nova"                       # Podcast Studio's default, kept for continuity
# 1600 wide because the triage table is clipped at 1440 — the "Why held"
# column, which carries the reason code, was cut off in the first recording.
VIEWPORT = {"width": 1600, "height": 1000}
PAD_AFTER_CUE = 0.45                 # a beat between cues, so it does not feel rushed


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed: {(p.stderr or p.stdout)[-600:]}")
    return p


def duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", str(path)]).stdout.strip()
    return float(out)


# ------------------------------------------------------------------------------ narration

def narrate(script: list[dict], voice: str) -> list[Path]:
    """One mp3 per cue. Cached on the text, so re-running after a wording change only
    re-synthesises the cues that changed — this is the slow and the only paid step."""
    from openai import OpenAI
    key = env("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY is not set. Add it to ~/.config/ironhack/.env.local")
    client = OpenAI(api_key=key)

    seg_dir = WORK / "narration"
    seg_dir.mkdir(parents=True, exist_ok=True)
    cache_file = seg_dir / "cache.json"
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}

    paths = []
    for i, cue in enumerate(script):
        p = seg_dir / f"{i:02d}.mp3"
        if cache.get(str(i)) == cue["say"] and p.exists():
            print(f"  [{i:02d}] cached")
        else:
            print(f"  [{i:02d}] speaking {len(cue['say'].split())} words…")
            with client.audio.speech.with_streaming_response.create(
                    model=TTS_MODEL, voice=voice, input=cue["say"]) as r:
                r.stream_to_file(p)
            cache[str(i)] = cue["say"]
        paths.append(p)
    cache_file.write_text(json.dumps(cache, indent=2))
    return paths


# -------------------------------------------------------------------------------- capture

SELECT_ROW = """
(n) => {
  const grid = document.querySelector('[data-testid="stDataFrame"]');
  if (!grid) return false;
  const c = grid.querySelector('canvas'); const b = grid.getBoundingClientRect();
  // The grid is a canvas, so a DOM click does nothing — the checkbox column has to be hit
  // with real pointer events at the row's coordinates.
  const o = {bubbles: true, cancelable: true, clientX: b.left + 16,
             clientY: b.top + 52 + n * 35, button: 0, pointerId: 1,
             pointerType: 'mouse', isPrimary: true, detail: 1};
  ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(t =>
    c.dispatchEvent(new (t.startsWith('pointer') ? PointerEvent : MouseEvent)(t, o)));
  return true;
}
"""



# ------------------------------------------------------------------------------- cursor
# Playwright dispatches input without moving a pointer, and the OS cursor is not captured
# in the video either — so the first cut had nothing moving on screen at all. A demo where
# the viewer cannot see what is being pointed at is a slideshow with a voiceover.
#
# So: an arrow drawn INTO the page, kept in step with real mouse movement. The mouse moves
# for real (so the app receives genuine events, including on the canvas grid where
# synthetic dispatch was needed before), and the drawn arrow follows it frame by frame.
CURSOR_JS = """
() => {
  if (document.getElementById('demo-cursor')) return;
  const c = document.createElement('div');
  c.id = 'demo-cursor';
  c.style.cssText = 'position:fixed;left:0;top:0;width:26px;height:26px;z-index:2147483647;'
    + 'pointer-events:none;transition:transform .06s linear;will-change:transform;'
    + 'filter:drop-shadow(0 2px 4px rgba(0,0,0,.45))';
  c.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26">'
    + '<path d="M5 2 L5 20 L10 15.5 L13 22 L16 20.5 L13 14.5 L19.5 14.5 Z" '
    + 'fill="#ffffff" stroke="#1D2A32" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  document.body.appendChild(c);

  const ring = document.createElement('div');
  ring.id = 'demo-ring';
  ring.style.cssText = 'position:fixed;left:0;top:0;width:40px;height:40px;border-radius:50%;'
    + 'border:3px solid #2a78d6;opacity:0;z-index:2147483646;pointer-events:none;'
    + 'margin:-20px 0 0 -20px';
  document.body.appendChild(ring);

  window.__cur = (x, y) => {
    c.style.transform = `translate(${x}px, ${y}px)`;
    ring.style.left = x + 'px';
    ring.style.top = y + 'px';
  };
  window.__ping = () => {
    ring.animate(
      [{opacity: 1, transform: 'scale(.35)'}, {opacity: 0, transform: 'scale(1.9)'}],
      {duration: 650, easing: 'ease-out'});
  };
}
"""


def ensure_cursor(page) -> None:
    """Idempotent. Streamlit reruns keep the node, a navigation does not."""
    try:
        page.evaluate(CURSOR_JS)
    except Exception:
        pass


def glide(page, x: float, y: float, steps: int = 26) -> None:
    """Move the real mouse to (x, y) along an eased path, arrow following.

    Eased rather than linear because a constant-velocity cursor reads as a machine. This
    is the one place in the project where looking human is the actual requirement.
    """
    ensure_cursor(page)
    sx, sy = page.evaluate("() => window.__mx ?? [80, 80]") if False else (
        getattr(page, "_demo_x", 80.0), getattr(page, "_demo_y", 80.0))
    for i in range(1, steps + 1):
        u = i / steps
        e = 1 - (1 - u) ** 3                       # ease-out cubic
        nx, ny = sx + (x - sx) * e, sy + (y - sy) * e
        page.mouse.move(nx, ny)
        page.evaluate("([x, y]) => window.__cur && window.__cur(x, y)", [nx, ny])
        page.wait_for_timeout(12)
    page._demo_x, page._demo_y = x, y


def in_main(page, text: str):
    """Find text in the CONTENT area, never the sidebar.

    `get_by_text("Checks")` matched the sidebar caption "...all run the same six checks"
    before it reached the Checks panel, so the cursor confidently pointed at the wrong
    thing while the narrator described the right one. Scoping to stMain removes a whole
    class of that: the sidebar repeats a lot of the vocabulary the narration uses.
    """
    return (page.locator('[data-testid="stMain"]')
            .get_by_text(text, exact=False).locator("visible=true").first)


def centre_of(page, locator) -> tuple[float, float]:
    locator.scroll_into_view_if_needed(timeout=6000)
    page.wait_for_timeout(350)
    b = locator.bounding_box()
    if not b:
        raise RuntimeError("element has no box on screen")
    return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2


def click_at(page, x: float, y: float) -> None:
    glide(page, x, y)
    page.wait_for_timeout(320)                     # a beat before pressing, as a person does
    page.evaluate("() => window.__ping && window.__ping()")
    page.wait_for_timeout(220)                     # let the ripple start before the rerun
    page.mouse.click(x, y)


def settle(page, seconds: float = 2.5) -> None:
    """Streamlit reruns on every interaction; give it time to finish drawing."""
    try:
        page.wait_for_load_state("networkidle", timeout=int(seconds * 1000))
    except Exception:
        pass
    page.wait_for_timeout(int(seconds * 1000))


def act(page, do: tuple) -> None:
    kind, arg = do
    if kind == "goto":
        page.goto(arg, wait_until="domcontentloaded")
        settle(page, 4)
        ensure_cursor(page)
        glide(page, 300, 260, steps=18)            # bring the pointer on screen gently

    elif kind == "nav":
        loc = page.locator(f'section[data-testid="stSidebar"] a:has-text("{arg}")').first
        try:
            x, y = centre_of(page, loc)
        except Exception:
            pages = page.eval_on_selector_all(
                'section[data-testid="stSidebar"] a',
                "els => els.map(e => e.innerText.replace(/\\n+/g, ' ').trim())")
            raise RuntimeError(f"no sidebar page matching {arg!r}. Pages: "
                               + ", ".join(repr(p) for p in pages if p)) from None
        click_at(page, x, y)
        settle(page, 3)
        ensure_cursor(page)

    elif kind == "click":
        loc = page.locator(f'button:has-text("{arg}")').first
        try:
            x, y = centre_of(page, loc)
        except Exception:
            labels = page.eval_on_selector_all(
                "button", "els => els.map(e => e.innerText.replace(/\\n+/g, ' ').trim())")
            raise RuntimeError(
                f"no button matching {arg!r}. Buttons on the page: "
                + ", ".join(repr(x) for x in labels if x)) from None
        click_at(page, x, y)
        settle(page, 3)
        ensure_cursor(page)

    elif kind == "point":
        # Move to a thing WITHOUT clicking it, so the viewer's eye goes where the narration
        # is. This is what makes a talking cue watchable instead of a still frame.
        try:
            x, y = centre_of(page, in_main(page, arg))
        except Exception:
            print(f"       (point at {arg!r} skipped — not on screen)")
            return
        glide(page, x, y)

    elif kind == "row":
        # Real mouse on the canvas grid's checkbox column. The earlier synthetic dispatch
        # worked but was invisible; a genuine click is both visible and closer to the truth.
        grid = page.locator('[data-testid="stDataFrame"]').first
        grid.scroll_into_view_if_needed(timeout=6000)
        b = grid.bounding_box()
        if not b:
            raise RuntimeError("the data grid is not on screen")
        click_at(page, b["x"] + 16, b["y"] + 52 + int(arg) * 35)
        settle(page, 3)
        ensure_cursor(page)

    elif kind == "scroll_to":
        try:
            in_main(page, arg).scroll_into_view_if_needed(timeout=4000)
        except Exception:
            print(f"       (scroll_to {arg!r} skipped — not visible or already in view)")
        page.wait_for_timeout(1100)
        ensure_cursor(page)

    elif kind == "wait":
        page.wait_for_timeout(int(float(arg) * 1000))

    else:
        raise ValueError(f"unknown action {kind!r}")


def looks_like_login(page) -> bool:
    """Is this a sign-in wall rather than the thing we came to film?

    Worth checking explicitly: without it the recorder happily produces a beautifully
    narrated two-minute film of a login form, and you find out when you watch it.
    """
    if any(k in page.url.lower() for k in ("/signin", "/login", "/auth")):
        return True
    return page.locator('input[type="password"]').count() > 0


def open_login(url: str) -> int:
    """Log in once, by hand, into the profile the recorder reuses."""
    from playwright.sync_api import sync_playwright
    print(f"opening {url} — sign in, then close the window.")
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(str(PROFILE), headless=False,
                                                    viewport=VIEWPORT)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")
        try:
            page.wait_for_event("close", timeout=600000)
        except Exception:
            pass
        ctx.close()
    print("session saved to the recorder's profile.")
    return 0


def capture(script: list[dict], segs: list[Path], headed: bool) -> tuple[Path, list[float]]:
    """Drive the browser, recording. Returns the video and the action time per cue."""
    from playwright.sync_api import sync_playwright

    vid_dir = WORK / "video"
    shutil.rmtree(vid_dir, ignore_errors=True)
    vid_dir.mkdir(parents=True, exist_ok=True)

    lead_in = []
    with sync_playwright() as pw:
        # A persistent profile, so a gated target (the cohort n8n instance) can be logged
        # into once and stay logged in. Nothing secret is stored by us — it is the browser's
        # own cookie jar, and the directory is gitignored.
        ctx = pw.chromium.launch_persistent_context(
            str(PROFILE), headless=not headed, viewport=VIEWPORT,
            record_video_dir=str(vid_dir), record_video_size=VIEWPORT)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.wait_for_timeout(1200)                     # a moment of stillness to open on
        for i, (cue, seg) in enumerate(zip(script, segs)):
            t0 = time.monotonic()
            act(page, cue["do"])
            if i == 0 and looks_like_login(page):
                ctx.close()
                raise RuntimeError(
                    "that URL is showing a sign-in page, so the recording would be of a "
                    "login form.\n  Run:  python -m demo.generate_demo "
                    f"{'poc'} --login    then sign in and close the window.")
            spent = time.monotonic() - t0
            lead_in.append(spent)
            speak = duration(seg)
            print(f"  [{i:02d}] action {spent:5.1f}s · narration {speak:5.1f}s")
            page.wait_for_timeout(int((speak + PAD_AFTER_CUE) * 1000))
        page.wait_for_timeout(1200)
        ctx.close()                                     # video is only written on close

    vids = list(vid_dir.glob("*.webm"))
    if not vids:
        raise RuntimeError("playwright wrote no video")
    return vids[0], lead_in


# ---------------------------------------------------------------------------------- mux

def build_audio(segs: list[Path], lead_in: list[float]) -> Path:
    """Assemble the soundtrack to match the video that actually happened.

    Each cue's narration is preceded by exactly as much silence as its action took, so the
    words land when the thing they describe is already on screen.
    """
    a_dir = WORK / "audio"
    shutil.rmtree(a_dir, ignore_errors=True)
    a_dir.mkdir(parents=True, exist_ok=True)

    parts = []
    # Everything is normalised to one wav format first; the concat demuxer can only copy
    # streams that already agree, and the TTS mp3s do not agree with generated silence.
    fmt = ["-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le"]
    head = a_dir / "head.wav"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", "1.2", *fmt, str(head)])
    parts.append(head)

    for i, (seg, lead) in enumerate(zip(segs, lead_in)):
        if lead > 0.05:
            s = a_dir / f"{i:02d}_gap.wav"
            run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                 "-t", f"{lead:.3f}", *fmt, str(s)])
            parts.append(s)
        w = a_dir / f"{i:02d}.wav"
        run(["ffmpeg", "-y", "-i", str(seg), *fmt, str(w)])
        parts.append(w)
        pad = a_dir / f"{i:02d}_pad.wav"
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", f"{PAD_AFTER_CUE:.3f}", *fmt, str(pad)])
        parts.append(pad)

    listing = a_dir / "list.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    track = a_dir / "track.wav"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt",
         "-c", "copy", "track.wav"], cwd=a_dir)
    return track


def mux(video: Path, track: Path, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(video), "-i", str(track),
         "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         "-shortest", str(out)])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("script", choices=sorted(SCRIPTS))
    ap.add_argument("--headed", action="store_true",
                    help="watch it record; useful when a selector stops matching")
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--login", action="store_true",
                    help="open the target headed so you can sign in once; the recorder "
                         "reuses that session afterwards")
    a = ap.parse_args()

    if a.login:
        from demo.cues import MVP_URL, POC_URL
        return open_login(POC_URL if a.script == "poc" else MVP_URL)

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} is not on PATH.")

    script = SCRIPTS[a.script]
    WORK.mkdir(parents=True, exist_ok=True)

    print(f"narrating {len(script)} cues…")
    segs = narrate(script, a.voice)

    print("recording…")
    try:
        video, lead_in = capture(script, segs, a.headed)
    except RuntimeError as exc:
        sys.stdout.flush()          # so the message lands after the progress, not before
        # These are the expected failures — a sign-in wall, a renamed button. They deserve
        # the sentence, not a traceback; the traceback tells you Python was upset, the
        # sentence tells you what to do about it.
        sys.exit(f"\n{exc}")

    print("assembling the soundtrack…")
    track = build_audio(segs, lead_in)

    out = OUT / f"{a.script}_demo.mp4"
    print("muxing…")
    mux(video, track, out)

    d = duration(out)
    mm, ss = divmod(int(round(d)), 60)
    print(f"\nwrote {out.relative_to(Path.cwd()) if out.is_relative_to(Path.cwd()) else out}"
          f"  —  {mm}:{ss:02d}  ({out.stat().st_size / 1e6:.1f} MB)")
    if a.script == "poc" and not (2 * 60 <= d <= 5 * 60):
        print("  NOTE: deliverable 2 wants 2-5 minutes; pf-05 gives slide 4 a 2-3 min slot.")
    if a.script == "mvp" and d > 2 * 60:
        print("  NOTE: pf-05 gives slide 9 one to two minutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
