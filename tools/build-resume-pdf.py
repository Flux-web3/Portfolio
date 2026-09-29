#!/usr/bin/env python3
"""Build the 2-page résumé PDF: Enhancv page 1 + generated page 2.

Why it works this way: page 1 of Olamide-Olanipekun-Product-Manager.pdf is an
export from Enhancv (the résumé builder), and it is full. Enhancv cannot be
scripted, and re-rendering its page would lose fidelity, so page 1 is kept
exactly as exported: its PDF page object (content stream, fonts, links) is
copied unchanged. Page 2 ("PROJECTS") is generated from tools/resume-page2.html
with headless Chrome. That HTML copies page 1's left-column styling, measured
from the Enhancv PDF.

Steps:
  1. Render tools/resume-page2.html to a temporary 1-page PDF with headless
     Chrome (Google Fonts: Rubik and Inter, the fonts page 1 uses).
  2. Check the render: exactly 1 page, and Rubik/Inter are embedded (not
     fallback fonts).
  3. Write ONLY page index 0 of the current résumé PDF, then the rendered page,
     back to the résumé PDF. Enhancv's document metadata is kept.

Running the script again gives the same result, because it always takes just
page 0 of the current file (the Enhancv page) and appends a fresh page 2.

Usage:  python tools/build-resume-pdf.py [--chrome PATH]
Needs:  Python 3 with pypdf, Google Chrome, network access (Google Fonts).
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "Olamide-Olanipekun-Product-Manager.pdf"
PAGE2_HTML = ROOT / "tools" / "resume-page2.html"

CHROME_CANDIDATES = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chrome") or "",
]

REQUIRED_FONTS = ("Rubik", "Inter")

# Enhancv lays page 1 out in CSS px on a 939.5 px-wide canvas at 0.634309 pt
# per px (its content stream: 0.24 x 2.6429522). The HTML uses the same px.
DESIGN_PX_PT = 0.24 * 2.6429522
CSS_PX_PT = 0.75


def find_chrome(explicit: str | None) -> str:
    for c in [explicit or ""] + CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    sys.exit("Chrome not found; pass --chrome PATH or set CHROME_PATH.")


def render_page2(chrome: str, out_pdf: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="resume-chrome-") as profile:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-data-dir={profile}",   # isolated profile: never touches a running Chrome
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=20000",  # let Google Fonts load before printing
            f"--print-to-pdf={out_pdf}",
            PAGE2_HTML.as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if not out_pdf.exists() or out_pdf.stat().st_size == 0:
            sys.exit(f"Chrome did not produce a PDF.\n{res.stdout}\n{res.stderr}")


def embedded_fonts(page) -> set[str]:
    """/BaseFont names (subset prefix removed) used by the page, including fonts
    inside Form XObjects (Chrome draws transformed content into forms)."""
    names: set[str] = set()

    def walk(res, depth=0):
        res = res.get_object() if hasattr(res, "get_object") else res
        if not res or depth > 8:
            return
        for f in res.get("/Font", {}).values():
            base = str(f.get_object().get("/BaseFont", ""))
            names.add(base.split("+", 1)[-1].lstrip("/"))
        for x in res.get("/XObject", {}).values():
            x = x.get_object()
            if x.get("/Subtype") == "/Form":
                walk(x.get("/Resources", {}), depth + 1)

    walk(page.get("/Resources", {}))
    return names


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--chrome", help="path to the Chrome/Chromium executable")
    args = ap.parse_args()

    chrome = find_chrome(args.chrome)
    # Load the current résumé fully into memory (it is overwritten below).
    src = PdfReader(io.BytesIO(RESUME.read_bytes()))
    page1 = src.pages[0]

    with tempfile.TemporaryDirectory(prefix="resume-page2-") as tmp:
        tmp_pdf = Path(tmp) / "page2.pdf"
        render_page2(chrome, tmp_pdf)
        rendered = PdfReader(io.BytesIO(tmp_pdf.read_bytes()))

    if len(rendered.pages) != 1:
        sys.exit(f"Page 2 rendered to {len(rendered.pages)} pages; it must fit on one. Shorten the text.")
    page2 = rendered.pages[0]

    fonts = embedded_fonts(page2)
    missing = [f for f in REQUIRED_FONTS if not any(n.startswith(f) for n in fonts)]
    if missing:
        sys.exit(f"Web fonts did not load (embedded: {sorted(fonts)}); missing {missing}. Check network access.")

    # The HTML is printed on a design-px sheet (939.5 x 1328.8 CSS px = 704.6 x
    # 996.6 pt). Scale it uniformly onto page 1's box (Enhancv: 595.92 x 842.88
    # pt, 0.634309 pt per design px). This also scales the link rectangles.
    w1, h1 = float(page1.mediabox.width), float(page1.mediabox.height)
    w2, h2 = float(page2.mediabox.width), float(page2.mediabox.height)
    # Use Enhancv's exact scale rather than w1/w2: Chrome rounds the paper size
    # up slightly (e.g. 705.12 pt instead of 704.63), and the layout starts at
    # the top-left, so the excess is blank margin that the box below crops.
    k = DESIGN_PX_PT / CSS_PX_PT
    if abs(w2 * k - w1) > 2.0 or abs(h2 * k - h1) > 2.0:
        sys.exit(f"Unexpected sheet size: page 1 {w1}x{h1} pt, rendered {w2}x{h2} pt.")
    page2.scale(k, k)
    # Pin the boxes to page 1's exactly. Keep the top-left corner fixed, as
    # page 1's content is laid out from the top.
    dy = h1 - h2 * k
    if abs(dy) > 1e-6:
        page2.add_transformation((1, 0, 0, 1, 0, dy))
        for a in page2.get("/Annots") or []:
            r = a.get_object()["/Rect"]
            r[1] = type(r[1])(float(r[1]) + dy)
            r[3] = type(r[3])(float(r[3]) + dy)
    page2.mediabox = page1.mediabox
    page2.cropbox = page1.mediabox
    for box in ("/TrimBox", "/BleedBox", "/ArtBox"):
        if box in page2:
            del page2[box]

    writer = PdfWriter()
    writer.add_page(page1)          # Enhancv page, unchanged
    writer.add_page(page2)          # generated PROJECTS page

    meta = {str(k): v for k, v in (src.metadata or {}).items()}
    meta["/Producer"] = "Enhancv (page 1); headless Chrome + pypdf (page 2)"
    meta["/ModDate"] = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%SZ")
    writer.add_metadata(meta)

    buf = io.BytesIO()
    writer.write(buf)
    tmp_out = RESUME.with_suffix(".pdf.tmp")
    tmp_out.write_bytes(buf.getvalue())
    os.replace(tmp_out, RESUME)

    print(f"Wrote {RESUME.name}: 2 pages, page 2 fonts {sorted(fonts)}")


if __name__ == "__main__":
    main()
