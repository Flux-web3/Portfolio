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
        page.extract_text(visitor_text=collect)
        total_chars = sum(count for _, count in samples)
        readable_chars = sum(count for size, count in samples if size >= 10.0)
        if not total_chars or readable_chars / total_chars < 0.65:
            raise SystemExit(f"FAIL: {path.name} page {page_number} does not use the required larger 10 pt principal typography")
        page_texts.append(page_text)
    page_two_start = page_texts[1][:650].casefold()
    valid_page_two_starts = (
        "product manager | deserialize",
        "product manager & growth operations lead | limitless prop firm",
    )
    if not any(marker in page_two_start for marker in valid_page_two_starts):
        raise SystemExit(
            f"FAIL: {path.name} page 2 must begin with a complete Deserialize or Limitless role. "
            f"Page 2 starts: {page_texts[1][:260]}"
        )
    expected_links = {
        "https://www.linkedin.com/in/olanipekun-olamide-flux-939a34235/",
        "https://olamide-olanipekun.vercel.app/#/",
        "https://github.com/Flux-web3",
        "https://t.me/king_flux",
        "https://www.datacamp.com/completed/statement-of-accomplishment/course/d2b403c9775c6f044933a0f0c04b995599f52745",
        "https://www.datacamp.com/completed/statement-of-accomplishment/course/639e3d23f56331e4778550bfe3a969aad4971fcc",
        "https://www.datacamp.com/completed/statement-of-accomplishment/course/65fee3ea851aa182dd6c8d6487c9c8d04182cf49",
    }
    actual_links = {
        str(a.get_object().get("/A", {}).get("/URI"))
        for page in reader.pages for a in (page.get("/Annots") or [])
        if a.get_object().get("/A", {}).get("/URI")
    }
    if actual_links != expected_links:
        missing_links = expected_links - actual_links
        unexpected_links = actual_links - expected_links
        details = []
        if missing_links:
            details.append("missing: " + "; ".join(sorted(missing_links)))
        if unexpected_links:
            details.append("unexpected: " + "; ".join(sorted(unexpected_links)))
        raise SystemExit(f"FAIL: {path.name} clickable link audit failed: " + " | ".join(details))
    extracted = " ".join(page_texts)
    if "flux.fx05@gmail.com" not in extracted:
        raise SystemExit(f"FAIL: {path.name} must show the email address as readable text")
    if "FortaFlow | Independent Product Builder" not in extracted:
        raise SystemExit(f"FAIL: {path.name} must retain FortaFlow build experience as plain text")
    return " ".join(page_texts)

required = [
    "Olamide Olanipekun",
    "4+ years of hands-on PM experience",
    "7+ years",
    "$30M+", "40%", "30%",
    "YNX | Apr 2025 - May 2026",
    "Built and owned the YNX community from scratch",
    "sourced moderators",
    "Sourced marketing talent and developers",
    "Dextopus | Aug 2025 - Feb 2026",
    "Debonk Bot | Jun 2025 - Jan 2026",
    "Deserialize | Apr 2024 - May 2025",
    "Limitless Prop Firm | May 2022 - Dec 2023",
    "Gotabit | Feb 2021 - Oct 2022",
    "Betboom | Jan 2020 - Sep 2021",
    "FortaFlow | Independent Product Builder",
    "intermediate retail crypto and forex traders",
    "Build is paused; it is not shipped",
    "manual/CSV journaling",
    "B.Sc.Ed., Mathematics and Education", "University of Lagos", "Second Class Upper",
]
stale = (
    "50% reduction in operational bottlenecks",
    "in active development",
    "futures, stock, and prop-firm traders",
    "Dextopus Bridge",
    "Community & Customer support specialist",
    "CGPA",
    "Completed 2026",
    "3.8/5",
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

print("PASS: " + ("generated " if GENERATED_ONLY else "committed and generated ") + "PM PDF(s) are two-page A4 with all seven role dates, YNX community ownership and sourcing, metrics, Limitless full-date exception, FortaFlow scope/status, and the degree, institution, and Second Class Upper classification verified.")
