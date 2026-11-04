#!/usr/bin/env python3
"""Reproducibly build the two-page Community Management résumé PDF."""
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
styles.add(ParagraphStyle(name="Name", fontName="Helvetica-Bold", fontSize=23, leading=25.5, textColor=INK, spaceAfter=3))
styles.add(ParagraphStyle(name="Headline", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=ACCENT, spaceAfter=4))
styles.add(ParagraphStyle(name="Contact", fontName="Helvetica", fontSize=8.4, leading=10.8, textColor=MUTED, spaceAfter=5))
styles.add(ParagraphStyle(name="Section", fontName="Helvetica-Bold", fontSize=10.3, leading=12.3, textColor=ACCENT, spaceBefore=5, spaceAfter=2.5, keepWithNext=True))
styles.add(ParagraphStyle(name="Summary", fontName="Helvetica", fontSize=10.0, leading=13.2, textColor=BODY, spaceAfter=3))
styles.add(ParagraphStyle(name="Role", fontName="Helvetica-Bold", fontSize=10.0, leading=12.2, textColor=INK))
styles.add(ParagraphStyle(name="Date", fontName="Helvetica", fontSize=8.5, leading=10.0, textColor=MUTED, alignment=TA_RIGHT))
styles.add(ParagraphStyle(name="RoleText", fontName="Helvetica", fontSize=9.5, leading=12.4, textColor=BODY, spaceAfter=2))
styles.add(ParagraphStyle(name="ResumeBullet", fontName="Helvetica", fontSize=9.5, leading=12.0, textColor=BODY, leftIndent=9, firstLineIndent=-6, spaceAfter=1.0))
styles.add(ParagraphStyle(name="SkillTitle", fontName="Helvetica-Bold", fontSize=9.4, leading=11.0, textColor=INK, spaceAfter=1))
styles.add(ParagraphStyle(name="SkillText", fontName="Helvetica", fontSize=9.3, leading=11.7, textColor=BODY))
styles.add(ParagraphStyle(name="Small", fontName="Helvetica", fontSize=9.3, leading=11.8, textColor=BODY, spaceAfter=2))

def p(text: str, style: str = "Small") -> Paragraph:
    return Paragraph(text, styles[style])

def section(title: str):
    return [Paragraph(title.upper(), styles["Section"]), HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=3)]

def bullet(text: str):
    return Paragraph("- " + text, styles["ResumeBullet"])

def role(title: str, org: str, dates: str, summary: str, items: list[str]):
    heading = Table([[
        Paragraph(f"{escape(title)} · {escape(org)}", styles["Role"]),
        Paragraph(escape(dates), styles["Date"])
    ]], colWidths=[136 * mm, 48 * mm])
    heading.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    block = [heading]
    if summary:
        block.append(p(summary, "RoleText"))
    block.extend(bullet(item) for item in items)
    block.append(Spacer(1, 3))
    return KeepTogether(block)

def footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 11 * mm, width - 15 * mm, 11 * mm)
    canvas.setFont("Helvetica", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(15 * mm, 7 * mm, "OLAMIDE OLANIPEKUN  |  COMMUNITY MANAGEMENT")
    canvas.drawRightString(width - 15 * mm, 7 * mm, f"PAGE {doc.page} OF 2")
    if doc.page == 2:
        canvas.setFont("Helvetica-Bold", 7.2)
        canvas.setFillColor(INK)
        canvas.drawString(15 * mm, height - 9 * mm, "OLAMIDE OLANIPEKUN  |  COMMUNITY MANAGEMENT RÉSUMÉ")
        canvas.setStrokeColor(LINE)
        canvas.line(15 * mm, height - 11 * mm, width - 15 * mm, height - 11 * mm)
    canvas.restoreState()

doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, leftMargin=13 * mm, rightMargin=13 * mm,
    topMargin=14 * mm, bottomMargin=16 * mm,
    title="Olamide Olanipekun - Community Management Resume",
    author="Olamide Olanipekun",
    subject="Web3 Community Management, Growth, Customer Support and Operations",
)
story = []

