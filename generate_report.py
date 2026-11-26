"""Generate MITM / VTU Project Report PDF with adapted front matter (up to Table of Contents) and 16 numbered body pages."""

import csv
import json
from pathlib import Path

from PIL import Image as PILImage, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image as RLImage,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = Path(__file__).resolve().parent
SHOTS_DIR = BASE_DIR / "screenshots"
LOGOS_DIR = BASE_DIR / "logos"
DATA = json.loads((BASE_DIR / "test_data.json").read_text(encoding="utf-8"))
CODE_LINES = (BASE_DIR / "blinkit_automation.py").read_text(encoding="utf-8").splitlines()
with open(BASE_DIR / DATA["report_files"]["csv"], "r", encoding="utf-8") as f:
    RESULTS = list(csv.DictReader(f))

PDF_PATH = BASE_DIR / "Blinkit_Automation_Project_Report.pdf"

TOPIC_NAME = "Automation Testing Using Selenium on Blinkit E-Commerce"
FULL_REPORT_TITLE = "AUTOMATION TESTING USING SELENIUM ON BLINKIT E-COMMERCE WEBSITE"
INSTITUTE_SHORT = "MITM"
STUDENT_NAME = "JYOTHISH GOUD G E"
STUDENT_USN = "4MH24IS037"
HOD_NAME = "Dr. Sharath Kumar Y H"

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
pdfmetrics.registerFont(TTFont("TNR", str(FONT_DIR / "Times New Roman.ttf")))
pdfmetrics.registerFont(TTFont("TNR-Bold", str(FONT_DIR / "Times New Roman Bold.ttf")))
pdfmetrics.registerFont(TTFont("TNR-Italic", str(FONT_DIR / "Times New Roman Italic.ttf")))
pdfmetrics.registerFont(TTFont("TNR-BoldItalic", str(FONT_DIR / "Times New Roman Bold Italic.ttf")))
registerFontFamily("TNR", normal="TNR", bold="TNR-Bold", italic="TNR-Italic", boldItalic="TNR-BoldItalic")

NAVY = colors.HexColor("#0F172A")
SLATE = colors.HexColor("#1E293B")
MUTED = colors.HexColor("#475569")
GREEN = colors.HexColor("#0C831F")
DARK_GREEN = colors.HexColor("#2E5B1E")
CRIMSON = colors.HexColor("#991B1B")
BLUE_TEXT = colors.HexColor("#1D4ED8")
SOFT_GREEN = colors.HexColor("#ECFDF5")
YELLOW = colors.HexColor("#F8CB46")
SOFT_YELLOW = colors.HexColor("#FEF9C3")
SOFT_BLUE = colors.HexColor("#EFF6FF")
BORDER = colors.HexColor("#94A3B8")
ROW_ALT = colors.HexColor("#F8FAFC")
CODE_BG = colors.HexColor("#F1F5F9")


class ReportDocTemplate(BaseDocTemplate):
    """Two-template document: clean bordered front matter, then numbered body starting at Page 1."""

    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.body_start_page = None
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="main_frame",
        )
        self.addPageTemplates([
            PageTemplate(id="front", frames=[frame], onPage=draw_front_chrome),
            PageTemplate(id="abstract", frames=[frame], onPage=draw_abstract_chrome),
            PageTemplate(id="body", frames=[frame], onPage=draw_body_chrome),
        ])


def build_styles():
    # Strict requested typography: Main heading 16pt, Heading 14pt, Paragraph 12pt, Times New Roman
    return {
        "main_h": ParagraphStyle("main_h", fontName="TNR-Bold", fontSize=16, leading=20, textColor=NAVY, spaceAfter=5, spaceBefore=2),
        "sub_h": ParagraphStyle("sub_h", fontName="TNR-Bold", fontSize=14, leading=18, textColor=GREEN, spaceAfter=4, spaceBefore=6),
        "para": ParagraphStyle("para", fontName="TNR", fontSize=12, leading=15.2, textColor=SLATE, alignment=TA_JUSTIFY, spaceAfter=5),
        "bullet": ParagraphStyle("bullet", fontName="TNR", fontSize=12, leading=15.0, textColor=SLATE, leftIndent=14, firstLineIndent=-10, spaceAfter=3.5),
        "vtu_hdr": ParagraphStyle("vtu_hdr", fontName="TNR-Bold", fontSize=15, leading=19, textColor=colors.black, alignment=TA_CENTER, spaceAfter=2),
        "vtu_sub": ParagraphStyle("vtu_sub", fontName="TNR-Bold", fontSize=12, leading=15, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=8),
        "rep_label": ParagraphStyle("rep_label", fontName="TNR-Bold", fontSize=13, leading=17, textColor=DARK_GREEN, alignment=TA_CENTER, spaceAfter=4),
        "rep_title": ParagraphStyle("rep_title", fontName="TNR-Bold", fontSize=15, leading=20, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=6),
        "rep_code": ParagraphStyle("rep_code", fontName="TNR-Bold", fontSize=12, leading=16, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=14),
        "stu_lbl": ParagraphStyle("stu_lbl", fontName="TNR-Bold", fontSize=12, leading=16, textColor=colors.black, alignment=TA_CENTER, underline=True),
        "stu_val": ParagraphStyle("stu_val", fontName="TNR-Bold", fontSize=13, leading=17, textColor=BLUE_TEXT, alignment=TA_CENTER),
        "dept_hdr": ParagraphStyle("dept_hdr", fontName="TNR-Bold", fontSize=12, leading=16, textColor=colors.black, alignment=TA_CENTER),
        "dept_sub": ParagraphStyle("dept_sub", fontName="TNR", fontSize=12, leading=15.5, textColor=colors.black, alignment=TA_CENTER),
        "cert_dept": ParagraphStyle("cert_dept", fontName="TNR-Bold", fontSize=12, leading=16, textColor=DARK_GREEN, alignment=TA_CENTER),
        "cert_title": ParagraphStyle("cert_title", fontName="TNR-Bold", fontSize=15, leading=19, textColor=CRIMSON, alignment=TA_CENTER, spaceBefore=6, spaceAfter=10),
        "cert_body": ParagraphStyle("cert_body", fontName="TNR", fontSize=12.5, leading=20, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=12),
        "sig_txt": ParagraphStyle("sig_txt", fontName="TNR", fontSize=11.5, leading=15, textColor=colors.black, alignment=TA_LEFT),
        "toc_title": ParagraphStyle("toc_title", fontName="TNR-Bold", fontSize=22, leading=26, textColor=colors.black, alignment=TA_CENTER, spaceBefore=10, spaceAfter=16),
        "tbl_hdr": ParagraphStyle("tbl_hdr", fontName="TNR-Bold", fontSize=9.5, leading=12, textColor=colors.white),
        "tbl_hdr_blk": ParagraphStyle("tbl_hdr_blk", fontName="TNR-Bold", fontSize=10.5, leading=13, textColor=colors.black, alignment=TA_CENTER),
        "tbl_cell": ParagraphStyle("tbl_cell", fontName="TNR", fontSize=9.0, leading=11.4, textColor=NAVY),
        "tbl_cell_blk": ParagraphStyle("tbl_cell_blk", fontName="TNR", fontSize=10.5, leading=14, textColor=colors.black),
        "tbl_cell_c": ParagraphStyle("tbl_cell_c", fontName="TNR-Bold", fontSize=11.5, leading=15, textColor=colors.black, alignment=TA_CENTER),
        "callout": ParagraphStyle("callout", fontName="TNR", fontSize=12, leading=15, textColor=NAVY, alignment=TA_JUSTIFY),
        "code": ParagraphStyle("code", fontName="Courier", fontSize=6.6, leading=8.3, textColor=NAVY, backColor=CODE_BG, leftIndent=5, rightIndent=5),
        "caption": ParagraphStyle("caption", fontName="TNR-Italic", fontSize=10.5, leading=13, textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=4),
    }


