#!/usr/bin/env python3
"""Validate committed and regenerated Community Management résumé PDFs."""
from pathlib import Path
import sys
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
COMMITTED = ROOT / "Olamide_Olanipekun_Community_Management_Resume.pdf"
args = [arg for arg in sys.argv[1:] if arg != "--generated-only"]
GENERATED = Path(args[0]) if args else COMMITTED
GENERATED_ONLY = "--generated-only" in sys.argv[1:]

REQUIRED = [
    "OLAMIDE OLANIPEKUN", "WEB3 COMMUNITY MANAGER",
    "Apr 2025", "May 2026", "Built and owned the YNX community from scratch",
    "Sourced moderators", "marketing talent", "developers",
    "Product Manager & Growth Operations Lead", "Sep 2022", "Dec 2023",
    "Community & Customer support specialist", "May 2022",
    "six-person Discord and Telegram team", "two-person website support team",
    "5,000 members", "5–15 minutes", "Community Manager", "Gotabit",
    "Feb 2021", "Oct 2022", "Community Management & Growth Contributor",
    "Betboom", "Jan 2020", "Sep 2021", "50,000 members", "5–7 minutes",
    "University of Lagos", "B.Sc.Ed., Mathematics and Education", "Second Class Upper"
]
EXCLUDED = ["50% reduction in operational bottlenecks", "community ownership at Deserialize", "CGPA", "Completed 2026", "3.8/5"]

def inspect(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"FAIL: missing Community Management PDF: {path}")
    reader = PdfReader(str(path), strict=True)
    if len(reader.pages) != 2:
        raise SystemExit(f"FAIL: {path.name} must be exactly two pages; got {len(reader.pages)}")
    parts = []
    for page_number, page in enumerate(reader.pages, start=1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if abs(width - 595.276) > 1 or abs(height - 841.89) > 1:
            raise SystemExit(f"FAIL: {path.name} page {page_number} is not A4")
        page_text = " ".join((page.extract_text() or "").split())
        if not page_text:
            raise SystemExit(f"FAIL: {path.name} page {page_number} has no extractable text")
        if any(ord(ch) < 32 and ch not in "\t\n\r" for ch in page_text):
            raise SystemExit(f"FAIL: {path.name} page {page_number} contains control characters")
        samples = []
        def collect(text, cm, tm, font_dict, font_size):
            if text.strip():
                try:
                    samples.append((float(font_size), len(text.strip())))
                except (TypeError, ValueError):
                    pass
        page.extract_text(visitor_text=collect)
        total_chars = sum(count for _, count in samples)
        readable_chars = sum(count for size, count in samples if size >= 10.0)
        if not total_chars or readable_chars / total_chars < 0.65:
            raise SystemExit(f"FAIL: {path.name} page {page_number} does not use the required larger 10 pt principal typography")
        parts.append(page_text)
    if "community & customer support specialist" not in parts[0].casefold():
        raise SystemExit(f"FAIL: {path.name} page 1 did not reach the Limitless Community & Customer support role after natural flow. Last extracted text: {parts[0][-260:]}")
    content = " ".join(parts)
    missing = [term for term in REQUIRED if term.casefold() not in content.casefold()]
    if missing:
        raise SystemExit(f"FAIL: {path.name} is missing current résumé facts: " + "; ".join(missing))
    stale = [term for term in EXCLUDED if term.casefold() in content.casefold()]
    if stale:
        raise SystemExit(f"FAIL: {path.name} contains stale or excluded claims: " + "; ".join(stale))

# Always validate the freshly generated PDF before considering the committed copy.
inspect(GENERATED)
if not GENERATED_ONLY:
    inspect(COMMITTED)
print("PASS: " + ("generated " if GENERATED_ONLY else "committed and regenerated ") +
      "Community Management PDF(s) are two-page A4, ATS-readable, and retain YNX ownership and sourcing, both concurrent Limitless positions, Gotabit and Betboom dates, support metrics, and B.Sc.Ed. qualification from the University of Lagos, with Second Class Upper classification.")
