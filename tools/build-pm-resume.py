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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
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
styles.add(ParagraphStyle(name="Name", fontName="Helvetica-Bold", fontSize=21, leading=23,
                          textColor=NAVY, spaceAfter=2, alignment=TA_LEFT))
styles.add(ParagraphStyle(name="Headline", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
                          textColor=BLUE, spaceAfter=4))
styles.add(ParagraphStyle(name="Contact", fontName="Helvetica", fontSize=7.4, leading=9.5,
                          textColor=MUTED, spaceAfter=6))
styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=9.3, leading=11,
                          textColor=NAVY, spaceBefore=7, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="Summary", fontName="Helvetica", fontSize=8.05, leading=11.1,
                          textColor=BODY, spaceAfter=4))
styles.add(ParagraphStyle(name="BodySmall", fontName="Helvetica", fontSize=7.55, leading=10.1,
                          textColor=BODY, spaceAfter=2))
styles.add(ParagraphStyle(name="Role", fontName="Helvetica-Bold", fontSize=8.55, leading=10.5,
                          textColor=NAVY))
styles.add(ParagraphStyle(name="RoleMeta", fontName="Helvetica", fontSize=7.1, leading=8.8,
                          textColor=MUTED, spaceAfter=2))
styles.add(ParagraphStyle(name="ResumeBullet", fontName="Helvetica", fontSize=7.35, leading=9.45,
                          textColor=BODY, leftIndent=9, firstLineIndent=-6,
                          bulletIndent=0, spaceAfter=1.2))
styles.add(ParagraphStyle(name="Skill", fontName="Helvetica", fontSize=7.45, leading=10,
                          textColor=BODY, spaceAfter=2))
styles.add(ParagraphStyle(name="ProjectTitle", fontName="Helvetica-Bold", fontSize=8.0, leading=9.8,
                          textColor=NAVY, spaceAfter=1))


def P(text: str, style: str = "BodySmall") -> Paragraph:
    return Paragraph(text, styles[style])


def section(title: str):
    return [
        Paragraph(title.upper(), styles["Section"]),
        HRFlowable(width="100%", thickness=0.7, color=LINE, spaceAfter=4)
    ]


def bullet(text: str) -> Paragraph:
    return Paragraph("• " + text, styles["ResumeBullet"])


def role(title, company, dates, location, summary, bullets):
    # Keep title, employer, and dates in one text object so text extraction and
    # ATS parsers encounter them in the same logical order as a human reader.
    heading = Paragraph(
        f"<b>{escape(title)} | {escape(company)}</b>  "
        f"<font name='Helvetica' size='7.4' color='#667482'>| {escape(dates)}</font>",
        styles["Role"]
    )
    block = [heading]
    if location:
        block.append(P(escape(location), "RoleMeta"))
    if summary:
        block.append(P(summary, "BodySmall"))
    block.extend(bullet(item) for item in bullets)
    block.append(Spacer(1, 4))
    return KeepTogether(block)


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
    str(OUT), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
    topMargin=14*mm, bottomMargin=17*mm,
    title="Olamide Olanipekun - Product Manager Resume",
    author="Olamide Olanipekun",
    subject="Technical Product Management, Growth, Web3 and Fintech",
)
story = []

# Page 1: profile and latest product roles.
story.append(P("OLAMIDE OLANIPEKUN", "Name"))
story.append(P("TECHNICAL PRODUCT MANAGER  |  PRODUCT STRATEGY, GROWTH &amp; OPERATIONS", "Headline"))
story.append(P(
    'Lagos, Nigeria  &nbsp;•&nbsp; <link href="mailto:flux.fx05@gmail.com" color="#667482">flux.fx05@gmail.com</link>  &nbsp;•&nbsp; '
    '<link href="https://www.linkedin.com/in/olanipekun-olamide-flux-939a34235/" color="#667482">LinkedIn</link>  &nbsp;•&nbsp; '
    '<link href="https://portfolio-site-kappa-ashy.vercel.app" color="#667482">Portfolio</link>', "Contact"))

