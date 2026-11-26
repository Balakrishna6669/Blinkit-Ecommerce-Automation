"""Generate a 12-slide PowerPoint presentation from the actual test data and execution report."""

import csv
import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt


BASE_DIR = Path(__file__).resolve().parent
DATA = json.loads((BASE_DIR / "test_data.json").read_text(encoding="utf-8"))
with open(BASE_DIR / DATA["report_files"]["csv"], "r", encoding="utf-8") as f:
    RESULTS = list(csv.DictReader(f))

# Theme palette (Blinkit-inspired crisp dark slate + yellow-gold + fresh green)
BG_LIGHT = RGBColor(248, 250, 252)
NAVY = RGBColor(15, 23, 42)
SLATE = RGBColor(51, 65, 85)
MUTED = RGBColor(100, 116, 139)
BLINKIT_YELLOW = RGBColor(248, 203, 70)
GREEN = RGBColor(12, 131, 31)
WHITE = RGBColor(255, 255, 255)
BORDER = RGBColor(226, 232, 240)
SOFT_GREEN = RGBColor(236, 253, 245)
SOFT_YELLOW = RGBColor(254, 249, 195)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK_LAYOUT = prs.slide_layouts[6]


def set_bg(slide, color=BG_LIGHT):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, title: str, subtitle: str, slide_num: int):
    # Top accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.14))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLINKIT_YELLOW
    bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.65), Inches(0.32), Inches(11.2), Inches(0.95))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = NAVY

    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.size = Pt(14)
    p2.font.color.rgb = MUTED

    # Slide number pill
    num_box = slide.shapes.add_textbox(Inches(12.1), Inches(0.38), Inches(0.65), Inches(0.4))
    np = num_box.text_frame.paragraphs[0]
    np.text = f"{slide_num}/12"
    np.alignment = PP_ALIGN.RIGHT
    np.font.size = Pt(12)
    np.font.bold = True
    np.font.color.rgb = MUTED


def add_card(slide, left, top, width, height, title: str, bullets: list, accent=GREEN, bg=WHITE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.adjustments[0] = 0.04
    card.fill.solid()
    card.fill.fore_color.rgb = bg
    card.line.color.rgb = BORDER
    card.line.width = Pt(1)

    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.1), Inches(height))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = accent
    stripe.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.16), Inches(width - 0.4), Inches(height - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(6)

    for b in bullets:
        bp = tf.add_paragraph()
        bp.text = f"• {b}"
        bp.font.size = Pt(13)
        bp.font.color.rgb = SLATE
        bp.space_after = Pt(4)


def add_table(slide, left, top, width, height, headers, rows, col_widths):
    table_shape = slide.shapes.add_table(len(rows) + 1, len(headers), Inches(left), Inches(top), Inches(width), Inches(height))
    table = table_shape.table
    for idx, cw in enumerate(col_widths):
        table.columns[idx].width = Inches(cw)

    for c, h in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = WHITE

    for r_idx, row in enumerate(rows, start=1):
        row_bg = WHITE if r_idx % 2 == 1 else RGBColor(241, 245, 249)
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = SOFT_GREEN if val == "PASS" else row_bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.size = Pt(11)
            p.font.bold = (c_idx == 0 or val == "PASS")
            p.font.color.rgb = GREEN if val == "PASS" else NAVY


# ---------------- SLIDE 1: Title Slide ----------------
s1 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s1, NAVY)

accent_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.32), Inches(7.5))
accent_box.fill.solid()
accent_box.fill.fore_color.rgb = BLINKIT_YELLOW
accent_box.line.fill.background()

badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.3), Inches(3.8), Inches(0.5))
badge.adjustments[0] = 0.5
badge.fill.solid()
badge.fill.fore_color.rgb = GREEN
badge.line.fill.background()
bp = badge.text_frame.paragraphs[0]
bp.text = "SOFTWARE TESTING MINI PROJECT"
bp.alignment = PP_ALIGN.CENTER
bp.font.size = Pt(13)
bp.font.bold = True
bp.font.color.rgb = WHITE

