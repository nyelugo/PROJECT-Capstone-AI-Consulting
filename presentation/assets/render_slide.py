"""Re-render slide 4 from its HTML source and put it back into the deck.

The slide is a PNG inside presentation.pptx. Edit decision_spine_slide.html, run this, and
the deck picks up the new image with nothing else touched — the package is rewritten part by
part and only ppt/media/image1.png is replaced.

    python presentation/assets/render_slide.py

Needs playwright with a chromium build (the same one demo/generate_demo.py uses).
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE.parents[1] / "presentation.pptx"
SRC = HERE / "decision_spine_slide.html"
PNG = HERE / "decision_spine_slide.png"
# the deck's content band: 13.333in x 6.95in of a 13.333 x 7.5 page
W, H = 1600, 834


def render() -> None:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": W, "height": H},
                            device_scale_factor=2, color_scheme="light")
        page = ctx.new_page()
        page.goto(SRC.as_uri(), wait_until="networkidle", timeout=60_000)
        # the board is authored at 900 tall; retune it to the band so nothing is cropped
        page.evaluate("(h) => {const s=document.getElementById('slide');"
                      "s.style.height=h+'px'; s.style.paddingBottom='30px';}", H)
        page.wait_for_timeout(1500)
        over = page.evaluate("() => {const s=document.getElementById('slide');"
                             "return s.scrollHeight - s.clientHeight;}")
        if over > 0:
            raise SystemExit(f"content overflows the band by {over}px — shorten it or the "
                             f"render will be cropped")
        page.screenshot(path=str(PNG), clip={"x": 0, "y": 0, "width": W, "height": H})
        ctx.close(); b.close()


def swap_into_deck() -> None:
    """Replace only ppt/media/image1.png, copying every other part byte-for-byte."""
    backup = DECK.with_suffix(".pptx.bak")
    shutil.copy2(DECK, backup)
    src = zipfile.ZipFile(backup)
    tmp = DECK.with_suffix(".tmp.pptx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for item in src.infolist():
            data = PNG.read_bytes() if item.filename == "ppt/media/image1.png" else src.read(item.filename)
            out.writestr(item, data)
    src.close()
    tmp.replace(DECK)
    a, b = zipfile.ZipFile(backup), zipfile.ZipFile(DECK)
    diff = [n for n in a.namelist() if a.read(n) != b.read(n)]
    print(f"  parts differing: {diff or 'none — the render was identical'}")
    # an unchanged render is the common case and is not a failure; anything OTHER than the
    # image having moved is
    if set(diff) - {"ppt/media/image1.png"}:
        raise SystemExit("blast radius wider than the image — restore from the .bak and stop")
    backup.unlink()
    print("  deck updated. Re-export the PDF: "
          "soffice --headless --convert-to pdf --outdir . presentation.pptx")


if __name__ == "__main__":
    render()
    print(f"  rendered {PNG.name}")
    swap_into_deck()
    sys.exit(0)
