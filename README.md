# GemEdge Data Scraping Assignment

Scraper for **GeM Portal** (`bidplus.gem.gov.in/all-bids`) — India's central government procurement marketplace.

## What it does

- Scrapes active government tender/bid listings across multiple pages
- Visits each tender's detail page for additional fields
- Outputs clean data in both CSV and JSON

## Fields extracted

| Field | Source |
|---|---|
| `bid_number` | Listing page |
| `title` | Listing page |
| `organization` | Listing page |
| `quantity` | Listing page |
| `start_date` | Listing page |
| `end_date` | Listing page |
| `category` | Listing page |
| `detail_url` | Listing page |
| `estimated_value` | Detail page |
| `location` | Detail page |
| `items_preview` | Detail page |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Output files will appear in the `output/` folder.

## Configuration

Edit `config.py` to change:
- `PAGES_TO_SCRAPE` — how many pages to go through (default: 5)
- `HEADLESS` — set to `False` to watch the browser run
- `DELAY_BETWEEN_PAGES` — seconds between page loads

## Tech stack

- `selenium` + `webdriver-manager` — browser automation for JS-rendered pages  
- `beautifulsoup4` + `lxml` — HTML parsing  
- `pandas` — CSV export  

## Notes

- Delays are built in between requests to avoid overloading the server  
- Missing fields are stored as `null` rather than crashing the scraper  
- Duplicate bids are removed before saving  
