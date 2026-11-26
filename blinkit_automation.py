"""
Automated E-Commerce Testing Script for Blinkit using Python & Selenium WebDriver.

All test inputs (URL, delivery location, mobile number, product search list,
timeouts, and report filenames) are loaded dynamically from `test_data.json`.
No test data is hardcoded in this script or entered manually at runtime.
"""

import csv
import html
import json
import re
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "test_data.json"


def load_test_data(file_path: Path) -> dict:
    """Load external test configuration and input data feeds from JSON."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_and_type(element, text: str) -> None:
    """Clear a React-controlled input reliably and enter text."""
    element.click()
    element.send_keys(Keys.COMMAND + "a")
    element.send_keys(Keys.CONTROL + "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(text)


def extract_cart_count(cart_text: str) -> int:
    """Parse item count from Blinkit cart button text (e.g., '3 items')."""
    match = re.search(r"(\d+)\s+item", cart_text, re.IGNORECASE)
    return int(match.group(1)) if match else 0


def extract_product_title_from_card(add_button) -> str:
    """Extract the product title from the nearest product card ancestor."""
    card = add_button.find_element(By.XPATH, "./ancestor::div[3]")
    lines = [line.strip() for line in card.text.splitlines() if line.strip()]
    skip_prefixes = ("ADD", "₹")
    for line in lines:
        if any(line.startswith(p) for p in skip_prefixes):
            continue
        if re.match(r"^\d+\s*MINS?$", line, re.IGNORECASE):
            continue
        if re.match(r"^\d+%\s*OFF$", line, re.IGNORECASE):
            continue
        return line
    return lines[0] if lines else "Unknown Product"


def write_reports(results: list, csv_path: Path, html_path: Path, project_name: str) -> None:
    """Write test execution results to CSV and HTML summary reports."""
    fieldnames = [
        "Test_Case_ID",
        "Scenario",
        "Input_Data",
        "Expected_Result",
        "Actual_Result",
        "Status",
        "Timestamp",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    passed = sum(1 for r in results if r["Status"] == "PASS")
    failed = sum(1 for r in results if r["Status"] == "FAIL")
    rows_html = "\n".join(
        f"<tr>"
        f"<td>{html.escape(r['Test_Case_ID'])}</td>"
        f"<td>{html.escape(r['Scenario'])}</td>"
        f"<td>{html.escape(r['Input_Data'])}</td>"
        f"<td>{html.escape(r['Expected_Result'])}</td>"
        f"<td>{html.escape(r['Actual_Result'])}</td>"
        f"<td class='status-{r['Status'].lower()}'>{html.escape(r['Status'])}</td>"
        f"<td>{html.escape(r['Timestamp'])}</td>"
        f"</tr>"
        for r in results
    )

    report_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{html.escape(project_name)} - Test Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 32px; background: #f8fafc; color: #0f172a; }}
    h1 {{ margin-bottom: 6px; }}
    .summary {{ display: flex; gap: 16px; margin: 20px 0; }}
    .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 20px; min-width: 140px; }}
    .card strong {{ display: block; font-size: 24px; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 14px; }}
    th {{ background: #0f172a; color: #fff; }}
    .status-pass {{ color: #15803d; font-weight: 700; }}
    .status-fail {{ color: #b91c1c; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>{html.escape(project_name)}</h1>
  <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Source: <code>test_data.json</code></p>
  <div class="summary">
    <div class="card">Total Tests<strong>{len(results)}</strong></div>
    <div class="card">Passed<strong style="color:#15803d">{passed}</strong></div>
    <div class="card">Failed<strong style="color:#b91c1c">{failed}</strong></div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Test Case ID</th>
        <th>Test Scenario</th>
        <th>Input Data</th>
        <th>Expected Result</th>
        <th>Actual Result</th>
        <th>Status</th>
        <th>Timestamp</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>
"""
    html_path.write_text(report_html, encoding="utf-8")