def make_table(headers, rows, col_widths, st, pad_v=4):
    data = [[Paragraph(h, st["tbl_hdr"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), st["tbl_cell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), pad_v),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for idx in range(1, len(data)):
        bg = colors.white if idx % 2 == 1 else ROW_ALT
        cmds.append(("BACKGROUND", (0, idx), (-1, idx), bg))
        if str(rows[idx - 1][-1]) == "PASS":
            cmds.append(("BACKGROUND", (-1, idx), (-1, idx), SOFT_GREEN))
    t.setStyle(TableStyle(cmds))
    return t


def make_callout(text: str, st, bg=SOFT_GREEN, accent=GREEN):
    t = Table([[Paragraph(text, st["callout"])]], colWidths=[6.85 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("LINEBEFORE", (0, 0), (0, -1), 3.5, accent),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return t


def framed_photo(filename: str, width_in=5.85, height_in=2.95):
    img = RLImage(str(SHOTS_DIR / filename), width=width_in * inch, height=height_in * inch, kind="proportional")
    t = Table([[img]], colWidths=[(width_in + 0.14) * inch])
    t.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.9, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    t.hAlign = "CENTER"
    return t


def photo_grid_2x2(items, st):
    cells = []
    for i in range(0, len(items), 2):
        row_cells = []
        for fname, cap in items[i : i + 2]:
            img = RLImage(str(SHOTS_DIR / fname), width=3.15 * inch, height=1.88 * inch, kind="proportional")
            inner = Table([[img], [Paragraph(cap, st["caption"])]], colWidths=[3.28 * inch])
            inner.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
                        ("BACKGROUND", (0, 0), (-1, -1), ROW_ALT),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            row_cells.append(inner)
        cells.append(row_cells)
    outer = Table(cells, colWidths=[3.42 * inch, 3.42 * inch])
    outer.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return outer


def architecture_diagram():
    d = Drawing(455, 130)
    boxes = [
        (8, 38, 95, 56, SOFT_YELLOW, "test_data.json", "External Data Feed"),
        (124, 38, 108, 56, SOFT_GREEN, "blinkit_automation.py", "Selenium Engine"),
        (253, 38, 95, 56, SOFT_BLUE, "Chrome + Blinkit", "Live Web App"),
        (368, 38, 78, 56, SOFT_GREEN, "CSV / HTML", "12/12 PASS"),
    ]
    for x, y, w, h, fill, title, sub in boxes:
        d.add(Rect(x, y, w, h, rx=5, ry=5, fillColor=fill, strokeColor=NAVY, strokeWidth=1.1))
        d.add(String(x + w / 2, y + 32, title, fontName="TNR-Bold", fontSize=8.5, fillColor=NAVY, textAnchor="middle"))
        d.add(String(x + w / 2, y + 14, sub, fontName="TNR", fontSize=7.5, fillColor=SLATE, textAnchor="middle"))
    for x1, x2 in [(103, 124), (232, 253), (348, 368)]:
        d.add(Line(x1, 66, x2 - 4, 66, strokeColor=NAVY, strokeWidth=1.2))
        d.add(Polygon([x2, 66, x2 - 6, 69, x2 - 6, 63], fillColor=NAVY, strokeColor=NAVY))
    d.add(String(227, 10, "Figure 4.1: Data-Driven Selenium Automation Architecture", fontName="TNR-Italic", fontSize=9, fillColor=MUTED, textAnchor="middle"))
    return d


def workflow_diagram():
    d = Drawing(455, 148)
    steps = [
        (8, 90, "1. Load JSON", "Read Inputs"),
        (120, 90, "2. Launch Chrome", "TC_01 - TC_02"),
        (232, 90, "3. Set Location", "TC_03 Modal"),
        (344, 90, "4. Login Check", "TC_04 Mobile"),
        (344, 24, "5. Search Loop", "TC_05 - TC_10"),
        (192, 24, "6. Verify Cart", "TC_11 (5 Items)"),
        (42, 24, "7. Report & Quit", "TC_12 CSV/HTML"),
    ]
    for x, y, t, s in steps:
        d.add(Rect(x, y, 100, 42, rx=4, ry=4, fillColor=ROW_ALT, strokeColor=GREEN, strokeWidth=1.1))
        d.add(String(x + 50, y + 25, t, fontName="TNR-Bold", fontSize=8.4, fillColor=NAVY, textAnchor="middle"))
        d.add(String(x + 50, y + 10, s, fontName="TNR", fontSize=7.5, fillColor=SLATE, textAnchor="middle"))
    for x1, x2 in [(108, 120), (220, 232), (332, 344)]:
        d.add(Line(x1, 111, x2 - 3, 111, strokeColor=NAVY, strokeWidth=1))
        d.add(Polygon([x2, 111, x2 - 5, 114, x2 - 5, 108], fillColor=NAVY))
    d.add(Line(394, 90, 394, 69, strokeColor=NAVY, strokeWidth=1))
    d.add(Polygon([394, 66, 391, 72, 397, 72], fillColor=NAVY))
    for x1, x2 in [(344, 292), (192, 142)]:
        d.add(Line(x1, 45, x2 + 3, 45, strokeColor=NAVY, strokeWidth=1))
        d.add(Polygon([x2, 45, x2 + 5, 48, x2 + 5, 42], fillColor=NAVY))
    d.add(String(227, 6, "Figure 6.1: Seven-Phase Automated Execution Pipeline (TC_01 to TC_12)", fontName="TNR-Italic", fontSize=9, fillColor=MUTED, textAnchor="middle"))
    return d


def cart_progression_chart():
    d = Drawing(455, 145)
    bars = [
        ("Item 1 (milk)", 234),
        ("Item 2 (bread)", 299),
        ("Item 3 (butter)", 527),
        ("Item 4 (chips)", 562),
        ("Item 5 (choc.)", 962),
        ("Cart Total", 964),
    ]
    max_v = 1060
    d.add(Line(42, 30, 442, 30, strokeColor=NAVY, strokeWidth=1))
    for i, (lbl, val) in enumerate(bars):
        bw = 42
        bx = 55 + i * 64
        bh = (val / max_v) * 88
        col = GREEN if i < 5 else YELLOW
        d.add(Rect(bx, 30, bw, bh, fillColor=col, strokeColor=NAVY, strokeWidth=0.6))
        d.add(String(bx + bw / 2, 34 + bh, f"Rs.{val}", fontName="TNR-Bold", fontSize=8, fillColor=NAVY, textAnchor="middle"))
        d.add(String(bx + bw / 2, 17, lbl, fontName="TNR", fontSize=7.2, fillColor=SLATE, textAnchor="middle"))
    d.add(String(242, 3, "Figure 9.1: Cumulative Cart Value Progression Across 5 Auto-Searched Items", fontName="TNR-Italic", fontSize=9, fillColor=MUTED, textAnchor="middle"))
    return d


def _draw_border(canvas):
    w, h = A4
    margin = 0.42 * inch
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.3)
    canvas.rect(margin, margin, w - 2 * margin, h - 2 * margin)
    canvas.setLineWidth(0.5)
    canvas.rect(margin + 3, margin + 3, w - 2 * margin - 6, h - 2 * margin - 6)
    return w, h, margin


def draw_front_chrome(canvas, doc):
    """Front matter pages 1 & 2 (Cover & Certificate): clean outer border only."""
    canvas.saveState()
    _draw_border(canvas)
    canvas.restoreState()


def draw_abstract_chrome(canvas, doc):
    """Abstract & TOC page chrome: classic top and bottom double horizontal bars matching reference PDF."""
    w, h = A4
    margin = 0.65 * inch
    canvas.saveState()
    canvas.setStrokeColor(colors.black)
    # Top double bar
    canvas.setLineWidth(2.2)
    canvas.line(margin, h - 0.52 * inch, w - margin, h - 0.52 * inch)
    canvas.setLineWidth(0.8)
    canvas.line(margin, h - 0.57 * inch, w - margin, h - 0.57 * inch)
    # Bottom double bar
    canvas.setLineWidth(2.2)
    canvas.line(margin, 0.56 * inch, w - margin, 0.56 * inch)
    canvas.setLineWidth(0.8)
    canvas.line(margin, 0.61 * inch, w - margin, 0.61 * inch)
    canvas.restoreState()


def draw_body_chrome(canvas, doc):
    """Body pages starting from CHAPTER 1: border + Top-Left Topic + Bottom-Left MITM + Bottom-Right 1..N."""
    phys_page = canvas.getPageNumber()
    if doc.body_start_page is None:
        doc.body_start_page = phys_page
    seq_num = phys_page - doc.body_start_page + 1

    canvas.saveState()
    w, h, margin = _draw_border(canvas)

    canvas.setFont("TNR-Bold", 9.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(margin + 12, h - margin - 16, TOPIC_NAME)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(margin + 8, h - margin - 22, w - margin - 8, h - margin - 22)

    canvas.line(margin + 8, margin + 22, w - margin - 8, margin + 22)
    canvas.setFont("TNR-Bold", 10)
    canvas.setFillColor(NAVY)
    canvas.drawString(margin + 12, margin + 9, INSTITUTE_SHORT)
    canvas.drawRightString(w - margin - 12, margin + 9, str(seq_num))
    canvas.restoreState()


def build_pdf():
    st = build_styles()
    doc = ReportDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=0.68 * inch,
        rightMargin=0.68 * inch,
        topMargin=0.78 * inch,
        bottomMargin=0.78 * inch,
        title=TOPIC_NAME,
    )
    story = []

    def h1(txt):
        story.append(Paragraph(txt, st["main_h"]))

    def h2(txt):
        story.append(Paragraph(txt, st["sub_h"]))

    def p(txt):
        story.append(Paragraph(txt, st["para"]))

    def b(txt):
        story.append(Paragraph(f"• {txt}", st["bullet"]))

    def pb():
        story.append(PageBreak())

    # =========================================================================
    # FRONT PAGE 1: VTU / MITM COVER PAGE (Exact layout of DBMS Final Report P1)
    # =========================================================================
    story.append(Spacer(1, 0.22 * inch))
    story.append(Paragraph("VISVESVARAYA TECHNOLOGICAL UNIVERSITY", ParagraphStyle("dbms_vtu", fontName="TNR-Bold", fontSize=15.5, leading=20, textColor=colors.black, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("JNANA SANGAMA, BELAGAVI – 590018", ParagraphStyle("dbms_bel", fontName="TNR", fontSize=12.5, leading=16, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=8)))
    vtu_img = RLImage(str(LOGOS_DIR / "p1_1_Image16.png"), width=1.22 * inch, height=1.55 * inch, kind="proportional")
    vtu_img.hAlign = "CENTER"
    story.append(vtu_img)
    story.append(Spacer(1, 0.14 * inch))
    story.append(Paragraph("<i>SOFTWARE TESTING</i>", ParagraphStyle("dbms_subj", fontName="TNR-Italic", fontSize=13, leading=17, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph("<i>[Project]</i>", ParagraphStyle("dbms_code", fontName="TNR-Italic", fontSize=12.5, leading=16, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=6)))
    story.append(Paragraph("<b><i>Project Report On</i></b>", ParagraphStyle("dbms_on", fontName="TNR-BoldItalic", fontSize=13, leading=17, textColor=colors.black, alignment=TA_CENTER, spaceAfter=10)))
    story.append(Paragraph('<b>" Automation Testing Using Selenium on Blinkit E-Commerce Website "</b>', ParagraphStyle("dbms_ttl", fontName="TNR-Bold", fontSize=14.5, leading=19, textColor=colors.black, alignment=TA_CENTER, spaceAfter=8)))
    story.append(Paragraph("<b>Submitted by</b>", ParagraphStyle("dbms_sub", fontName="TNR-Bold", fontSize=12.5, leading=16, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=6)))

    team_style_l = ParagraphStyle("tm_l", fontName="TNR-Bold", fontSize=11.5, leading=15, textColor=colors.HexColor("#1E40AF"), alignment=TA_LEFT)
    team_style_r = ParagraphStyle("tm_r", fontName="TNR-Bold", fontSize=11.5, leading=15, textColor=colors.HexColor("#1E40AF"), alignment=TA_LEFT)
    team_tbl = Table(
        [
            [Paragraph("Balakrishna Malage", team_style_l), Paragraph("4MH24IS006", team_style_r)],
            [Paragraph("Hithesh Narayan A", team_style_l), Paragraph("4MH24IS035", team_style_r)],
            [Paragraph("Jyothish Goud G E", team_style_l), Paragraph("4MH24IS037", team_style_r)],
            [Paragraph("Manoj D", team_style_l), Paragraph("4MH24IS056", team_style_r)],
        ],
        colWidths=[2.45 * inch, 1.55 * inch],
    )
    team_tbl.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]))
    team_tbl.hAlign = "CENTER"
    story.append(team_tbl)
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("<b>Under the Guidance of</b>", ParagraphStyle("dbms_gui", fontName="TNR-Bold", fontSize=12.5, leading=16, textColor=CRIMSON, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("<b>PROF. SRIKANTH BHARADWAJ M K</b>", ParagraphStyle("dbms_hod1", fontName="TNR-Bold", fontSize=12, leading=15, textColor=colors.black, alignment=TA_CENTER)))
    story.append(Paragraph("ASSISTANT PROFESSOR<br/>Dept. of ISE<br/>MIT Mysore", ParagraphStyle("dbms_hod2", fontName="TNR", fontSize=11.5, leading=14.5, textColor=colors.black, alignment=TA_CENTER, spaceAfter=10)))

    nba_img = RLImage(str(LOGOS_DIR / "p1_0_Image14.png"), width=0.92 * inch, height=0.92 * inch, kind="proportional")
    mit_img = RLImage(str(LOGOS_DIR / "p1_2_Image17.png"), width=1.12 * inch, height=1.12 * inch, kind="proportional")
    naac_img = RLImage(str(LOGOS_DIR / "p1_3_Image18.png"), width=1.05 * inch, height=0.92 * inch, kind="proportional")
    logo_row = Table([[nba_img, mit_img, naac_img]], colWidths=[1.8 * inch, 2.0 * inch, 1.8 * inch])
    logo_row.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    logo_row.hAlign = "CENTER"
    story.append(logo_row)
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("DEPARTMENT OF INFORMATION SCIENCE &amp; ENGINEERING", st["dept_hdr"]))
    story.append(Paragraph("MAHARAJA INSTITUTE OF TECHNOLOGY MYSORE", st["dept_hdr"]))
    story.append(Paragraph("An Autonomous Institute, Affiliated to VTU, Belagavi", st["dept_hdr"]))
    story.append(Paragraph("BELAWADI, SRIRANGAPATNA TALUK, MANDYA - 571477", st["dept_hdr"]))
    pb()

    # =========================================================================
    # FRONT PAGE 2: CERTIFICATE PAGE (Exact layout of DBMS Final Report P2)
    # =========================================================================
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("MAHARAJA INSTITUTE OF TECHNOLOGY MYSORE", ParagraphStyle("c_mit", fontName="TNR-Bold", fontSize=14.5, leading=19, textColor=colors.HexColor("#0369A1"), alignment=TA_CENTER, spaceAfter=3)))
    story.append(Paragraph("An Autonomous Institute, Affiliated to VTU, Belagavi", ParagraphStyle("c_aff", fontName="TNR", fontSize=12.5, leading=16, textColor=colors.HexColor("#0284C7"), alignment=TA_CENTER, spaceAfter=18)))
    story.append(Paragraph("<u><b>CERTIFICATE</b></u>", ParagraphStyle("c_ttl", fontName="TNR-Bold", fontSize=15, leading=19, textColor=colors.black, alignment=TA_CENTER, spaceAfter=18)))
    mit_cert = RLImage(str(LOGOS_DIR / "p1_2_Image17.png"), width=1.35 * inch, height=1.35 * inch, kind="proportional")
    mit_cert.hAlign = "CENTER"
    story.append(mit_cert)
    story.append(Spacer(1, 0.28 * inch))
    story.append(Paragraph(
        'This is to certify that the Software Testing Project entitled <b>" Automation Testing Using Selenium on Blinkit E-Commerce Website "</b> '
        'has been successfully carried out by <b>Balakrishna Malage [4MH24IS006], Hithesh Narayan A [4MH24IS035], '
        'Jyothish Goud G E [4MH24IS037] and Manoj D [4MH24IS056]</b>, '
        'bonafide students of Maharaja Institute of Technology Mysore, in partial fulfilment of the requirements of Degree of Bachelor of Engineering in '
        'Information Science and Engineering of Visvesvaraya Technological University, Belagavi during the academic year 2026-2027. '
        'The report has been approved as it satisfies the academic requirements with respect to the Project work prescribed for the said degree.',
        ParagraphStyle("c_body", fontName="TNR", fontSize=12, leading=21, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=24),
    ))
    story.append(Spacer(1, 1.05 * inch))
    sig_style = ParagraphStyle("c_sig", fontName="TNR", fontSize=11.5, leading=16, textColor=colors.black, alignment=TA_CENTER)
    hod_sig = Table(
        [[
            Paragraph("------------------------------------<br/>Signature of the Guide<br/>Prof. Srikanth Bharadwaj M K<br/>Assistant Professor<br/>Dept. of ISE", sig_style),
            "",
            Paragraph(f"------------------------------------<br/>Signature of the HOD<br/>{HOD_NAME}<br/>Professor &amp; Head<br/>Dept. of ISE", sig_style),
        ]],
        colWidths=[2.85 * inch, 1.15 * inch, 2.85 * inch],
    )
    hod_sig.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(hod_sig)
    story.append(NextPageTemplate("abstract"))
    pb()

    # =========================================================================
    # FRONT PAGE 3: ABSTRACT PAGE (Exact layout of DBMS Final Report P3)
    # =========================================================================
    story.append(Paragraph("<u><b>ABSTRACT</b></u>", ParagraphStyle("abs_h", fontName="TNR-Bold", fontSize=14, leading=18, textColor=colors.black, alignment=TA_CENTER, spaceAfter=14)))
    abs_style = ParagraphStyle("abs_p", fontName="TNR", fontSize=12, leading=17, textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=12)
    story.append(Paragraph(
        "The Blinkit E-Commerce Automation Testing project is a Python and Selenium WebDriver-based automated quality assurance framework developed to validate end-to-end online grocery shopping workflows. The system provides a reliable, repeatable execution pipeline for verifying browser startup, website navigation, delivery locality selection, mobile login validation, multi-product search, and shopping cart inspection. Its primary objective is to eliminate manual regression effort, prevent human oversight, and ensure consistent functional verification across live Single-Page Application (SPA) interactions.",
        abs_style,
    ))
    story.append(Paragraph(
        "The automation suite consists of structured functional modules covering Chrome WebDriver Session Management, Locality Autocomplete Handling, Login Modal Phone Input Validation, Autonomous Multi-Product Search Loop, and My Cart Drawer Verification. In strict adherence to data-driven testing guidelines, every test input—including the target URL (https://blinkit.com/), serviceable delivery locality (Indiranagar, Bengaluru), mobile number (9876543210), and five search queries (milk, bread, butter, chips, chocolate)—is linked externally through test_data.json with zero hardcoded inputs or manual runtime entry.",
        abs_style,
    ))
    story.append(Paragraph(
        "The framework is implemented using Python 3.13.15, Selenium WebDriver 4.53.0, and Google Chrome controlled through Selenium Manager inside IntelliJ IDEA. Explicit synchronization primitives (WebDriverWait and Expected Conditions), React-safe input clearing (clear_and_type), and resilient partial-class and semantic XPath locators handle dynamic styled-component rendering cleanly. After searching and adding all five items to the cart, the script enters the My Cart drawer and asserts item presence alongside the displayed Bill details and Grand Total (₹964).",
        abs_style,
    ))
    story.append(Paragraph(
        "Live execution against Blinkit achieved a 100% pass rate (12/12 Test Cases PASSED, 0 Failed) with zero assertion errors or timeouts. At session teardown, the script automatically closes Chrome via driver.quit() inside a fail-safe finally block and generates both machine-readable CSV logs (test_results_report.csv) and a styled HTML dashboard (test_results_report.html) for audit review.",
        abs_style,
    ))
    story.append(Paragraph(
        "The project establishes a scalable foundation for future enhancements such as automated cart quantity increment/decrement assertions, negative search and unserviceable locality validation, cross-browser Selenium Grid execution, and GitHub Actions CI/CD integration. By automating repetitive e-commerce testing and producing instant visual and tabular reports, this framework improves QA accuracy, maintainability, and delivery confidence.",
        abs_style,
    ))
    pb()

    # =========================================================================
    # FRONT PAGE 4: TABLE OF CONTENTS (Unchanged as requested)
    # =========================================================================
    story.append(Paragraph("Table of contents", st["toc_title"]))
    toc_data = [
        [Paragraph("<b>Sl.no</b>", st["tbl_hdr_blk"]), Paragraph("<b>Title</b>", st["tbl_hdr_blk"]), Paragraph("<b>Pg.no</b>", st["tbl_hdr_blk"])],
        [Paragraph("1", st["tbl_cell_c"]), Paragraph("<b>Chapter 1: Introduction &amp; Project Overview</b>", st["tbl_cell_c"]), Paragraph("1", st["tbl_cell_c"])],
        [Paragraph("2", st["tbl_cell_c"]), Paragraph("<b>Chapter 2: Problem Statement &amp; Guidelines Compliance</b>", st["tbl_cell_c"]), Paragraph("2", st["tbl_cell_c"])],
        [Paragraph("3", st["tbl_cell_c"]), Paragraph("<b>Chapter 3: Tool Evaluation &amp; System Requirements</b>", st["tbl_cell_c"]), Paragraph("3", st["tbl_cell_c"])],
        [Paragraph("4", st["tbl_cell_c"]), Paragraph("<b>Chapter 4: System Architecture &amp; External Data Feed</b>", st["tbl_cell_c"]), Paragraph("4", st["tbl_cell_c"])],
        [Paragraph("5", st["tbl_cell_c"]), Paragraph("<b>Chapter 5: Website Photos &amp; UI Explanation</b>", st["tbl_cell_c"]), Paragraph("5", st["tbl_cell_c"])],
        [Paragraph("6", st["tbl_cell_c"]), Paragraph("<b>Chapter 6: Automation Workflow &amp; Element Locators</b>", st["tbl_cell_c"]), Paragraph("9", st["tbl_cell_c"])],
        [Paragraph("7", st["tbl_cell_c"]), Paragraph("<b>Chapter 7: Detailed Test Cases Specification</b>", st["tbl_cell_c"]), Paragraph("10", st["tbl_cell_c"])],
        [Paragraph("8", st["tbl_cell_c"]), Paragraph("<b>Chapter 8: Implementation Code &amp; Analysis</b>", st["tbl_cell_c"]), Paragraph("12", st["tbl_cell_c"])],
        [Paragraph("9", st["tbl_cell_c"]), Paragraph("<b>Chapter 9: Execution Results, Cart Chart &amp; Challenges</b>", st["tbl_cell_c"]), Paragraph("14", st["tbl_cell_c"])],
        [Paragraph("10", st["tbl_cell_c"]), Paragraph("<b>Chapter 10: IntelliJ Guide, Conclusion &amp; References</b>", st["tbl_cell_c"]), Paragraph("16", st["tbl_cell_c"])],
    ]
    toc_tbl = Table(toc_data, colWidths=[1.2 * inch, 4.15 * inch, 1.3 * inch], rowHeights=[0.48 * inch] + [0.46 * inch] * 10)
    toc_tbl.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.9, colors.black), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    toc_tbl.hAlign = "CENTER"
    story.append(toc_tbl)
    story.append(NextPageTemplate("body"))
    pb()

    # =========================================================================
    # NUMBERED BODY PAGES 1..16 (Starting directly with CHAPTER 1 = Page 1)
    # =========================================================================
    # ---------------- PAGE 1: CHAPTER 1 - INTRODUCTION ----------------
    h1("CHAPTER 1: INTRODUCTION")
    h2("1.1 Overview of Software Test Automation")
    p("Software quality assurance (QA) ensures that web applications deliver accurate functionality, consistent UI state, and resilient workflows across every release. Manual testing requires repetitive human interaction across browsers and is prone to missed edge cases when verifying multi-step user journeys. Automated testing addresses these limitations by executing repeatable browser scripts that locate elements, simulate realistic user input, evaluate programmatic assertions, and generate audit-ready execution reports.")
    h2("1.2 Evolution of Quick-Commerce & Blinkit SPA Architecture")
    p("Blinkit (<i>https://blinkit.com/</i>) is one of India's fastest-growing quick-commerce platforms, delivering groceries, dairy, snacks, bakery items, and electronics in 10–20 minutes. From a testing perspective, Blinkit is a rich React Single-Page Application (SPA): product availability depends on a locality gate, search queries dynamically fetch matching items on <i>/s/</i>, and clicking <i>ADD</i> updates React cart state, badges, and slide-over drawers in real time without full page reloads.")
    h2("1.3 Project Scope & Functional Coverage")
    b("<b>Browser & Navigation Control:</b> Launch a clean Chrome WebDriver session and open Blinkit.")
    b("<b>Data-Driven Configuration:</b> Load every test input dynamically from <i>test_data.json</i>.")
    b("<b>Locality & Authentication Validation:</b> Select a serviceable city locality and verify mobile phone entry inside the Login modal.")
    b("<b>Autonomous Multi-Product Cart Flow:</b> Search 5 items sequentially, add each to the cart, open <i>My Cart</i> to verify all 5 items and grand total, export CSV/HTML reports, and terminate Chrome cleanly.")
    h2("1.4 Key Software Testing Terminology")
    story.append(make_table(
        ["Term", "Technical Role in This Project"],
        [
            ["WebDriver Session", "Live browser control channel established between Python and Google Chrome"],
            ["Explicit Wait (WebDriverWait)", "Polls DOM conditions up to 15 seconds until elements become visible or clickable"],
            ["Assertion", "Boolean verification checking actual browser state matches expected test outcome"],
            ["Data-Driven Testing", "Separating test inputs (test_data.json) from automation code (blinkit_automation.py)"],
            ["DOM Locator", "CSS selector or XPath expression uniquely identifying an interactive page element"],
        ],
        [2.1 * inch, 4.75 * inch],
        st,
        pad_v=4,
    ))
    h2("1.5 Industrial Relevance of Automated Cart Verification")
    p("In production e-commerce teams, search-to-cart regression suites run before every deployment because broken add-to-cart handlers or stale cart totals directly impact customer conversion. Automating a 5-item cart cycle validates search indexing, inventory availability, state persistence, and subtotal arithmetic simultaneously.")
    pb()

    # ---------------- PAGE 2: CHAPTER 2 - PROBLEM STATEMENT & GUIDELINES ----------------
    h1("CHAPTER 2: PROBLEM STATEMENT, OBJECTIVES & GUIDELINES")
    h2("2.1 Problem Statement")
    p("Testing an e-commerce search-to-cart flow manually across 4–5 distinct products is slow and error-prone—testers must repeatedly set delivery location, search each product, add items, open the cart, and verify names and totals. Additionally, hardcoding URLs, mobile numbers, or product lists inside Python code violates maintainability because modifying test inputs requires editing source code.")
    h2("2.2 Project Objectives")
    b("Build a modular, data-driven Selenium automation framework linked to an external <i>test_data.json</i> file.")
    b("Automate searching 5 items on Blinkit independently and adding each matched product to the shopping cart.")
    b("Open the <i>My Cart</i> view and programmatically assert that all 5 products and bill totals appear accurately.")
    b("Export timestamped CSV and HTML test reports alongside formal test documentation and visual evidence.")
    h2("2.3 Assignment Guidelines Compliance Matrix")
    story.append(make_table(
        ["Prescribed Guideline", "Implementation in This Project", "Verification"],
        [
            ["Create a WebDriver session", "webdriver.Chrome() + driver.maximize_window()", "TC_01 PASS"],
            ["Navigate to a Web page", "driver.get(website_url) loaded from test_data.json", "TC_02 PASS"],
            ["Locate web elements", "CSS selectors, partial classes, semantic XPath + WebDriverWait", "TC_03 – TC_11"],
            ["Perform actions on elements", "Type locality, check phone, search 5 items, click ADD, open cart", "TC_03 – TC_11"],
            ["Assert actions did correct thing", "Title, URL, button enabled, badge count 1..5, 5/5 items in cart", "12/12 PASS"],
            ["Report assertion results", "Console summary + test_results_report.csv & .html", "Automated"],
            ["End the WebDriver session", "driver.quit() inside try/finally block", "TC_12 PASS"],
            ["Inputs via linked external file", "100% of inputs read from test_data.json", "Verified"],
        ],
        [1.95 * inch, 3.85 * inch, 1.05 * inch],
        st,
    ))
    story.append(Spacer(1, 0.1 * inch))
    h2("2.4 Target vs. Achieved Outcomes")
    story.append(make_callout("<b>100% Guideline Alignment:</b> Every requirement from the project specification—including external file-driven inputs, multi-item autonomous search, shopping cart entry & verification, assertion reporting, and session cleanup—was verified live on Blinkit with 12/12 PASS.", st))
    pb()

    # ---------------- PAGE 3: CHAPTER 3 - TOOL EVALUATION & REQUIREMENTS ----------------
    h1("CHAPTER 3: TOOL EVALUATION & SYSTEM REQUIREMENTS")
    h2("3.1 Manual Testing vs. Automated Testing")
    story.append(make_table(
        ["Evaluation Parameter", "Manual Testing", "Automated Testing (Python + Selenium)"],
        [
            ["Execution Time", "3–5 minutes per 5-item verification cycle", "Completes 12 verified test cases in ~55 seconds"],
            ["Input Flexibility", "Tester manually types city, phone & products", "test_data.json supplies all inputs automatically"],
            ["Assertion Accuracy", "Subject to human visual oversight", "Exact programmatic regex & DOM text assertions"],
            ["Auditability", "Manual notes and ad-hoc screenshots", "Timestamped CSV & HTML execution dashboards"],
        ],
        [1.6 * inch, 2.35 * inch, 2.9 * inch],
        st,
    ))
    h2("3.2 Tool Selection Rationale (Selenium vs. Alternatives)")
    story.append(make_table(
        ["Automation Tool", "Strengths", "Reason for Final Choice"],
        [
            ["Selenium WebDriver (Chosen)", "W3C standard, Python 3.13 support, built-in Selenium Manager, IntelliJ support", "Best fit for cross-platform college & industry QA"],
            ["Katalon Studio", "GUI recorder with built-in keywords", "Heavier IDE footprint; less transparent Python code control"],
            ["Cypress", "Fast JS runner inside browser", "Restricted to JS/TS; weaker multi-origin handling"],
            ["Playwright", "Modern async API and auto-wait", "Course guidelines emphasize Selenium / Katalon"],
        ],
        [1.7 * inch, 2.55 * inch, 2.6 * inch],
        st,
    ))
    h2("3.3 Hardware & Software Environment")
    story.append(make_table(
        ["Category", "Specification Used"],
        [
            ["Operating System & Hardware", "macOS (Apple Mac), Minimum 8 GB RAM, Broadband Internet"],
            ["Web Browser & Driver", "Google Chrome + Selenium Manager (selenium 4.53.0)"],
            ["Runtime & IDE", "Python 3.13.15 (/usr/local/bin/python3) + IntelliJ IDEA (Python Plugin)"],
            ["Dependencies (requirements.txt)", "selenium>=4.0.0, python-pptx>=1.0.0 (plus reportlab, pypdf)"],
        ],
        [2.2 * inch, 4.65 * inch],
        st,
    ))
    h2("3.4 Project Directory Structure")
    dir_tree = """/Users/apple/Desktop/software testing/
├── blinkit_automation.py                     # Main 12-TC Selenium script
├── test_data.json                            # External linked data feed
├── requirements.txt                          # Python dependencies manifest
├── test_results_report.csv / .html           # Automated CSV & HTML test reports
├── TEST_CASES_DOCUMENTATION.md               # Formal QA test case specification
├── Blinkit_Automation_Testing_PPT.pptx       # 12-slide project presentation
├── Blinkit_Automation_Project_Report.pdf     # MITM/VTU technical project report
├── screenshots/                              # 10 live Blinkit shots + 3 diagrams
└── .idea/runConfigurations/blinkit_automation.xml  # IntelliJ IDEA Run config"""
    story.append(Preformatted(dir_tree, st["code"]))
    story.append(Spacer(1, 0.06 * inch))
    p("<b>Selenium Manager Advantage:</b> Selenium 4.53 automatically detects the installed Google Chrome binary on macOS and manages a matching ChromeDriver without manual PATH setup.")
    h2("3.5 Browser & Driver Lifecycle Management")
    p("Each execution creates an ephemeral Chrome session with clean localStorage and cookies, eliminating cross-run state leakage. Session cleanup is guaranteed by wrapping execution in a structured <i>try / except / finally</i> block calling <i>driver.quit()</i>.")
    pb()

    # ---------------- PAGE 4: CHAPTER 4 - ARCHITECTURE & DATA FEED ----------------
    h1("CHAPTER 4: SYSTEM ARCHITECTURE & EXTERNAL DATA FEED")
    h2("4.1 Data-Driven Framework Architecture")
    p("The framework separates <b>test inputs</b> from <b>test logic</b>. At startup, <i>blinkit_automation.py</i> loads <i>test_data.json</i>, drives Google Chrome via Selenium WebDriver, validates assertions across 12 test cases, and writes both <i>test_results_report.csv</i> and <i>test_results_report.html</i>.")
    story.append(architecture_diagram())
    h2("4.2 External Linked Input File (test_data.json)")
    story.append(Preformatted(json.dumps(DATA, indent=2), st["code"]))
    story.append(Spacer(1, 0.06 * inch))
    h2("4.3 JSON Parameter Mapping Table")
    story.append(make_table(
        ["JSON Field", "Mapped Test Case(s)", "Role During Automated Execution"],
        [
            ["website_url & expected_title_keyword", "TC_02", "Navigates Chrome to Blinkit and asserts title match"],
            ["delivery_location", "TC_03", "Populates locality modal and picks first autocomplete match"],
            ["user_credentials.mobile_no", "TC_04", "Validates Login modal 10-digit phone field & Continue button"],
            ["products (5-item array)", "TC_06 – TC_10", "Drives autonomous search, ADD click & cart count assertions"],
            ["timeouts & report_files", "TC_01 – TC_12", "Configures explicit wait (15s), pauses (1.5s) & CSV/HTML paths"],
        ],
        [2.2 * inch, 1.15 * inch, 3.5 * inch],
        st,
    ))
    pb()

    # ---------------- PAGE 5: CHAPTER 5 - WEBSITE PHOTOS (PART 1) ----------------
    h1("CHAPTER 5: WEBSITE PHOTOS & EXPLANATION (PART 1)")
    h2("5.1 Delivery Location Selection Modal (TC_03)")
    story.append(framed_photo("01_location_modal.png", width_in=5.85, height_in=2.95))
    story.append(Paragraph("Figure 5.1: Blinkit Delivery Location Modal Showing Autocomplete Suggestions for Indiranagar", st["caption"]))
    p("<b>Detailed Explanation:</b> When Blinkit loads, a modal dialog prompts for a delivery locality because store catalog, pricing, and delivery ETA depend on the nearest dark store. In <i>TC_03</i>, the script locates <i>input[name='select-locality']</i>, types <i>Indiranagar, Bengaluru</i> from <i>test_data.json</i>, waits for <i>LocationSearchList__LocationListContainer</i>, and clicks the first suggestion.")
    h2("5.2 Blinkit Storefront Home Page After Locality Selection")
    story.append(framed_photo("01b_home_page.png", width_in=5.85, height_in=2.95))
    story.append(Paragraph("Figure 5.2: Blinkit Home Storefront with Selected Locality, Top Search Bar, Login & My Cart", st["caption"]))
    p("<b>Detailed Explanation:</b> After the locality modal dismisses, Blinkit renders the live storefront header showing <i>Delivery in 8 minutes</i> for <i>Indiranagar, Bengaluru</i>, the global search bar anchor (<i>a[href*='/s/']</i>), the <i>Login</i> trigger, and the <i>My Cart</i> counter.")
    pb()

    # ---------------- PAGE 6: CHAPTER 5 - WEBSITE PHOTOS (PART 2) ----------------
    h1("CHAPTER 5: WEBSITE PHOTOS & EXPLANATION (PART 2)")
    h2("5.3 Login Modal & Mobile Number Input Validation (TC_04)")
    story.append(framed_photo("02_login_modal.png", width_in=5.85, height_in=2.95))
    story.append(Paragraph("Figure 5.3: Blinkit Login Modal Accepting 10-Digit Mobile Number from test_data.json", st["caption"]))
    p("<b>Detailed Explanation:</b> Clicking <i>Login</i> opens Blinkit's phone authentication modal. The automation script locates <i>input.login-phone__input</i>, injects <i>9876543210</i> from <i>test_data.json</i>, and asserts that the 10-digit value is retained and the green <i>Continue</i> button becomes enabled—validating form behavior cleanly without bypassing SMS OTP verification.")
    h2("5.4 Live Product Search & First Add-to-Cart Action (TC_05 – TC_06)")
    story.append(framed_photo("03_search_add_to_cart.png", width_in=5.85, height_in=2.95))
    story.append(Paragraph("Figure 5.4: Blinkit Search Route (/s/) Showing Results for 'milk' and Cart Badge '1 item'", st["caption"]))
    p("<b>Detailed Explanation:</b> Navigating to <i>https://blinkit.com/s/</i> opens the dedicated SPA search route. The script enters <i>milk</i>, waits for matching product cards, extracts the product title, clicks <i>ADD</i>, and asserts the top-right cart badge updates to <i>1 item | ₹234</i>.")
    pb()

    # ---------------- PAGE 7: CHAPTER 5 - WEBSITE PHOTOS (PART 3 - 2x2 GALLERY) ----------------
    h1("CHAPTER 5: WEBSITE PHOTOS & EXPLANATION (PART 3)")
    h2("5.5 Automated Search-and-Add Loop Across Items 2 to 5 (TC_07 – TC_10)")
    p("After adding <i>milk</i>, the automation loop clears the React search input using <i>clear_and_type()</i> and sequentially searches <b>bread</b>, <b>butter</b>, <b>chips</b>, and <b>chocolate</b>. Figures 5.5–5.8 capture live browser proof at each step as the cart counter increments from <i>2 items</i> to <i>5 items</i>.")
    story.append(photo_grid_2x2([
        ("03b_search_bread.png", "Figure 5.5: Search 'bread' -> Added (2 items)"),
        ("03c_search_butter.png", "Figure 5.6: Search 'butter' -> Added (3 items)"),
        ("03d_search_chips.png", "Figure 5.7: Search 'chips' -> Added (4 items)"),
        ("03e_search_chocolate.png", "Figure 5.8: Search 'chocolate' -> Added (5 items)"),
    ], st))
    story.append(Spacer(1, 0.08 * inch))
    h2("5.6 Per-Iteration Verification Table")
    story.append(make_table(
        ["Test Case", "Query (JSON)", "Captured Product Title", "Asserted Cart Badge"],
        [
            ["TC_07", "bread", "Modern 100% Whole Wheat Bread (Zero Maida)", "2 items | ₹299"],
            ["TC_08", "butter", "Akshayakalpa Organic Cooking Organic Butter", "3 items | ₹527"],
            ["TC_09", "chips", "Bingo Masala Massacre Potato Chips", "4 items | ₹562"],
            ["TC_10", "chocolate", "Celebrations Assorted Chocolate Gift Pack", "5 items | ₹962"],
        ],
        [0.85 * inch, 1.0 * inch, 3.55 * inch, 1.45 * inch],
        st,
        pad_v=4,
    ))
    story.append(Spacer(1, 0.06 * inch))
    p("<b>Loop Synchronization:</b> Before clicking <i>ADD</i> on each query, <i>WebDriverWait</i> ensures the search heading matches the newly typed keyword so stale cards from the previous product are never clicked.")
    story.append(make_callout("<b>Zero Manual Selection:</b> Every product search, add-to-cart click, and badge increment verification runs autonomously across all items listed in <i>test_data.json</i>.", st))
    pb()

    # ---------------- PAGE 8: CHAPTER 5 - WEBSITE PHOTOS (PART 4) ----------------
    h1("CHAPTER 5: WEBSITE PHOTOS & EXPLANATION (PART 4)")
    h2("5.7 My Cart Drawer Inspection & Item Verification (TC_11)")
    story.append(framed_photo("04_cart_drawer.png", width_in=5.85, height_in=2.95))
    story.append(Paragraph("Figure 5.9: Blinkit My Cart Drawer Displaying All 5 Added Products & Total", st["caption"]))
    p("<b>Detailed Explanation:</b> Clicking <i>[class*='CartButton__Container']</i> opens the slide-over <i>My Cart</i> drawer. The script waits for <i>Bill details</i>, verifies all 5 captured product names appear inside the active cart view simultaneously, and extracts the displayed <i>Grand total</i>.")
    h2("5.8 Self-Contained HTML Test Execution Dashboard")
    story.append(framed_photo("05_html_report.png", width_in=5.85, height_in=2.95))
    story.append(Paragraph("Figure 5.10: Generated HTML Execution Report Confirming 12/12 PASSED", st["caption"]))
    p("<b>Detailed Explanation:</b> Once <i>driver.quit()</i> closes Chrome, <i>write_reports()</i> saves both <i>test_results_report.csv</i> and <i>test_results_report.html</i> with executive KPI cards and color-coded status rows for instant faculty inspection.")
    pb()

    # ---------------- PAGE 9: CHAPTER 6 - WORKFLOW & LOCATORS ----------------
    h1("CHAPTER 6: AUTOMATION WORKFLOW & LOCATOR STRATEGY")
    h2("6.1 Seven-Phase Automation Flowchart")
    story.append(workflow_diagram())
    h2("6.2 Resilient Element Locator & Synchronization Table")
    story.append(make_table(
        ["UI Element", "Strategy", "Selector Expression", "Reliability Rationale"],
        [
            ["Location Input", "CSS", "input[name='select-locality']", "Stable HTML name attribute"],
            ["Location Suggestion", "CSS Prefix", "[class*='LocationSearchList__LocationListContainer']", "Ignores styled-component hash"],
            ["Login Button", "XPath", "//div[normalize-space()='Login'] | //button[normalize-space()='Login']", "Matches visible label"],
            ["Mobile Input", "CSS", "input.login-phone__input", "Static semantic class"],
            ["Search Anchor", "CSS", "a[href*='/s/']", "Stable SPA route href"],
            ["Search Input", "CSS Prefix", "input[class*='SearchBarContainer__Input']", "Active SPA search input"],
            ["First ADD Button", "XPath", "(//*[normalize-space(text())='ADD'])[1]", "First matching product card"],
            ["Cart Container", "CSS Prefix", "[class*='CartButton__Container']", "Reads live count & subtotal"],
            ["Cart Drawer Header", "XPath", "//*[normalize-space()='My Cart']", "Confirms drawer opened"],
        ],
        [1.25 * inch, 0.85 * inch, 3.0 * inch, 1.75 * inch],
        st,
    ))
    h2("6.3 Explicit Wait Synchronization Strategy")
    p("Blinkit's React components render asynchronously over network calls. Rather than relying on brittle blind delays, the script configures <i>WebDriverWait(driver, 15)</i> with <i>visibility_of_element_located</i>, <i>element_to_be_clickable</i>, <i>invisibility_of_element_located</i>, and a custom lambda predicate checking live cart item count increments.")
    h2("6.4 Why Partial Class & Semantic XPath Selectors Matter")
    p("Modern CSS-in-JS libraries append build-specific hashes to class names. Pairing attribute selectors like <i>input[name='select-locality']</i> with prefix wildcards (<i>[class*='CartButton__Container']</i>) and visible-text XPaths keeps the test suite resilient across Blinkit UI updates.")
    pb()

    # ---------------- PAGE 10: CHAPTER 7 - TEST CASES PART 1 ----------------
    h1("CHAPTER 7: DETAILED TEST CASES SPECIFICATION (PART 1)")
    p("Table 7.1 documents the IEEE-829 test case definitions for browser launch, URL navigation, locality selection, mobile login validation, search page entry, and the first product addition (<b>TC_01 to TC_06</b>).")
    tc_p1 = [
        ["TC_01", "Session", "Launch Chrome WebDriver & maximize window", "Chrome", "Active session started", "PASS"],
        ["TC_02", "Navigation", "Navigate to Blinkit URL from JSON", "https://blinkit.com/", "Title includes 'Blinkit'", "PASS"],
        ["TC_03", "Location", "Enter locality & click first suggestion", "Indiranagar, Bengaluru", "Locality selected; modal closes", "PASS"],
        ["TC_04", "Auth Modal", "Open Login & type 10-digit mobile no", "9876543210", "Phone accepted; Continue enabled", "PASS"],
        ["TC_05", "Search UI", "Click search bar to open /s/ page", "Click a[href*='/s/']", "Search input visible on /s/", "PASS"],
        ["TC_06", "Item 1", "Search 'milk' & click ADD on first card", "Search='milk'", "Item added; badge = 1 item", "PASS"],
    ]
    story.append(make_table(["TC ID", "Module", "Test Scenario", "Input (JSON)", "Expected Result", "Status"], tc_p1, [0.65 * inch, 0.85 * inch, 2.0 * inch, 1.3 * inch, 1.45 * inch, 0.6 * inch], st))
    story.append(Spacer(1, 0.1 * inch))
    h2("7.1 Preconditions & Entry Criteria")
    b("Google Chrome and Selenium 4.53.0 are installed on macOS under Python 3.13.15 (/usr/local/bin/python3).")
    b("All test feeds reside inside <i>test_data.json</i> and are never hardcoded inside Python code or entered manually.")
    b("Every test case asserts concrete browser state (URL, title, enabled attribute, badge integer, or cart DOM text) before recording <b>PASS</b>.")
    h2("7.2 Test Environment, Isolation & Risk Mitigation")
    p("Each WebDriver invocation creates a fresh, isolated Chrome profile with empty cookies and zero pre-existing cart items. This guarantees deterministic starting state so <i>TC_06</i> always begins from an empty cart and increments cleanly from <i>0</i> to <i>1</i>.")
    p("To mitigate transient network latency when Blinkit loads dark-store search inventory, every locator lookup is wrapped in a 15-second explicit wait, and <i>scrollIntoView</i> centers target buttons before clicking.")
    h2("7.2b Coverage Breakdown (TC_01 – TC_06)")
    story.append(make_table(
        ["Coverage Area", "Test Cases", "Verification Mechanism"],
        [
            ["Environment & Navigation", "TC_01, TC_02", "Session ID validation & document title keyword assertion"],
            ["Locality & Auth Boundary", "TC_03, TC_04", "Autocomplete click + 10-digit mobile acceptance & button state"],
            ["Search Discovery & Cart", "TC_05, TC_06", "Route URL (/s/) check + initial '1 item' cart badge assertion"],
        ],
        [1.95 * inch, 1.15 * inch, 3.75 * inch],
        st,
        pad_v=4,
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(make_callout("<b>Design Principle:</b> Decoupling <i>test_data.json</i> from <i>blinkit_automation.py</i> ensures that any tester can validate new delivery localities or product lists simply by editing JSON values.", st, bg=SOFT_BLUE, accent=NAVY))
    pb()

    # ---------------- PAGE 11: CHAPTER 7 - TEST CASES PART 2 ----------------
    h1("CHAPTER 7: DETAILED TEST CASES SPECIFICATION (PART 2)")
    p("Table 7.2 details the remaining four product search-and-add iterations, complete <i>My Cart</i> drawer verification, and WebDriver session teardown (<b>TC_07 to TC_12</b>).")
    tc_p2 = [
        ["TC_07", "Item 2", "Clear search, query 'bread', click ADD", "Search='bread'", "Bread added; badge = 2 items", "PASS"],
        ["TC_08", "Item 3", "Clear search, query 'butter', click ADD", "Search='butter'", "Butter added; badge = 3 items", "PASS"],
        ["TC_09", "Item 4", "Clear search, query 'chips', click ADD", "Search='chips'", "Chips added; badge = 4 items", "PASS"],
        ["TC_10", "Item 5", "Clear search, query 'chocolate', click ADD", "Search='chocolate'", "Chocolate added; badge = 5 items", "PASS"],
        ["TC_11", "Cart View", "Open My Cart & verify all 5 items", "Expected=5 items", "My Cart, Bill details & 5/5 items", "PASS"],
        ["TC_12", "Teardown", "Close browser & write CSV/HTML reports", "driver.quit()", "Session closed; reports saved", "PASS"],
    ]
    story.append(make_table(["TC ID", "Module", "Test Scenario", "Input (JSON)", "Expected Result", "Status"], tc_p2, [0.65 * inch, 0.85 * inch, 2.0 * inch, 1.3 * inch, 1.45 * inch, 0.6 * inch], st))
    story.append(Spacer(1, 0.1 * inch))
    h2("7.3 Assertion & Fail-Safe Teardown Rules")
    b("Each loop iteration parses the integer item count from <i>CartButton__Container</i> and asserts equality with the expected 1-based counter.")
    b("In <i>TC_11</i>, all 5 captured product names are matched case-insensitively against the cart drawer text, and <i>Grand total</i> is extracted via regex.")
    b("The <i>try / except / finally</i> block guarantees <i>driver.quit()</i> and CSV/HTML report output even on exceptions.")
    h2("7.4 Post-Conditions & Exit Criteria")
    p("A test suite run is classified as <b>PASSED</b> only when all 12 test cases return status <i>PASS</i>, zero unhandled <i>TimeoutException</i> or <i>AssertionError</i> events occur, both <i>test_results_report.csv</i> and <i>test_results_report.html</i> are written to disk, and the Chrome browser process exits with return code <i>0</i>.")
    h2("7.5 Traceability Summary & Exit Checklist")
    p("Every requirement—locality gate, login validation, 5-item autonomous search, cart drawer inspection, and external JSON data linkage—maps directly to one or more verified test cases above.")
    story.append(make_table(
        ["Exit Criterion", "Target Threshold", "Actual Result"],
        [
            ["Total Test Cases Executed", "12 / 12 Executed", "12 / 12 Executed"],
            ["Assertion Pass Percentage", "100% PASS (0 Failures)", "100% PASS (12/12)"],
            ["Cart Verification Accuracy", "All 5 Searched Items Matched", "5/5 Items Matched (₹964)"],
            ["Audit Reports Persisted", "CSV & HTML Written Cleanly", "Both Reports Verified"],
        ],
        [2.45 * inch, 2.2 * inch, 2.2 * inch],
        st,
        pad_v=4,
    ))
    pb()

    # ---------------- PAGE 12: CHAPTER 8 - CODE PART 1 ----------------
    h1("CHAPTER 8: IMPLEMENTATION CODE (PART 1)")
    p("Listing 8.1 presents the external JSON loader, React-safe input clearing helper, product card title extractor, and CSV/HTML report setup from <i>blinkit_automation.py</i> (Lines 1–54):")
    story.append(Preformatted("\n".join(CODE_LINES[:54]), st["code"]))
    h2("8.1 Helper Functions Design Analysis")
    b("<b>load_test_data():</b> Resolves <i>test_data.json</i> relative to <i>__file__</i> so the script runs reliably from IntelliJ IDEA or any directory.")
    b("<b>clear_and_type():</b> Sends OS-agnostic Select-All (<i>Cmd+A</i> / <i>Ctrl+A</i>) + <i>Backspace</i> so React's controlled search state resets cleanly before each query.")
    b("<b>extract_product_title_from_card():</b> Filters out delivery ETA badges (<i>11 MINS</i>), discount tags, and currency lines to isolate the exact product name for Cart verification.")
    pb()

    # ---------------- PAGE 13: CHAPTER 8 - CODE PART 2 ----------------
    h1("CHAPTER 8: IMPLEMENTATION CODE (PART 2)")
    p("Listing 8.2 shows the core WebDriver execution and assertion logic inside <i>run_automation()</i> covering browser startup, Blinkit navigation, locality selection, mobile input validation, and search startup (Lines 152–212):")
    story.append(Preformatted("\n".join(CODE_LINES[151:212]), st["code"]))
    h2("8.2 Search Loop & Cart Drawer Assertion Logic")
    p("Following search initialization, the loop iterates over <i>products</i> from <i>test_data.json</i>, clears the input via <i>clear_and_type()</i>, scrolls the first <i>ADD</i> button into view, clicks it, and asserts the live cart badge matches the expected count. Finally, <i>TC_11</i> opens <i>My Cart</i>, waits for <i>Bill details</i>, and verifies every added item name appears inside the cart drawer.")
    pb()

    # ---------------- PAGE 14: CHAPTER 9 - EXECUTION LOGS & CSV RESULTS ----------------
    h1("CHAPTER 9: EXECUTION LOGS & CSV AUDIT RESULTS")
    h2("9.1 Captured Console Execution Transcript")
    console_log = """===== BLINKIT E-COMMERCE AUTOMATION TESTING STARTED =====
Loaded external data from: test_data.json
Target Website: https://blinkit.com/ | Products: ['milk', 'bread', 'butter', 'chips', 'chocolate']

[PASS] TC_01 - Create Chrome WebDriver session | Session started (ID: 40660b953ecb...)
[PASS] TC_02 - Navigate to Blinkit website | Loaded title: '30,000+ products delivered to your doorstep | Blinkit'
[PASS] TC_03 - Select delivery location | Selected location: 'Indiranagar, Bengaluru, Karnataka, India'
[PASS] TC_04 - Validate Login modal mobile number input | Entered '9876543210'; Continue enabled=True
[PASS] TC_05 - Navigate to product search bar | Opened 'https://blinkit.com/s/'
[PASS] TC_06 - Search 'milk' and add item to cart | Added 'Milky Mist Pro+ 25 g High Protein Milk - Pack of 3'
[PASS] TC_07 - Search 'bread' and add item to cart | Added 'Modern 100% Whole Wheat Bread (Zero Maida)'
[PASS] TC_08 - Search 'butter' and add item to cart | Added 'Akshayakalpa Organic Cooking Organic Butter'
[PASS] TC_09 - Search 'chips' and add item to cart | Added 'Bingo Masala Massacre Potato Chips'
[PASS] TC_10 - Search 'chocolate' and add item to cart | Added 'Celebrations Assorted Chocolate Gift Pack'
[PASS] TC_11 - Open shopping cart and verify all 5 added items | Verified 5/5 items in cart (₹964)
[PASS] TC_12 - Close browser and end WebDriver session | WebDriver session closed successfully
===== SUMMARY: 12/12 PASSED, 0 FAILED ====="""
    story.append(Preformatted(console_log, st["code"]))
    h2("9.2 Generated CSV Audit Table (test_results_report.csv)")
    csv_rows = [[r["Test_Case_ID"], r["Scenario"], r["Actual_Result"][:70], r["Status"]] for r in RESULTS]
    story.append(make_table(["TC ID", "Scenario", "Actual Observed Result", "Status"], csv_rows, [0.65 * inch, 1.95 * inch, 3.65 * inch, 0.6 * inch], st, pad_v=3.5))
    story.append(Spacer(1, 0.08 * inch))
    story.append(make_callout("<b>Execution Audit Summary:</b> Total runtime from WebDriver initialization (09:53:47) to clean session termination (09:54:36) was <b>49 seconds</b>, with <b>12/12 PASS</b> and <b>0 failures</b>.", st))
    h2("9.3 Audit Verification Notes")
    p("Both output formats serve complementary roles: <i>test_results_report.csv</i> enables automated CI parsing and spreadsheet sorting, whereas <i>test_results_report.html</i> renders a clean visual summary suitable for academic presentation and viva-voce demonstration.")
    pb()

    # ---------------- PAGE 15: CHAPTER 9 - CART ANALYSIS & CHALLENGES ----------------
    h1("CHAPTER 9: CART ANALYSIS, CHART & CHALLENGES")
    h2("9.1 Breakdown of 5 Auto-Searched Cart Items")
    cart_rows = [
        ["1", "milk", "Milky Mist Pro+ 25 g High Protein Milk - Pack of 3", "1 item", "₹234"],
        ["2", "bread", "Modern 100% Whole Wheat Bread (Zero Maida)", "2 items", "₹299"],
        ["3", "butter", "Akshayakalpa Organic Cooking Organic Butter", "3 items", "₹527"],
        ["4", "chips", "Bingo Masala Massacre Potato Chips", "4 items", "₹562"],
        ["5", "chocolate", "Celebrations Assorted Chocolate Gift Pack", "5 items", "₹962"],
    ]
    story.append(make_table(["#", "Query", "Matched Product Added to Cart", "Badge", "Subtotal"], cart_rows, [0.35 * inch, 0.85 * inch, 3.65 * inch, 0.9 * inch, 1.1 * inch], st))
    story.append(cart_progression_chart())
    h2("9.2 Technical Challenges & Engineering Solutions")
    b("<b>Headless Bot Protection:</b> Blinkit blocks headless Chrome with a Cloudflare challenge; running in visible ChromeDriver matches genuine desktop traffic cleanly without bypassing checks.")
    b("<b>React Controlled Input State:</b> Standard <i>.clear()</i> failed to reset Blinkit's search field; using <i>Cmd/Ctrl + A</i> + <i>Backspace</i> cleared state reliably before every query.")
    b("<b>Dynamic CSS-in-JS Hashes:</b> Partial class prefix selectors (<i>[class*='CartButton__Container']</i>) eliminated fragility from changing styled-component suffixes.")
    b("<b>SMS OTP Boundary & Card Parsing:</b> <i>TC_04</i> validates phone entry cleanly without OTP bypass, while regex filtering isolates product titles from delivery ETA and discount badges.")
    story.append(Spacer(1, 0.08 * inch))
    h2("9.3 Challenge Impact & Mitigation Matrix")
    story.append(make_table(
        ["Challenge Area", "Root Cause", "Implemented Engineering Fix"],
        [
            ["Headless Challenge", "Anti-bot gate on headless browser", "Standard visible Chrome WebDriver session"],
            ["Search Input Clear", "React state ignores .clear()", "Cmd/Ctrl+A + Backspace via clear_and_type()"],
            ["CSS Class Hashes", "Styled-components hash suffixes", "Partial [class*='...'] + semantic XPath"],
            ["Cart Title Parsing", "ETA/discount text inside cards", "Regex filtering in extract_product_title_from_card()"],
        ],
        [1.5 * inch, 2.35 * inch, 3.0 * inch],
        st,
        pad_v=4,
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(make_callout("<b>Cart Consistency Confirmed:</b> Subtotal progression from ₹234 to ₹962 plus ₹2 handling charge aligns cleanly with the asserted <b>₹964 Grand Total</b> inside Blinkit's <i>My Cart</i> drawer.", st))
    pb()

    # ---------------- PAGE 16: CHAPTER 10 - INTELLIJ GUIDE, CONCLUSION & REFS ----------------
    h1("CHAPTER 10: INTELLIJ GUIDE, CONCLUSION & REFERENCES")
    h2("10.1 Running the Project in IntelliJ IDEA (macOS)")
    cmds = """unzip "/Users/apple/Desktop/software testing/blinkit_automation_intellij.zip" -d ~/Desktop/
cd ~/Desktop/blinkit-ecommerce-automation && python3 -m pip install -r requirements.txt
python3 blinkit_automation.py
open -a "Google Chrome" test_results_report.html"""
    story.append(Preformatted(cmds, st["code"]))
    p("In IntelliJ IDEA on macOS, install the <b>Python</b> plugin (<i>Cmd + ,</i>), open the extracted folder, configure <i>/usr/local/bin/python3</i> as the SDK (<i>Cmd + ;</i>), and click Run on <b>blinkit_automation</b>.")
    h2("10.2 Deliverables Inventory")
    story.append(make_table(
        ["Artifact", "Purpose"],
        [
            ["blinkit_automation.py & test_data.json", "Core Selenium automation script and external JSON data feed"],
            ["test_results_report.csv & .html", "Automated execution logs and interactive HTML summary"],
            ["Blinkit_Automation_Testing_PPT.pptx", "12-slide presentation deck with live test metrics"],
            ["Blinkit_Automation_Project_Report.pdf", "MITM/VTU project report with adapted front pages & 13 figures"],
            ["blinkit_automation_intellij.zip", "Complete IntelliJ IDEA ready-to-import project archive"],
        ],
        [3.15 * inch, 3.7 * inch],
        st,
        pad_v=3.5,
    ))
    h2("10.3 Conclusion & Future Enhancements")
    p("This project at <b>MITM</b> successfully delivers a complete, data-driven Selenium automation suite for <b>Blinkit</b>. All inputs reside in <i>test_data.json</i>, 5 products are searched and added automatically, all 5 items are verified in <i>My Cart</i> (Grand total <i>₹964</i>), and <b>12/12 test cases pass</b>.")
    p("Future enhancements include automating cart <i>+ / -</i> quantity controls and item removal assertions, adding negative search datasets (unserviceable pincodes or out-of-stock queries), and integrating <i>pytest</i> with GitHub Actions CI/CD for cross-browser regression testing.")
    h2("10.4 Technical References")
    b("SeleniumHQ Official Documentation: <i>https://www.selenium.dev/documentation/</i>")
    b("Python 3.13 Standard Library Reference: <i>https://docs.python.org/3/</i>")
    b("Blinkit Web Storefront: <i>https://blinkit.com/</i>")
    b("JetBrains IntelliJ IDEA Python SDK Guide: <i>https://www.jetbrains.com/help/idea/configuring-python-sdk.html</i>")
    h2("10.5 Viva-Voce Quick Summary")
    story.append(make_table(
        ["Viva Question Topic", "Concise Technical Answer"],
        [
            ["Where are inputs stored?", "100% externally in test_data.json (zero hardcoding in Python)"],
            ["How are 5 items selected?", "Autonomous loop searches each JSON item, clicks ADD & asserts count"],
            ["How is cart verified?", "Clicks CartButton__Container, waits for Bill details & matches all 5 items"],
        ],
        [2.05 * inch, 4.8 * inch],
        st,
        pad_v=4,
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(make_callout("<b>End of Report — MITM / VTU Software Testing Project (2026–2027)</b> | Verified 12/12 Test Cases PASSED.", st, bg=SOFT_YELLOW, accent=YELLOW))

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    r = PdfReader(str(PDF_PATH))
    print(f"PDF generated: {PDF_PATH} -> {len(r.pages)} total pages ({PDF_PATH.stat().st_size} bytes)")
    for idx, page in enumerate(r.pages, 1):
        lines = [l.strip() for l in (page.extract_text() or "").splitlines() if l.strip()]
        preview = " | ".join(lines[:4])[:95]
        print(f"Physical P{idx:2d}: {preview}")
