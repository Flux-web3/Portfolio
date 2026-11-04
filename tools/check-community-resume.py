#!/usr/bin/env python3
"""Validate the committed Community Management résumé PDF."""
from pathlib import Path
from pypdf import PdfReader

PDF = Path(__file__).resolve().parent.parent / "Olamide_Olanipekun_Community_Management_Resume.pdf"
if not PDF.is_file():
    raise SystemExit(f"FAIL: missing Community Management PDF: {PDF}")
reader = PdfReader(str(PDF))
if len(reader.pages) != 2:
    raise SystemExit(f"FAIL: Community Management PDF must be exactly two pages; got {len(reader.pages)}")
pages = []
for n, page in enumerate(reader.pages, start=1):
    width, height = float(page.mediabox.width), float(page.mediabox.height)
    if abs(width - 595.276) > 1 or abs(height - 841.89) > 1:
        raise SystemExit(f"FAIL: page {n} is not A4")
    pages.append(" ".join((page.extract_text() or "").split()))
text = " ".join(pages)
required = [
    "OLAMIDE OLANIPEKUN", "WEB3 COMMUNITY MANAGER", "Apr 2025", "May 2026",
    "Built and owned the YNX community from scratch", "moderators, marketing talent, and developers",
    "Product Manager & Growth Operations Lead", "Sep 2022", "Dec 2023",
    "Community & Customer support specialist", "May 2022", "six-person Discord and Telegram team",
    "two-person website support team", "5,000 members", "5–15 minutes",
    "Community Manager", "Gotabit", "Feb 2021", "Oct 2022",
    "Community Management & Growth Contributor", "Betboom", "Jan 2020", "Sep 2021",
    "50,000 members", "5–7 minutes", "B.Sc.Ed.", "University of Lagos"
]
missing = [item for item in required if item.casefold() not in text.casefold()]
if missing:
    raise SystemExit("FAIL: Community PDF is missing current résumé facts: " + "; ".join(missing))
for stale in ["50% reduction in operational bottlenecks", "community ownership at Deserialize"]:
    if stale.casefold() in text.casefold():
        raise SystemExit(f"FAIL: Community PDF contains stale or excluded claim: {stale}")
if not text.strip():
    raise SystemExit("FAIL: Community PDF has no extractable text layer")
print("PASS: two-page A4 Community Management PDF contains YNX ownership and sourcing, both distinct Limitless roles, Gotabit, Betboom, dates, support metrics, and an ATS-readable text layer.")