# Page 1: identity, summary, capabilities and latest roles.
story.append(p("OLAMIDE OLANIPEKUN", "Name"))
story.append(p("WEB3 COMMUNITY MANAGER  |  COMMUNITY GROWTH, CUSTOMER SUPPORT &amp; OPERATIONS", "Headline"))
story.append(p(
    '<link href="mailto:flux.fx05@gmail.com" color="#5D6870">flux.fx05@gmail.com</link>  |  '
    '<link href="https://www.linkedin.com/in/olanipekun-olamide-flux-939a34235/" color="#5D6870">LinkedIn</link>  |  '
    '<link href="https://portfolio-site-kappa-ashy.vercel.app/" color="#5D6870">Portfolio</link>  |  Remote / Hybrid', "Contact"))

story.extend(section("Professional Summary"))
story.append(p(
    "I build Web3 communities and run the work that keeps them active and supported: engagement, moderation, social channels, automation, and customer support, with a working knowledge of blockchain and cryptocurrency. At <b>Betboom</b>, I created Discord and Telegram communities from scratch for approximately <b>50,000 members</b>, maintaining typical response times of <b>5–7 minutes</b>. At <b>Limitless Prop Firm</b>, I held two concurrent roles: Product Manager &amp; Growth Operations Lead (Sep 2022–Dec 2023) and Community &amp; Customer support specialist (May 2022–Dec 2023). Across those roles, I helped grow Discord and Telegram communities beyond <b>5,000 members</b>, led a six-person community team and a separate two-person website support team, and maintained support response times of approximately <b>5–15 minutes</b> using Zendesk. At <b>YNX</b>, I built and owned the community from scratch, then sourced moderators, marketing talent, and developers to support community operations, growth, and product delivery. My broader experience spans <b>7+ years</b> across product, operations, marketing, growth, community management, and customer experience.", "Summary"))

story.extend(section("Core Skills"))
skills = [
    ("Community Management", "Community strategy and operations; community building and growth; onboarding; moderation and member conduct; moderator management; member engagement and retention; community communications; campaigns, giveaways, AMAs and events; Discord and Telegram; team coordination."),
    ("Customer Support &amp; CX", "Customer support; customer experience; Zendesk implementation; ticketing workflows; issue triage and escalation; SLAs and response-time management; support team leadership; SOPs, documentation and knowledge bases."),
    ("Automation &amp; Social Media", "Bot configuration; automation and auto-responses; X/Twitter and LinkedIn management; content coordination and publishing; social scheduling."),
    ("Analytics, Growth &amp; Product", "Growth marketing; KOL and influencer outreach; partnership coordination; community analytics and reporting; KPI monitoring; user feedback; product feedback loops; stakeholder communication; operational process improvement."),
    ("Web3 &amp; Crypto", "Web3 industry knowledge; blockchain and cryptocurrency communities; crypto product and trading ecosystem familiarity."),
]
rows = []
for i in range(0, len(skills), 2):
    left = skills[i]
    right = skills[i + 1] if i + 1 < len(skills) else ("", "")
    left_cell = [p(left[0], "SkillTitle"), p(left[1], "SkillText")]
    right_cell = [p(right[0], "SkillTitle"), p(right[1], "SkillText")] if right[0] else ""
    rows.append([left_cell, right_cell])