story.extend(section("Professional Summary"))
story.append(P(
    "Technical Product Manager with <b>4+ years of hands-on product management experience</b> and "
    "<b>7+ years of broader experience</b> across product, operations, growth, marketing, community management, "
    "customer experience, and trading. Experience across Web3, fintech, SaaS, and AI, translating ambiguous "
    "user and business problems into product direction, requirements, prioritised backlogs, and cross-functional "
    "delivery. Contributed to a Web3 swap aggregator that processed <b>$30M+ in transaction volume within its "
    "first six months</b>; contributed to a <b>40%</b> improvement in onboarding and activation and a <b>30%</b> "
    "reduction in YNX workflow bottlenecks.", "Summary"))

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
    "Product discovery &amp; user research  •  Product strategy &amp; roadmapping  •  PRDs, user stories &amp; acceptance criteria  •  "
    "RICE / MoSCoW prioritisation  •  Agile delivery &amp; backlog management  •  Cross-functional stakeholder management  •  "
    "Onboarding, activation &amp; retention  •  Product analytics, SQL &amp; Dune  •  AI-assisted prototyping &amp; development  •  "
    "Workflow automation &amp; process optimisation", "Skill"))

story.extend(section("Professional Experience"))
story.append(role("Product Manager | Growth Lead", "YNX", "Apr 2025 - May 2026", "United Kingdom · Remote",
    "Led product development and growth execution across digital products, taking initiatives from discovery and planning through development and launch. Built and owned the YNX community from scratch, then sourced moderators, marketing talent, and developers to support community operations, growth initiatives, and product delivery.",
    [
        "Built and launched an MVP, managed its product lifecycle, and coordinated delivery with engineering and cross-functional teams.",
        "Built and owned the YNX community from scratch, establishing its structure and ongoing community operations.",
        "Sourced moderator talent, marketing talent, and developers to support community moderation, growth initiatives, and product delivery.",
        "Partnered with leadership on product direction, early-stage growth strategy, and grant and fundraising initiatives.",
        "Managed sprint planning and backlog prioritisation in Notion and Trello; conducted market and competitor research to inform product decisions.",
        "Improved operational workflows, reducing workflow bottlenecks by <b>30%</b> through data-informed process improvements."
    ]))
story.append(role("Product Manager", "Dextopus", "Aug 2025 - Feb 2026", "Hybrid",
    "Supported product growth, product operations, and lifecycle optimisation for a fintech platform following launch.",
    [
        "Optimised onboarding and activation workflows to improve user engagement and retention.",
        "Worked with product and technical teams to turn business and user needs into prioritised features and execution requirements.",
        "Analysed user behaviour, engagement patterns, and operational feedback to identify friction and inform product improvements."
    ]))
story.append(role("Product Manager | Team Lead", "Debonk Bot", "Jun 2025 - Jan 2026", "",
    "Led product and team execution for Debonk Bot, moving the concept toward an initial product.",
    [
        "Drove 0-to-1 product development, translating the concept into product direction and actionable requirements.",
        "Coordinated a multidisciplinary team of approximately <b>eight people</b> around priorities, tasks, and delivery.",
        "Contributed to onboarding, demo trading, gamification, and the final mini-app experience."
    ]))
story.append(role("Product Manager", "Deserialize", "Apr 2024 - May 2025", "Lagos, Nigeria · Remote",
    "Led product and ecosystem operations for a Web3 swap aggregator focused on best-price routing. The platform processed <b>$30M+ in transaction volume within its first six months</b> (team outcome).",
    [
        "Worked across product discovery, execution planning, feature prioritisation, and product improvement.",
        "Collaborated with engineering and stakeholders to translate user and business needs into product requirements and delivery priorities.",
        "Improved onboarding and activation workflows, and used behavioural data and operational feedback to guide engagement and retention improvements."
    ]))

