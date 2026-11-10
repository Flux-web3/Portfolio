#!/usr/bin/env python3
"""Build Olamide Olanipekun's current two-page Product Manager rÃ©sumÃ©.

Source of truth: the corrected LinkedIn Experience history supplied on
2026-11-04. Overlapping engagements remain separate and overlapping dates are
not added together when stating years of experience.

Run: python tools/build-pm-resume.py [output.pdf]
Requires: Python 3 and ReportLab.
"""
from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, HRFlowable
)

rl_config.invariant = 1

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Olamide-Olanipekun-Product-Manager.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

# ReportLab's built-in Base-14 fonts keep the generated PDF compact and
# reliably searchable/selectable without external font downloads.
pdfmetrics.registerFontFamily("Helvetica", normal="Helvetica", bold="Helvetica-Bold",
                              italic="Helvetica-Oblique", boldItalic="Helvetica-BoldOblique")

NAVY = colors.HexColor("#132B43")
BLUE = colors.HexCo¶»§q«^