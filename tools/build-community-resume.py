#!/usr/bin/env python3
"""Reproducibly build the two-page Community Management rÃ©sumÃ© PDF."""
from __future__ import annotations
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable

rl_config.invariant = 1
ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Olamide_Olanipekun_Community_Management_Resume.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

INK = colors.HexColor("#20272B")
ACCENT = colors.HexColor("#A96512")
BODY = colors.HexColor("#343D42")
MUTED = colors.HexColor("#5D6870")
LINE = colors.HexColor("#D9DFE2")
WASH = colors.HexColor("#FBF4E8")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Name", fontName="Helvetica-Bold", fontSize=24, leading=27, textColor=INK, spaceAfter=3))
styles.add(ParagraphStyle(name="Headline", fontName="Helvetica-Bold", fontSize=11.2, leading=14, textColor=ACCENT, spaceAfter=4))
styles.add(ParagraphStyle(name="Contact", fontName="Helvetica", fontSize=9.2, leading=11.8, textColor=MUTED, spaceAfter=5))
styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=11.0, leading=1¶»§q«^