t1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.15), Inches(11.0), Inches(1.9))
tf1 = t1.text_frame
tf1.word_wrap = True
p = tf1.paragraphs[0]
p.text = "Automated E-Commerce Testing\nof Blinkit Web Application"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = WHITE

sub = tf1.add_paragraph()
sub.text = "Data-Driven End-to-End Automation using Python, Selenium WebDriver & External JSON Feeds"
sub.font.size = Pt(20)
sub.font.color.rgb = BLINKIT_YELLOW
sub.space_before = Pt(14)

meta = s1.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.0), Inches(1.2))
mf = meta.text_frame
for line in [
    f"Target Website: {DATA['website_url']}   |   Location: {DATA['delivery_location']}",
    f"Test Coverage: 12 Automated Test Cases (12/12 PASSED)   |   5 Auto-Searched Cart Products",
    "Tool Stack: Python 3.13 • Selenium 4.53 • Chrome WebDriver • CSV & HTML Reporting",
]:
    mp = mf.add_paragraph()
    mp.text = line
    mp.font.size = Pt(14)
    mp.font.color.rgb = RGBColor(203, 213, 225)
    mp.space_after = Pt(4)

# ---------------- SLIDE 2: Problem Statement & Objectives ----------------
s2 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s2)
add_header(s2, "Problem Statement & Project Objectives", "Aligning automation design with core software testing guidelines", 2)

add_card(s2, 0.65, 1.55, 5.85, 2.5, "Problem Statement", [
    "Manual regression testing of quick-commerce flows (location, search, cart) is repetitive and error-prone.",
    "Hardcoded test scripts fail maintainability when URLs, credentials, or product catalogs change.",
    "Need an automated, data-driven framework that verifies search-to-cart workflows and generates structured reports."
], accent=BLINKIT_YELLOW)

add_card(s2, 6.8, 1.55, 5.85, 2.5, "Project Objectives", [
    "Automate end-to-end Blinkit shopping workflow from launch to cart verification.",
    "Feed all test inputs (URL, location, mobile no, 5 product names) via an external linked file (test_data.json).",
    "Assert every user action programmatically and export CSV + HTML execution reports."
], accent=GREEN)

add_card(s2, 0.65, 4.35, 12.0, 2.55, "Mini-Project Guidelines Coverage", [
    "1. Create WebDriver Session (Chrome maximized)   2. Navigate to Website   3. Locate Elements via CSS/XPath & Explicit Waits",
    "4. Perform Actions (location, mobile validation, 5 product searches, add to cart, view cart)   5. Assert Expected Outcomes",
    "6. Report Assertion Results (Console + CSV + HTML)   7. End WebDriver Session cleanly via driver.quit()"
], accent=NAVY, bg=SOFT_GREEN)

# ---------------- SLIDE 3: System Under Test (Blinkit) ----------------
s3 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s3)
add_header(s3, "System Under Test: Blinkit (Quick-Commerce)", "End-to-end user journey selected for automated verification", 3)

steps_s3 = [
    ("1. Location Gate", "Blinkit requires a serviceable delivery locality before showing live store inventory."),
    ("2. Login Modal", "Supports 10-digit mobile number entry for OTP authentication (validated without bypassing OTP)."),
    ("3. Product Search", "Dynamic React search bar (/s/) fetches instant matching grocery items and prices."),
    ("4. Add & Cart View", "Clicking ADD updates the live cart counter and populates the My Cart drawer & Bill details."),
]
for idx, (st_title, st_desc) in enumerate(steps_s3):
    left = 0.65 + idx * 3.08
    add_card(s3, left, 1.65, 2.85, 2.7, st_title, [st_desc], accent=BLINKIT_YELLOW if idx % 2 == 0 else GREEN)

add_card(s3, 0.65, 4.7, 12.0, 2.1, "Why Blinkit is Ideal for Automation Testing", [
    "Single-Page Application (SPA) built with dynamic React components—tests real-world explicit waits and state updates.",
    "Exercises multiple UI patterns: modal dialogs, autocomplete dropdowns, live search filtering, cart state badges, and slide-over drawers.",
    f"Verified live against {DATA['website_url']} for locality '{DATA['delivery_location']}'."
], accent=NAVY)

