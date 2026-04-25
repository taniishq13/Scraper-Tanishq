# config.py
# All settings live here. Change PAGES_TO_SCRAPE to scrape more data.

BASE_URL = "https://bidplus.gem.gov.in/all-bids"
DETAIL_BASE_URL = "https://bidplus.gem.gov.in/bidding/bid/showBidDocument"

PAGES_TO_SCRAPE = 5       # how many listing pages to go through
DELAY_BETWEEN_PAGES = 3   # seconds to wait between pages (be respectful)
DELAY_BETWEEN_DETAILS = 2 # seconds to wait between detail page visits
PAGE_LOAD_TIMEOUT = 20    # max seconds to wait for a page to load

OUTPUT_DIR = "output"
CSV_FILE = "output/tenders.csv"
JSON_FILE = "output/tenders.json"

# Chrome runs headless (no browser window opens). Set to False to watch it run.
HEADLESS = True
