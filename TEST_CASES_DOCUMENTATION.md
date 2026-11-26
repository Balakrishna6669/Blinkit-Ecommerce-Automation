# Mini Project Documentation: Automated Testing of Blinkit E-Commerce Website

## 1. Project Overview
This mini project demonstrates **Data-Driven End-to-End Automation Testing** of the **Blinkit** e-commerce web application (`https://blinkit.com/`) using **Python** and **Selenium WebDriver**.

All test inputs—including the target website URL, expected title keyword, delivery location, mobile number, list of 5 products to search, timeouts, and report filenames—are stored externally in [`test_data.json`](file:///Users/apple/Desktop/software%20testing/test_data.json) and loaded dynamically at runtime by [`blinkit_automation.py`](file:///Users/apple/Desktop/software%20testing/blinkit_automation.py).

## 2. Guidelines Covered
- **Create a WebDriver session**: Launches Google Chrome via `webdriver.Chrome()` and maximizes the browser window.
- **Navigate to a Web page**: Navigates to `website_url` read from `test_data.json`.
- **Locate web elements**: Uses `By.CSS_SELECTOR`, `By.XPATH`, `By.TAG_NAME`, and `WebDriverWait` + `expected_conditions`.
- **Perform actions on located elements**: Enters delivery location, validates login modal phone field, searches 5 products sequentially, clicks `ADD` on each item, and opens the `My Cart` drawer.
- **Assert performed actions**: Validates page title, phone number acceptance & button state, search URL & results, progressive cart count (`1` through `5`), and presence of all 5 added items in the Cart drawer.
- **Report assertion results**: Prints real-time `PASS`/`FAIL` logs to console and generates [`test_results_report.csv`](file:///Users/apple/Desktop/software%20testing/test_results_report.csv) and [`test_results_report.html`](file:///Users/apple/Desktop/software%20testing/test_results_report.html).
- **End the session**: Safely terminates the browser session via `driver.quit()` in a `finally` block.
- **External data-driven input**: Zero hardcoded inputs in code; all values come from `test_data.json`.

## 3. Environment & Project Files
- **Language**: Python 3.13.15
- **Automation Tool**: Selenium 4.53.0 (Chrome WebDriver)
- **Files in Workspace**:
  - `test_data.json` — External input data feed (URL, location, mobile number, 5 product keywords, timeouts, output paths)
  - `blinkit_automation.py` — Main Selenium automation script
  - `test_results_report.csv` — Machine-readable test execution results
  - `test_results_report.html` — Styled HTML execution summary report
  - `Blinkit_Automation_Testing_PPT.pptx` — 12-slide presentation deck
  - `TEST_CASES_DOCUMENTATION.md` — This test case & result documentation

## 4. Test Case Matrix & Execution Results
**Execution Summary**: **12 / 12 Test Cases PASSED (0 Failed)**

| TC ID | Test Scenario | Input Data (`test_data.json`) | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **TC_01** | Create Chrome WebDriver session | `Browser=Chrome (Maximized)` | Browser launches with active session | Session started cleanly (`driver.session_id` verified) | **PASS** |
| **TC_02** | Navigate to Blinkit website | `URL=https://blinkit.com/` | Page loads with `Blinkit` in title | Loaded title: `30,000+ products delivered to your doorstep | Blinkit` | **PASS** |
| **TC_03** | Select delivery location | `Location=Indiranagar, Bengaluru` | Location suggestion appears, is selected, and modal closes | Selected location: `Indiranagar, Bengaluru, Karnataka, India` | **PASS** |
| **TC_04** | Validate Login modal mobile number input | `Mobile=9876543210` | 10-digit mobile number accepted and Continue button enabled | Entered `9876543210`; Continue enabled=`True` | **PASS** |
| **TC_05** | Navigate to product search bar | `Click Search Bar` | Search page (`/s/`) opens with active search input | Opened `https://blinkit.com/s/` | **PASS** |
| **TC_06** | Search `'milk'` and add item to cart | `Search='milk'` | Product found and added; cart count becomes `1` | Added `Milky Mist Pro+ 25 g High Protein Milk - Pack of 3` (Cart: `1 item | ₹234`) | **PASS** |
| **TC_07** | Search `'bread'` and add item to cart | `Search='bread'` | Product found and added; cart count becomes `2` | Added `Modern 100% Whole Wheat Bread (Zero Maida)` (Cart: `2 items | ₹299`) | **PASS** |
| **TC_08** | Search `'butter'` and add item to cart | `Search='butter'` | Product found and added; cart count becomes `3` | Added `Akshayakalpa Organic Cooking Organic Butter` (Cart: `3 items | ₹527`) | **PASS** |
| **TC_09** | Search `'chips'` and add item to cart | `Search='chips'` | Product found and added; cart count becomes `4` | Added `Bingo Masala Massacre Potato Chips` (Cart: `4 items | ₹562`) | **PASS** |
| **TC_10** | Search `'chocolate'` and add item to cart | `Search='chocolate'` | Product found and added; cart count becomes `5` | Added `Celebrations Assorted Chocolate Gift Pack` (Cart: `5 items | ₹962`) | **PASS** |
| **TC_11** | Open shopping cart and verify all 5 added items | `Expected items=5` | Cart drawer displays `My Cart`, `Bill details`, and all 5 items | Verified `5/5` items in cart (`₹964` grand total) | **PASS** |
| **TC_12** | Close browser and end WebDriver session | `driver.quit()` | Browser closes and session terminates cleanly | WebDriver session closed successfully | **PASS** |

## 5. How to Run
```bash
pip install selenium
python3 blinkit_automation.py
```
To test different products, locations, or mobile numbers, edit `test_data.json` directly—no code changes required.