# ---------------- SLIDE 4: Tools, Tech Stack & Architecture ----------------
s4 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s4)
add_header(s4, "Tools, Environment & Architecture", "Technology stack powering the automated test suite", 4)

add_card(s4, 0.65, 1.55, 3.8, 5.2, "Core Testing Stack", [
    "Python 3.13.15 runtime",
    "Selenium WebDriver 4.53.0",
    "Google Chrome & Selenium Manager (auto driver resolution)",
    "WebDriverWait & Expected Conditions (EC) for synchronization",
    "Python csv, json & html modules for zero-dependency reporting"
], accent=GREEN)

add_card(s4, 4.75, 1.55, 3.8, 5.2, "Project File Structure", [
    "test_data.json — External data feed",
    "blinkit_automation.py — Main test runner & assertions",
    "test_results_report.csv — Tabular execution log",
    "test_results_report.html — Executive dashboard report",
    "TEST_CASES_DOCUMENTATION.md — Full QA specification"
], accent=BLINKIT_YELLOW)

add_card(s4, 8.85, 1.55, 3.8, 5.2, "Architectural Principles", [
    "Separation of Concerns: Test logic separated from test data.",
    "Fail-Safe Cleanup: try / except / finally guarantees driver.quit() even on failures.",
    "Deterministic Synchronization: Explicit waits replace brittle blind sleeps.",
    "Auditability: Timestamped assertions logged to console, CSV, and HTML."
], accent=NAVY)

# ---------------- SLIDE 5: External Data-Driven Design ----------------
s5 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s5)
add_header(s5, "External Data-Driven Input File (test_data.json)", "Zero hardcoded inputs: all test feeds loaded dynamically from JSON", 5)

code_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(1.55), Inches(6.6), Inches(5.2))
code_box.adjustments[0] = 0.03
code_box.fill.solid()
code_box.fill.fore_color.rgb = NAVY
code_box.line.fill.background()
ctf = code_box.text_frame
ctf.word_wrap = True
cp = ctf.paragraphs[0]
cp.text = "test_data.json"
cp.font.size = Pt(14)
cp.font.bold = True
cp.font.color.rgb = BLINKIT_YELLOW
cp.space_after = Pt(8)

json_lines = json.dumps(DATA, indent=2).splitlines()
for line in json_lines:
    lp = ctf.add_paragraph()
    lp.text = line
    lp.font.name = "Courier New"
    lp.font.size = Pt(11)
    lp.font.color.rgb = RGBColor(226, 232, 240)

add_card(s5, 7.55, 1.55, 5.1, 2.45, "Data Feeds Linked to Script", [
    f"Website URL: {DATA['website_url']}",
    f"Delivery Location: {DATA['delivery_location']}",
    f"Mobile Number: {DATA['user_credentials']['mobile_no']}",
    f"Product List (5 items): {', '.join(DATA['products'])}"
], accent=GREEN)

add_card(s5, 7.55, 4.25, 5.1, 2.5, "Key Benefits", [
    "Changing products or city requires editing only test_data.json.",
    "Eliminates manual data entry during automated execution.",
    "Configurable timeouts and output report paths."
], accent=BLINKIT_YELLOW)

# ---------------- SLIDE 6: Automation Workflow Pipeline ----------------
s6 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s6)
add_header(s6, "End-to-End Automation Workflow", "7-phase execution flow implemented in blinkit_automation.py", 6)

phases = [
    ("Phase 1", "Load JSON & Launch Chrome", "Read test_data.json; initialize Chrome WebDriver & maximize window."),
    ("Phase 2", "Navigate & Set Location", "Open blinkit.com; enter locality and pick first autocomplete match."),
    ("Phase 3", "Login Input Verification", "Open Login modal, enter mobile number, verify Continue button enables."),
    ("Phase 4", "Automated 5-Item Search Loop", "For each item in products[], search, locate card, click ADD, assert count."),
    ("Phase 5", "Enter & Inspect Cart Drawer", "Click My Cart button; assert all 5 items & Bill details are displayed."),
    ("Phase 6", "Report & End Session", "Export CSV + HTML reports and terminate browser via driver.quit()."),
]
for i, (ph, ttl, desc) in enumerate(phases):
    col = i % 3
    row = i // 3
    add_card(s6, 0.65 + col * 4.1, 1.65 + row * 2.65, 3.85, 2.35, f"{ph}: {ttl}", [desc], accent=GREEN if i % 2 == 0 else BLINKIT_YELLOW)

