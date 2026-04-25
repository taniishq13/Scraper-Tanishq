# scraper.py
# Drives the browser, handles pagination, and calls the parser.

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from config import (
    BASE_URL, PAGES_TO_SCRAPE, DELAY_BETWEEN_PAGES,
    DELAY_BETWEEN_DETAILS, PAGE_LOAD_TIMEOUT, HEADLESS
)
from parser import parse_listing_page, parse_detail_page
from utils import wait, log


def build_driver():
    """Set up Chrome with options that reduce the chance of getting blocked."""
    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    service = Service("/usr/local/bin/chromedriver")
    prefs = {
        "download.prompt_for_download": False,
        "download.default_directory": "/dev/null",
        "plugins.always_open_pdf_externally": False,
        "download_restrictions": 3
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=service, options=options)

    # Make automation harder to detect
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def wait_for_bids(driver, timeout=PAGE_LOAD_TIMEOUT):
    wait(3)  # let JS render first
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.block_header"))
    )

def go_to_next_page(driver):
    try:
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-link.next"))
        )
        print("BUTTON FOUND:", next_btn.get_attribute("outerHTML"))
        btn_class = next_btn.get_attribute("class") or ""
        if "disabled" in btn_class:
            log.info("Reached the last page")
            return False

        driver.execute_script("arguments[0].scrollIntoView();", next_btn)
        wait(1)
        driver.execute_script("arguments[0].click();", next_btn)
        wait(3)
        return True

    except Exception as e:
        print("NEXT BUTTON ERROR:", e)
        log.info("No Next button found — assuming last page")
        return False

    except Exception:
        log.info("No Next button found — assuming last page")
        return False


def fetch_detail(driver, url):
    """
    Open a tender's detail page and return its HTML.
    Returns None if the page fails to load.
    """
    if not url:
        return None
    try:
        driver.get(url)
        wait(DELAY_BETWEEN_DETAILS)
        return driver.page_source
    except Exception as e:
        log.warning(f"Could not load detail page {url}: {e}")
        return None


def run_scraper():
    log.info("Starting scraper...")
    driver = build_driver()
    all_tenders = []

    try:
        log.info(f"Opening {BASE_URL}")
        driver.get(BASE_URL)

        for page_num in range(1, PAGES_TO_SCRAPE + 1):
            log.info(f"--- Page {page_num} ---")

            try:
                wait_for_bids(driver)
            except TimeoutException:
                log.warning(f"Page {page_num} timed out. Skipping.")
                break

            current_page_url = driver.current_url

            page_html = driver.page_source
            tenders = parse_listing_page(page_html)

            for tender in tenders:
                if tender.get("detail_url"):
                    detail_html = fetch_detail(driver, tender["detail_url"])
                    if detail_html:
                        extra = parse_detail_page(detail_html, tender.get("bid_number", "?"))
                        tender.update(extra)
                    driver.get(current_page_url)
                    wait(2)

            all_tenders.extend(tenders)
            log.info(f"Total tenders collected so far: {len(all_tenders)}")

            if page_num < PAGES_TO_SCRAPE:
                moved = go_to_next_page(driver)
                if not moved:
                    break
                wait(DELAY_BETWEEN_PAGES)

    except Exception as e:
        log.error(f"Scraper crashed: {e}")

    finally:
        driver.quit()
        log.info("Browser closed.")

    log.info(f"Done. Total tenders scraped: {len(all_tenders)}")
    return all_tenders