# Page 2: earlier experience, selected product work, tools, and education.
story.append(PageBreak())
story.extend(section("Professional Experience | Continued"))
story.append(role("Product Manager & Growth Operations Lead", "Limitless Prop Firm", "May 2022 - Dec 2023", "",
    "Worked across growth-focused product initiatives, community infrastructure, customer experience, and operational execution for a proprietary trading business.",
    [
        "Translated user feedback, community insights, and operational challenges into product and growth improvements across onboarding, engagement, activation, and retention.",
        "Built Discord and Telegram communities from scratch, growing them beyond <b>5,000 members</b>; worked with and led a <b>six-person community team</b>.",
        "Led a separate <b>two-person website support team</b>; implemented Zendesk ticketing and escalation workflows, maintaining approximately <b>5-15-minute response times</b>.",
        "Configured Discord bots and built customised Telegram bots to support automation, engagement, and community operations.",
        "Coordinated growth campaigns, social content, and cross-functional community and product feedback loops."
    ]))
story.append(role("Community Manager", "Gotabit", "Feb 2021 - Oct 2022", "",
    "Managed community operations, customer support, content coordination, and engagement, acting as a communication link between users and the technical team.",
    [
        "Created and published social content; welcomed and onboarded new users and handled community enquiries and support.",
        "Programmed customised and general-purpose community bots to automate processes and support community operations.",
        "Coordinated technical issues with the technical team, hosted AMAs, organised engagement events, and enforced community rules fairly.",
        "Prepared weekly progress reports covering community activity, engagement, feedback, and outstanding issues."
    ]))
story.append(role("Community Management & Growth Contributor", "Betboom", "Jan 2020 - Sep 2021", "",
    "Created and supported Discord and Telegram communities from the ground up for a community of approximately <b>50,000 members</b>.",
    [
        "Managed member enquiries and customer support, maintaining typical response times of approximately <b>5-7 minutes</b>.",
        "Handled onboarding, community communications, project updates, campaigns, and engagement activities.",
        "Coordinated with project stakeholders and surfaced member questions, feedback, and recurring concerns for resolution."
    ]))

story.extend(section("Selected Product-Building Work"))
story.append(KeepTogether([
    P("FortaFlow | Independent Product Builder", "ProjectTitle"),
    P("A trading-strategy research and validation product scoped for intermediate retail crypto and forex traders. Led product discovery, product direction, requirements, UX, architecture, prototyping, and MVP planning. Coding/build work is currently paused; this is not a shipped production system. The MVP centres on explicit rules, immutable strategy versions, reproducible historical backtesting, performance and risk review, bounded stress scenarios, and manual/CSV journaling. It does not place live orders."),
    P("Tools: Notion, ChatGPT, Claude, Google Stitch, Lovable, Claude Code, Supabase, GitHub, Vercel.", "RoleMeta"),
    Spacer(1,3)
]))
story.append(KeepTogether([
    P("AI-Powered Job Discovery &amp; Automation", "ProjectTitle"),
    P("Built n8n workflows for job discovery, filtering, deduplication, AI-assisted relevance scoring, scheduling, and alerts, integrating data and decision workflows into one process."),
    Spacer(1,3)
]))
story.append(KeepTogether([
    P("Tourist | TS Academy Capstone", "ProjectTitle"),
    P("Defined a budget-first travel-planning MVP from user research (19 usable survey responses), wrote product documentation and prioritised scope, then built and deployed a working React and TypeScript prototype. Itinerary drafts use seeded templates rather than a live AI model.")
]))

story.extend(section("Tools &amp; Technologies"))
story.append(P(
    "Jira, Notion, Trello, ClickUp, Mixpanel, Amplitude, SQL, Dune, Figma, Google Stitch, Lovable, Claude Code, "
    "ChatGPT, Claude, n8n, Zapier, GitHub, Supabase, Vercel, Discord, Telegram, Zendesk, Slack, Google Workspace.", "Skill"))

story.extend(section("Education &amp; Professional Development"))
story.append(P("<b>B.Sc.Ed., Mathematics and Education</b> | University of Lagos, Lagos, Nigeria"))
story.append(P(
    "DataCamp: Introduction to SQL, Intermediate SQL, Data Manipulation in SQL, Joining Data in SQL, PostgreSQL Summary Statistics &amp; "
    "Window Functions, Introduction to Data, Introduction to Data Literacy, Communicating Data Insights.  |  "
    "Understanding Artificial Intelligence."
))

doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
print(f"Wrote {OUT}")