def run_automation() -> int:
    data = load_test_data(DATA_FILE)
    website_url = data["website_url"]
    expected_title = data["expected_title_keyword"]
    delivery_location = data["delivery_location"]
    mobile_no = data["user_credentials"]["mobile_no"]
    products = data["products"]
    wait_seconds = data["timeouts"]["explicit_wait_seconds"]
    pause_seconds = data["timeouts"]["step_pause_seconds"]
    csv_report = BASE_DIR / data["report_files"]["csv"]
    html_report = BASE_DIR / data["report_files"]["html"]

    results = []

    def record(tc_id: str, scenario: str, input_data: str, expected: str, actual: str, passed: bool) -> None:
        status = "PASS" if passed else "FAIL"
        results.append(
            {
                "Test_Case_ID": tc_id,
                "Scenario": scenario,
                "Input_Data": input_data,
                "Expected_Result": expected,
                "Actual_Result": actual,
                "Status": status,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        print(f"[{status}] {tc_id} - {scenario} | {actual}")

    driver = None
    added_products = []

    print("\n===== BLINKIT E-COMMERCE AUTOMATION TESTING STARTED =====")
    print(f"Loaded external data from: {DATA_FILE.name}")
    print(f"Target Website: {website_url} | Products to search & add: {products}\n")

    try:
        # TC_01: Launch Browser Session
        driver = webdriver.Chrome()
        driver.maximize_window()
        wait = WebDriverWait(driver, wait_seconds)
        assert driver.session_id is not None
        record(
            "TC_01",
            "Create Chrome WebDriver session",
            "Browser=Chrome (Maximized)",
            "Browser launches with an active WebDriver session",
            f"Session started (ID: {driver.session_id[:12]}...)",
            True,
        )
        time.sleep(pause_seconds)

        # TC_02: Navigate to Website
        driver.get(website_url)
        wait.until(lambda d: expected_title.lower() in d.title.lower())
        assert expected_title.lower() in driver.title.lower()
        record(
            "TC_02",
            "Navigate to Blinkit website",
            f"URL={website_url}",
            f"Page loads with '{expected_title}' in title",
            f"Loaded title: '{driver.title}'",
            True,
        )
        time.sleep(pause_seconds)

        # TC_03: Set Delivery Location from external data file
        location_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='select-locality']"))
        )
        location_input.send_keys(delivery_location)
        first_suggestion = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='LocationSearchList__LocationListContainer']"))
        )
        selected_loc_text = first_suggestion.text.replace("\n", ", ")
        first_suggestion.click()
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "input[name='select-locality']")))
        record(
            "TC_03",
            "Select delivery location",
            f"Location={delivery_location}",
            "Location suggestion appears, is selected, and modal closes",
            f"Selected location: '{selected_loc_text}'",
            True,
        )
        time.sleep(pause_seconds)

        # TC_04: Verify Login Modal & Mobile Number Input from external data file
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Login'] | //button[normalize-space()='Login']"))
        )
        login_btn.click()
        phone_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input.login-phone__input"))
        )
        phone_input.send_keys(mobile_no)
        entered_phone = phone_input.get_attribute("value")
        continue_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Continue')]"))
        )
        assert entered_phone == mobile_no and continue_btn.is_enabled()
        record(
            "TC_04",
            "Validate Login modal mobile number input",
            f"Mobile={mobile_no}",
            "10-digit mobile number accepted and Continue button enabled",
            f"Entered '{entered_phone}'; Continue enabled={continue_btn.is_enabled()}",
            True,
        )
        time.sleep(pause_seconds)

        # Reload home URL cleanly to dismiss login modal without submitting OTP
        driver.get(website_url)
        time.sleep(pause_seconds)

        # TC_05: Open Search Page
        search_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/s/']")))
        search_link.click()
        search_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[class*='SearchBarContainer__Input']"))
        )
        assert "/s/" in driver.current_url and search_input.is_displayed()
        record(
            "TC_05",
            "Navigate to product search bar",
            "Click Search Bar",
            "Search page (/s/) opens with active search input",
            f"Opened '{driver.current_url}'",
            True,
        )
        time.sleep(pause_seconds)

        # TC_06 - TC_10: Search each of the 5 products from external file and add to cart
        for idx, query in enumerate(products, start=1):
            tc_id = f"TC_{5 + idx:02d}"
            search_input = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input[class*='SearchBarContainer__Input']"))
            )
            clear_and_type(search_input, query)

            # Wait until results header reflects the searched keyword
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{query.lower()}')]",
                    )
                )
            )
            time.sleep(1.5)

            add_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "(//*[normalize-space(text())='ADD'])[1]"))
            )
            product_title = extract_product_title_from_card(add_btn)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_btn)
            add_btn.click()

            # Wait until cart badge increments to expected count
            expected_count = idx
            wait.until(
                lambda d: extract_cart_count(
                    d.find_element(By.CSS_SELECTOR, "[class*='CartButton__Container']").text
                )
                >= expected_count
            )
            cart_text = driver.find_element(By.CSS_SELECTOR, "[class*='CartButton__Container']").text.replace("\n", " | ")
            actual_count = extract_cart_count(cart_text)
            assert actual_count == expected_count, f"Expected {expected_count} items, got {actual_count}"
            added_products.append(product_title)

            record(
                tc_id,
                f"Search '{query}' and add item to cart",
                f"Search='{query}'",
                f"Product found and added; cart count becomes {expected_count}",
                f"Added '{product_title}' | Cart badge: '{cart_text}'",
                True,
            )
            time.sleep(pause_seconds)

        # TC_11: Enter / Open Cart to View All Selected Items
        cart_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[class*='CartButton__Container']"))
        )
        cart_button.click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[normalize-space()='My Cart']")))
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Bill details')]")))
        time.sleep(1.5)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        matched_items = [name for name in added_products if name.lower() in body_text.lower()]
        assert len(matched_items) == len(products), (
            f"Expected {len(products)} items in cart view, matched {len(matched_items)}: {matched_items}"
        )

        # Extract bill grand total if visible
        total_match = re.search(r"Grand total\s*\n?\s*(₹\s*[\d,]+)", body_text, re.IGNORECASE)
        grand_total = total_match.group(1).replace("\n", " ") if total_match else "Displayed"

        record(
            "TC_11",
            "Open shopping cart and verify all 5 added items",
            f"Expected items={len(products)}",
            "Cart drawer displays My Cart, Bill details, and all 5 added items",
            f"Verified {len(matched_items)}/{len(products)} items in cart ({grand_total}): {', '.join(matched_items)}",
            True,
        )
        time.sleep(pause_seconds * 2)

    except AssertionError as err:
        record(
            f"TC_{len(results) + 1:02d}",
            "Assertion failure",
            "-",
            "Assertion succeeds",
            f"AssertionError: {err}",
            False,
        )
    except TimeoutException as err:
        record(
            f"TC_{len(results) + 1:02d}",
            "Element wait timeout",
            "-",
            "Element becomes visible/clickable within timeout",
            f"TimeoutException: {err}",
            False,
        )
    except Exception as err:
        record(
            f"TC_{len(results) + 1:02d}",
            "Unexpected automation error",
            "-",
            "Execution completes cleanly",
            f"{type(err).__name__}: {err}",
            False,
        )
    finally:
        # TC_12: End WebDriver Session
        if driver is not None:
            driver.quit()
            record(
                "TC_12",
                "Close browser and end WebDriver session",
                "driver.quit()",
                "Browser closes and session terminates cleanly",
                "WebDriver session closed successfully",
                True,
            )

        write_reports(results, csv_report, html_report, data["project_name"])
        passed_count = sum(1 for r in results if r["Status"] == "PASS")
        failed_count = sum(1 for r in results if r["Status"] == "FAIL")
        print(f"\n===== SUMMARY: {passed_count}/{len(results)} PASSED, {failed_count} FAILED =====")
        print(f"CSV Report : {csv_report}")
        print(f"HTML Report: {html_report}")
        print("===== AUTOMATION TESTING ENDED =====\n")

    return 0 if all(r["Status"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(run_automation())
