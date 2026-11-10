#!/usr/bin/env python3
"""Validate committed and regenerated Community Management rÃ©sumÃ© PDFs."""
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
    "5,000 members", "5â€“15 minutes", "Community Manager", "Gotabit",
    "Feb 2021", "Oct 2022", "Community Management & Growth Contributor",
    "Betboom", "Jan 2020", "Sep 2021", "50,000 members", "5â€“7 minutes",
    "University of Lagos", "B.Sc.Ed., Mathematics and Education", "Second Class Upper"
]
EXCLUDED = ["50% reduction in operational bottlenecks", "community ownership at Deserialize", "CGPA", "Completed 2026", "3.8/5"]

def inspect(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"FAIL: missing Community Management PDF: {path}")
    reader = PdfReader(str(path), strict=True)
    if len(reade¶»§q«^