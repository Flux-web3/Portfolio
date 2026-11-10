#!/usr/bin/env python3
"""Validate the committed PM PDF and the current generated build."""
from pathlib import Path
import sys
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
COMMITTED = ROOT / "Olamide-Olanipekun-Product-Manager.pdf"
ARGS = [arg for arg in sys.argv[1:] if arg != "--generated-only"]
GENERATED = Path(ARGS[0]) if ARGS else COMMITTED
GENERATED_ONLY = "--generated-only" in sys.argv[1:]

def read_pdf(path: Path):
    if not path.is_file():
        raise SystemExit(f"FAIL: missing PDF: {path}")
    reader = PdfReader(str(path))
    if len(reader.pages) != 2:
        raise SystemExit(f"FAIL: {path.name} must be two pages; got {len(reader.pages)}")
    page_texts = []
    for page_number, page in enumerate(reader.pages, start=1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if abs(width - 595.276) > 1 or abs(height - 841.89) > 1:
            raise SystemExit(f"FAIL: {path.name} page {page_number} is not A4")
        page_text = " ".join((page.extract_text() or "").split())
        if not page_text:
            raise SystemExit(f"FAIL: {path.name} page {page_number} has no extractable text")
        samples = []
        def collect(text, cm, tm, font_dict, font_size):
            if text.strip():
                try:
                    samples.append((float(font_size), len(text.strip())))
                except (TypeError, ValueError):
                    pass
        page.extract_text(visitor_tex¶»§q«^