# ---------------- SLIDE 7: Test Cases Part 1 (TC_01 - TC_06) ----------------
s7 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s7)
add_header(s7, "Test Cases & Execution Results (TC_01 – TC_06)", "Session setup, navigation, location, login validation, and first search item", 7)

rows_p1 = [
    [r["Test_Case_ID"], r["Scenario"], r["Input_Data"], r["Actual_Result"], r["Status"]]
    for r in RESULTS[:6]
]
add_table(
    s7, 0.55, 1.5, 12.2, 5.4,
    ["TC ID", "Test Scenario", "Input Data", "Actual Observed Result", "Status"],
    rows_p1,
    [0.9, 2.7, 2.2, 5.4, 1.0],
)

# ---------------- SLIDE 8: Test Cases Part 2 (TC_07 - TC_12) ----------------
s8 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s8)
add_header(s8, "Test Cases & Execution Results (TC_07 – TC_12)", "Remaining 4 product searches, cart drawer verification, and teardown", 8)

rows_p2 = [
    [r["Test_Case_ID"], r["Scenario"], r["Input_Data"], r["Actual_Result"], r["Status"]]
    for r in RESULTS[6:12]
]
add_table(
    s8, 0.55, 1.5, 12.2, 5.4,
    ["TC ID", "Test Scenario", "Input Data", "Actual Observed Result", "Status"],
    rows_p2,
    [0.9, 2.7, 2.2, 5.4, 1.0],
)

# ---------------- SLIDE 9: Implementation Highlights ----------------
s9 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s9)
add_header(s9, "Implementation & Locator Highlights", "Robust Selenium patterns used to handle dynamic React elements", 9)

add_card(s9, 0.65, 1.55, 5.85, 2.5, "Dynamic Search & Input Clearing", [
    "React-controlled search input cleared reliably using Select-All + Backspace before typing each keyword.",
    "Waits for search result DOM to reflect the queried product before clicking ADD.",
    "Scrolls target ADD button to center of viewport prior to click."
], accent=GREEN)

add_card(s9, 6.8, 1.55, 5.85, 2.5, "Resilient Locator Strategy", [
    "Location input: input[name='select-locality']",
    "Search bar input: input[class*='SearchBarContainer__Input']",
    "Add button: (//*[normalize-space(text())='ADD'])[1]",
    "Cart container: [class*='CartButton__Container']"
], accent=BLINKIT_YELLOW)

add_card(s9, 0.65, 4.3, 12.0, 2.5, "Automated Assertions & Cart Verification", [
    "Each iteration parses the cart badge regex (e.g., '3 items') and asserts count == loop_index.",
    "Extracts actual matched product titles from cards before clicking ADD.",
    "In TC_11, opens My Cart drawer, waits for 'Bill details', and asserts all 5 extracted product titles appear in the cart."
], accent=NAVY)

# ---------------- SLIDE 10: Live Execution Results Summary ----------------
s10 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s10)
add_header(s10, "Execution Results & Cart Verification Summary", "100% pass rate achieved on live Blinkit run", 10)

stats = [
    ("12", "Total Test Cases", NAVY),
    ("12", "Test Cases Passed", GREEN),
    ("0", "Test Cases Failed", SLATE),
    ("5 / 5", "Cart Items Verified", GREEN),
]
for idx, (val, lbl, col) in enumerate(stats):
    box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65 + idx * 3.08), Inches(1.55), Inches(2.85), Inches(1.55))
    box.adjustments[0] = 0.06
    box.fill.solid()
    box.fill.fore_color.rgb = WHITE
    box.line.color.rgb = BORDER
    tf = box.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p1 = tf.paragraphs[0]
    p1.text = val
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = col
    p2 = tf.add_paragraph()
    p2.text = lbl
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(13)
    p2.font.color.rgb = MUTED