skill_table = Table(rows, colWidths=[92 * mm, 92 * mm], hAlign="LEFT")
skill_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, -1), WASH),
    ("BOX", (0, 0), (-1, -1), 0.45, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(skill_table)

story.extend(section("Professional Experience"))
story.append(role("Product Manager | Growth Lead", "YNX", "Apr 2025 – May 2026",
    "Led product development and growth execution across digital products, taking initiatives from discovery and planning through development and launch. Built and owned the YNX community from scratch, then sourced moderators, marketing talent, and developers to support community operations, growth initiatives, and product delivery.", [
        "Built and launched an MVP and managed its product lifecycle, coordinating delivery with engineering and cross-functional teams.",
        "Built and owned the YNX community from scratch, establishing its structure and ongoing community operations.",
        "Sourced moderators to support community moderation, and sourced marketing talent and developers to support growth initiatives and product delivery.",
    ]))
story.append(role("Product Manager", "Deserialize", "Apr 2024 – May 2025",
    "Worked across product and ecosystem operations for a Web3 swap aggregator focused on best-price routing, using user feedback and operational insights to inform product improvements.", [
        "Supported discovery, prioritisation, delivery, and product improvement across the swap aggregator.",
        "Used user behaviour, operational feedback, and recurring customer needs to identify friction and inform product decisions.",
    ]))

# Earlier roles and supporting information continue through natural pagination.
# No forced page break: use remaining first-page space before flowing to page two.
story.append(role("Product Manager & Growth Operations Lead", "Limitless Prop Firm", "Sep 2022 – Dec 2023",
    "", [
        "Led growth-focused product initiatives using user/community feedback to improve engagement, activation, retention, and operations; coordinated campaigns and partnerships.",
    ]))
story.append(role("Community & Customer support specialist", "Limitless Prop Firm", "May 2022 – Dec 2023",
    "Owned community operations and customer support workflows alongside the concurrent product and growth role.", [
        "Built and managed Discord and Telegram communities from scratch, growing the community beyond <b>5,000 members</b>.",
        "Led a <b>six-person Discord and Telegram team</b>; developed community infrastructure, customised Telegram bots, Discord bots, engagement systems, and operational workflows.",
        "Coordinated a separate <b>two-person website support team</b> and improved support operations using Zendesk, maintaining response times of approximately <b>5–15 minutes</b>.",
        "Coordinated community engagement, moderation, announcements, and member feedback to inform product and operational improvements.",
    ]))
story.append(role("Community Manager", "Gotabit", "Feb 2021 – Oct 2022",
    "Managed community operations, customer support, content coordination, and engagement initiatives, acting as a communication link between users and the technical team.", [
        "Created and published community content across social media, keeping members informed about project updates and activities.",
        "Managed community enquiries and customer support, providing guidance and coordinating technical issues with the technical team.",
        "Programmed customised and general-purpose community bots to automate processes and support community operations.",
        "Welcomed and onboarded new users, hosted AMA sessions, organised community events, and enforced community guidelines fairly.",
        "Prepared weekly progress reports covering community activities, engagement, feedback, and outstanding issues.",
    ]))
story.append(role("Community Management & Growth Contributor", "Betboom", "Jan 2020 – Sep 2021",
    "Created Discord and Telegram communities from scratch and supported their ongoing management for a community of approximately <b>50,000 members</b>.", [
        "Managed member enquiries and customer support, maintaining typical response times of approximately <b>5–7 minutes</b>.",
        "Handled member onboarding, community communications, project updates, campaigns, and engagement activities.",
        "Coordinated with project stakeholders and surfaced member questions, feedback, and recurring concerns for resolution.",
    ]))

story.extend(section("Additional Web3 Projects"))
story.append(p("Dorum  |  SolFutureNFT  |  ChainPeak Global  |  Debonk"))
story.extend(section("Tools"))
story.append(p("Zendesk  |  Discord  |  Telegram  |  X/Twitter  |  LinkedIn  |  Buffer  |  Canva  |  Claude  |  ChatGPT  |  Notion  |  Trello  |  Slack  |  Google Workspace"))
story.extend(section("Education"))
story.append(p("<b>B.Sc.Ed., Mathematics and Education</b>  |  University of Lagos  |  Completed 2026  |  Second Class Upper  |  CGPA: 3.8/5"))

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Wrote {OUT}")