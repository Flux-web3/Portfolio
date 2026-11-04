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
    for page_number, page in enumerate(reader.pages, start=1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if abs(width - 595.276) > 1 or abs(height - 841.89) > 1:
            raise SystemExit(f"FAIL: {path.name} page {page_number} is not A4")
    text = " ".join(" ".join((page.extract_text() or "").split()) for page in reader.pages)
    return text

required = [
    "Olamide Olanipekun",
    "4+ years of hands-on product management experience",
    "7+ years of broader experience",
    "$30M+", "40%", "30%",
    "YNX | Apr 2025 - May 2026",
    "Built and owned the YNX community from scratch",
    "Sourced moderator talent, marketing talent, and developers",
    "Dextopus | Aug 2025 - Feb 2026",
    "Debonk Bot | Jun 2025 - Jan 2026",
    "Deserialize | Apr 2024 - May 2025",
    "Limitless Prop Firm | May 2022 - Dec 2023",
    "Gotabit | Feb 2021 - Oct 2022",
    "Betboom | Jan 2020 - Sep 2021",
    "intermediate retail crypto and forex traders",
    "currently paused",
    "manual/CSV journaling",
    "B.Sc.Ed., Mathematics and Education",
]
stale = (
    "50% reduction in operational bottlenecks",
    "in active development",
    "futures, stock, and prop-firm traders",
    "Dextopus Bridge",
    "Community & Customer support specialist",
)

checks = (("generated", GENERATED),) if GENERATED_ONLY else (("committed", COMMITTED), ("generated", GENERATED))
for label, path in checks:
    text = read_pdf(path)
    missing = [item for item in required if item.casefold() not in text.casefold()]
    if missing:
        raise SystemExit(f"FAIL: {label} PM PDF missing current facts: " + "; ".join(missing))
    if chr(127) in text or any(ord(ch) < 32 and ord(ch) not in (9, 10, 13) for ch in text):
        raise SystemExit(f"FAIL: {label} PM PDF contains control characters in its text layer")
    found_stale = [item for item in stale if item.casefold() in text.casefold()]
    if found_stale:
        raise SystemExit(f"FAIL: {label} PM PDF contains excluded/stale statements: " + "; ".join(found_stale))

if not GENERATED_ONLY and COMMITTED.resolve() != GENERATED.resolve() and COMMITTED.read_bytes() != GENERATED.read_bytes():
    raise SystemExit("FAIL: committed Product Manager PDF differs from the canonical generated output. Regenerate and commit the PDF with tools/build-pm-resume.py.")

print("PASS: " + ("generated " if GENERATED_ONLY else "committed and generated ") + "PM PDF(s) are two-page A4 with all seven role dates, YNX community ownership and sourcing, metrics, Limitless full-date exception, FortaFlow scope/status, and education verified.")