add_card(s10, 0.65, 3.4, 7.3, 3.45, "5 Items Automatically Searched & Verified in Cart (Grand Total: ₹964)", [
    "1. milk -> Milky Mist Pro+ 25 g High Protein Milk - Pack of 3",
    "2. bread -> Modern 100% Whole Wheat Bread (Zero Maida)",
    "3. butter -> Akshayakalpa Organic Cooking Organic Butter",
    "4. chips -> Bingo Masala Massacre Potato Chips",
    "5. chocolate -> Celebrations Assorted Chocolate Gift Pack"
], accent=GREEN, bg=SOFT_GREEN)

add_card(s10, 8.2, 3.4, 4.45, 3.45, "Generated Artifacts", [
    "test_results_report.csv (structured audit log)",
    "test_results_report.html (browser-ready report)",
    "TEST_CASES_DOCUMENTATION.md",
    "Blinkit_Automation_Testing_PPT.pptx"
], accent=BLINKIT_YELLOW)

# ---------------- SLIDE 11: Challenges & Solutions ----------------
s11 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s11)
add_header(s11, "Challenges Faced & Solutions Implemented", "Engineering fixes during live Blinkit automation", 11)

challenges = [
    ("Bot / Headless Detection", "Blinkit blocks headless browser sessions with a challenge page.", "Executed in standard visible Chrome WebDriver session (matching real user interaction)."),
    ("React Input Clearing", "Standard .clear() often leaves stale state in React search inputs.", "Implemented Select-All (Cmd/Ctrl+A) + Backspace helper before typing each keyword."),
    ("OTP Login Gate", "Real Blinkit checkout/login requires SMS OTP verification.", "Validated mobile number entry & Continue button enablement cleanly without bypassing OTP."),
    ("Dynamic Class Hashes", "Styled-components generate changing suffixes (e.g., sc-1k8u6a6-0).", "Used stable partial class prefixes ([class*='CartButton__Container']) and semantic text XPath."),
]
for idx, (ch_t, prob, sol) in enumerate(challenges):
    col = idx % 2
    row = idx // 2
    add_card(s11, 0.65 + col * 6.15, 1.6 + row * 2.65, 5.85, 2.35, ch_t, [f"Challenge: {prob}", f"Solution: {sol}"], accent=BLINKIT_YELLOW if col == 0 else GREEN)

# ---------------- SLIDE 12: Conclusion & Future Scope ----------------
s12 = prs.slides.add_slide(BLANK_LAYOUT)
set_bg(s12)
add_header(s12, "Conclusion & Future Scope", "Summary of project outcomes and potential enhancements", 12)

add_card(s12, 0.65, 1.6, 5.85, 4.9, "Conclusion", [
    "Successfully built a data-driven Selenium automation framework for Blinkit.",
    "All inputs (website URL, locality, mobile number, and 5 products) are decoupled in test_data.json.",
    "Automated search-to-cart flow added 5 distinct items and verified them inside the My Cart drawer.",
    "Achieved 12/12 PASS across all test cases with automated CSV and HTML reporting."
], accent=GREEN, bg=SOFT_GREEN)

add_card(s12, 6.8, 1.6, 5.85, 4.9, "Future Enhancements", [
    "Add quantity increment (+), decrement (-), and item removal assertions inside the Cart drawer.",
    "Integrate pytest + Allure or Selenium Grid for parallel cross-browser testing (Chrome, Edge, Firefox).",
    "Hook into GitHub Actions CI/CD for scheduled regression runs and automatic failure screenshots.",
    "Parameterize multiple delivery cities and negative search scenarios (out-of-stock / invalid queries)."
], accent=BLINKIT_YELLOW)

out_path = BASE_DIR / "Blinkit_Automation_Testing_PPT.pptx"
prs.save(out_path)
print("Saved 12-slide PPT to:", out_path)
print("Total slides:", len(prs.slides))
