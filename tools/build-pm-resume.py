#!/usr/bin/env python3
"""Build Olamide Olanipekun's current two-page Product Manager résumé.

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
BLUE = colors.HexColor("#1876B9")
BODY = colors.HexColor("#35424E")
MUTED = colors.HexColor("#667482")
LINE = colors.HexColor("#D8E0E7")
PALE = colors.HexColor("#F2F6F9")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Name", fontName="Helvetica-Bold", fontSize=24, leading=27,
                          textColor=NAVY, spaceAfter=2, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="Headline", fontName="Helvetica-Bold", fontSize=11.3, leading=14.2,
                          textColor=BLUE, spaceAfter=4))
styles.add(ParagraphStyle(name="Contact", fontName="Helvetica", fontSize=9.2, leading=11.8,
                          textColor=MUTED, spaceAfter=4))
styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=11.2, leading=13.2,
                          textColor=NAVY, spaceBefore=5, spaceAfter=2.5, keepWithNext=True))
styles.add(ParagraphStyle(name="Summary", fontName="Helvetica", fontSize=11.0, leading=14.5,
                          textColor=BODY, spaceAfter=4))
styles.add(ParagraphStyle(name="BodySmall", fontName="Helvetica", fontSize=10.7, leading=14.0,
                          textColor=BODY, spaceAfter=2))
styles.add(ParagraphStyle(name="Role", fontName="Helvetica-Bold", fontSize=10.7, leading=13.0,
                          textColor=NAVY))
styles.add(ParagraphStyle(name="RoleMeta", fontName="Helvetica", fontSize=9.0, leading=11.2,
                          textColor=MUTED, spaceAfter=2))
styles.add(ParagraphStyle(name="ResumeBullet", fontName="Helvetica", fontSize=10.6, leading=13.8,
                          textColor=BODY, leftIndent=9, firstLineIndent=-6,
                          bulletIndent=0, spaceAfter=0.8))
styles.add(ParagraphStyle(name="Skill", fontName="Helvetica", fontSize=10.6, leading=13.8,
                          textColor=BODY, spaceAfter=2))
styles.add(ParagraphStyle(name="ProjectTitle", fontName="Helvetica-Bold", fontSize=10.7, leading=13.2,
                          textColor=NAVY, spaceAfter=1))


def P(text: str, style: str = "BodySmall") -> Paragraph:
    return Paragraph(text, styles[style])


def section(title: str):
    return [
        Paragraph(title.upper(), styles["Section"]),
        HRFlowable(width="100%", thickness=0.7, color=LINE, spaceAfter=4)
    ]


def bullet(text: str) -> Paragraph:
    return Paragraph("- " + text, styles["ResumeBullet"])


def role(title, company, dates, location, summary, bullets, keep_all=False):
    # Keep title, employer, and dates in one text object so text extraction and
    # ATS parsers encounter them in the same logical order as a human reader.
    heading = Paragraph(
        f"<b>{escape(title)} | {escape(company)}</b>  "
        f"<font name='Helvetica' size='8.4' color='#667482'>| {escape(dates)}</font>",
        styles["Role"]
    )
    # Keep the role title, employer, and dates together. Let the summary
    # and bullets flow independently so a short remaining space is not wasted
    # merely because the complete role lead cannot fit before a page break.
    lead = [heading]
    if location:
        lead.append(P(escape(location), "RoleMeta"))
    if summary:
        lead.append(P(summary, "BodySmall"))
    if keep_all:
        # Keep this role intact when it falls near a page boundary. This avoids
        # leaving its title/summary at the foot of one page and bullets at the
        # top of the next.
        flow = [KeepTogether(lead + [bullet(item) for item in bullets] + [Spacer(1, 1.5)])]
    else:
        flow = [KeepTogether(lead)]
        flow.extend(bullet(item) for item in bullets)
        flow.append(Spacer(1, 1.5))
    return flow


def page_frame(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.55)
    canvas.line(15*mm, 12*mm, width-15*mm, 12*mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(15*mm, 7.5*mm, "OLAMIDE OLANIPEKUN  |  PRODUCT MANAGEMENT")
    canvas.drawRightString(width-15*mm, 7.5*mm, f"{doc.page}")
    if doc.page > 1:
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(15*mm, height-10*mm, "OLAMIDE OLANIPEKUN  |  PRODUCT MANAGER RÉSUMÉ")
        canvas.setStrokeColor(LINE)
        canvas.line(15*mm, height-12*mm, width-15*mm, height-12*mm)
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, rightMargin=13*mm, leftMargin=13*mm,
    topMargin=14*mm, bottomMargin=15*mm,
    title="Olamide Olanipekun - Product Manager Resume",
    author="Olamide Olanipekun",
    subject="Technical Product Management, Growth, Web3 and Fintech",
)
story = []

# Page 1: profile and latest product roles.
story.append(P("OLAMIDE OLANIPEKUN", "Name"))
story.append(P("TECHNICAL PRODUCT MANAGER  |  PRODUCT STRATEGY, GROWTH &amp; OPERATIONS", "Headline"))
story.append(P(
    'Lagos, Nigeria  &nbsp;|&nbsp; flux.fx05@gmail.com  &nbsp;|&nbsp; '
    '<link href="https://www.linkedin.com/in/olanipekun-olamide-flux-939a34235/" color="#1876B9">LinkedIn</link>  &nbsp;|&nbsp; '
    '<link href="https://olamide-olanipekun.vercel.app/#/" color="#1876B9">Portfolio</link>  &nbsp;|&nbsp; '
    '<link href="https://github.com/Flux-web3" color="#1876B9">GitHub</link>  &nbsp;|&nbsp; '
    '<link href="https://t.me/king_flux" color="#1876B9">Telegram</link>', "Contact"))

story.extend(section("Professional Summary"))
story.append(P(
    "Technical Product Manager with <b>4+ years of hands-on PM experience</b> within <b>7+ years</b> "
    "across product, operations, marketing, growth, community, customer experience, and trading. Translate "
    "ambiguous business and user needs into product strategy, requirements, prioritised backlogs, and "
    "cross-functional delivery across Web3, fintech, SaaS, and AI. Contributed to <b>$30M+ swap volume in six "
    "months</b>, a <b>40%</b> onboarding/activation improvement, and a <b>30%</b> reduction in YNX workflow bottlenecks.", "Summary"))

metrics = Table([[
    P("<b>$30M+</b><br/><font color='#667482'>swap volume in 6 months</font>"),
    P("<b>40%</b><br/><font color='#667482'>activation improvement</font>"),
    P("<b>30%</b><br/><font color='#667482'>YNX workflow bottlenecks reduced</font>"),
    P("<b>5K+ / ~50K</b><br/><font color='#667482'>communities managed</font>")
]], colWidths=[45*mm,45*mm,45*mm,45*mm])
metrics.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), PALE),
    ("BOX", (0,0), (-1,-1), 0.5, LINE),
    ("INNERGRID", (0,0), (-1,-1), 0.35, LINE),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("LEFTPADDING", (0,0), (-1,-1), 5),
    ("RIGHTPADDING", (0,0), (-1,-1), 5),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(metrics)

story.extend(section("Core Product Competencies"))
story.append(P(
    "<b>Discovery &amp; strategy:</b> user research, problem framing, opportunity validation, product strategy, roadmaps and competitor analysis. "
    "<b>Product definition:</b> PRDs, user stories, acceptance criteria, user journeys, MVP scope, RICE / MoSCoW and backlog management. "
    "<b>Delivery &amp; leadership:</b> Scrum, Kanban, Scrumban, sprint planning, stakeholder alignment, cross-functional delivery, UAT and release coordination. "
    "<b>Growth &amp; operations:</b> go-to-market, onboarding, activation, retention, lifecycle optimisation, product operations and workflow automation. "
    "<b>Analytics &amp; experimentation:</b> SQL, Mixpanel, Amplitude, Dune, KPI tracking, funnel analysis, performance reporting and experimentation. "
    "<b>Technical product building:</b> product architecture, REST APIs, third-party integrations, UX prototyping and AI-assisted development. "
    "<b>Customer, community &amp; CX:</b> customer support workflows, issue triage and escalation, community strategy, moderation, member engagement and feedback loops.",
    "Skill"))

story.extend(section("Professional Experience"))
story.extend(role("Product Manager | Growth Lead", "YNX", "Apr 2025 - May 2026", "United Kingdom · Remote",
    "Led product development and growth from discovery through launch. Built and owned the YNX community from scratch, then sourced moderators, marketing talent, and developers for operations, growth, and product delivery.",
    [
        "Built and launched an MVP, managed its lifecycle, and coordinated engineering and cross-functional delivery.",
        "Sourced marketing talent and developers to support growth initiatives and product delivery.",
        "Partnered with leadership on product direction, growth strategy, grants, and fundraising; managed sprint planning, backlog priorities, and competitor research.",
        "Improved operational workflows, reducing bottlenecks by <b>30%</b>."
    ]))
story.extend(role("Product Manager", "Dextopus", "Aug 2025 - Feb 2026", "Hybrid",
    "Supported product growth, product operations, and lifecycle optimisation for a fintech platform following launch.",
    [
        "Optimised onboarding and activation workflows to improve engagement and retention.",
        "Translated user needs, behavioural data, and operational feedback into prioritised features with product and technical teams."
    ]))
story.extend(role("Product Manager | Team Lead", "Debonk Bot", "Jun 2025 - Jan 2026", "",
    "Led product and team execution for Debonk Bot, moving the concept toward an initial product.",
    [
        "Led 0-to-1 product direction and coordinated delivery with a multidisciplinary team of approximately <b>eight people</b>.",
        "Contributed to onboarding, demo trading, gamification, and the mini-app experience."
    ]))
story.extend(role("Product Manager", "Deserialize", "Apr 2024 - May 2025", "Lagos, Nigeria · Remote",
    "Led product and ecosystem operations for a best-price Web3 swap aggregator that processed <b>$30M+ in its first six months</b> (team outcome).",
    [
        "Coordinated discovery, requirements, prioritisation, and delivery with engineering and stakeholders.",
        "Used behavioural data and operational feedback to improve onboarding, activation, and retention."
    ], keep_all=True))

# Earlier experience, selected product work, tools, and education flow naturally
# into the remaining first-page space before continuing onto page two.
story.extend(role("Product Manager & Growth Operations Lead", "Limitless Prop Firm", "May 2022 - Dec 2023", "",
    "Led product and growth operations informed by user/community feedback. Built <b>5,000+ member</b> Discord/Telegram communities, led a <b>six-person community team</b> and a separate <b>two-person website support team</b>, and implemented Zendesk with <b>5–15-minute responses</b>.",
    []))
story.extend(role("Community Manager", "Gotabit", "Feb 2021 - Oct 2022", "",
    "Managed community operations, customer support, content coordination, and engagement, acting as a communication link between users and the technical team.",
    [
        "Managed community communications, social content, onboarding, and member support.",
        "Programmed community bots, coordinated technical issues, hosted AMAs and events, and enforced community rules.",
        "Prepared weekly reports on activity, engagement, feedback, and outstanding issues."
    ]))
story.extend(role("Community Management & Growth Contributor", "Betboom", "Jan 2020 - Sep 2021", "",
    "Created and supported Discord and Telegram communities from the ground up for a community of approximately <b>50,000 members</b>.",
    [
        "Created Discord and Telegram communities from scratch for approximately <b>50,000 members</b>, handling onboarding, updates, and engagement campaigns.",
        "Managed member support with typical response times of <b>5–7 minutes</b> and surfaced recurring issues and feedback to stakeholders."
    ]))

story.extend(section("Selected Product-Building Work"))
story.append(KeepTogether([
    P("FortaFlow | Independent Product Builder", "ProjectTitle"),
    P("A trading-strategy research and validation product scoped for intermediate retail crypto and forex traders. Led discovery, requirements, UX, architecture, prototyping, and MVP planning. <b>Build is paused; it is not shipped and has no live-order path.</b> MVP scope: explicit rules, immutable strategy versions, reproducible historical backtests, performance/risk reporting, bounded stress scenarios, and manual/CSV journaling."),
    P("Tools: Notion, ChatGPT, Claude, Google Stitch, Lovable, Claude Code, Supabase, GitHub, Vercel.", "RoleMeta"),
    Spacer(1,3)
]))
story.append(KeepTogether([
    P("AI-Powered Job Discovery &amp; Automation", "ProjectTitle"),
    P("Built n8n workflows for job discovery, filtering, deduplication, AI relevance scoring, scheduling, and alerts."),
    Spacer(1,3)
]))
story.append(KeepTogether([
    P("Tourist | TS Academy Capstone", "ProjectTitle"),
    P("Defined a budget-first travel MVP from 19 usable survey responses, documented and prioritised scope, then built and deployed a React/TypeScript prototype. Itinerary drafts use seeded templates, not a live AI model.")
]))

story.extend(section("Tools &amp; Technologies"))
for item in [
    "<b>Product delivery &amp; collaboration:</b> Jira, Notion, Trello, ClickUp, Slack and Google Workspace.",
    "<b>Product analytics &amp; data:</b> SQL, Mixpanel, Amplitude and Dune.",
    "<b>Design &amp; prototyping:</b> Figma, Google Stitch and Lovable.",
    "<b>AI-assisted building &amp; automation:</b> ChatGPT, Claude, Claude Code, n8n, Zapier, GitHub, Supabase and Vercel.",
    "<b>Community &amp; customer operations:</b> Discord, Telegram and Zendesk."
]:
    story.append(P(item, "Skill"))

story.extend(section("Education &amp; Professional Development"))
story.append(P("<b>B.Sc.Ed., Mathematics and Education</b> | University of Lagos, Lagos, Nigeria | Second Class Upper"))
story.append(P(
    'DataCamp: <link href="https://www.datacamp.com/completed/statement-of-accomplishment/course/d2b403c9775c6f044933a0f0c04b995599f52745" color="#1876B9">Introduction to SQL</link>, '
    '<link href="https://www.datacamp.com/completed/statement-of-accomplishment/course/639e3d23f56331e4778550bfe3a969aad4971fcc" color="#1876B9">Intermediate SQL</link>, '
    '<link href="https://www.datacamp.com/completed/statement-of-accomplishment/course/65fee3ea851aa182dd6c8d6487c9c8d04182cf49" color="#1876B9">Joining Data in SQL</link>, '
    'Data Manipulation in SQL, PostgreSQL Summary Statistics &amp; Window Functions, Introduction to Data, Introduction to Data Literacy, Communicating Data Insights.  |  '
    'Understanding Artificial Intelligence.' 
))

doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
print(f"Wrote {OUT}")
