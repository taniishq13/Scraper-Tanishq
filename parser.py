# parser.py
# HTML parsing using the exact class names from bidplus.gem.gov.in/all-bids

from bs4 import BeautifulSoup
from utils import clean, log


def parse_listing_page(html):
    """
    Pull all bid cards from one listing page.
    Each card starts with div.block_header on the live site.
    """
    soup = BeautifulSoup(html, "lxml")
    tenders = []

    # Each bid is wrapped in a parent div containing div.block_header + div.card-body
    cards = soup.select("div.block_header")

    if not cards:
        log.warning("No cards found on this page — selectors may have changed")
        return tenders

    for header in cards:
        card = header.parent  # full card = parent of block_header
        tender = extract_card_fields(header, card)
        if tender:
            tenders.append(tender)

    log.info(f"  Parsed {len(tenders)} tenders from this page")
    return tenders


def extract_card_fields(header, card):
    """
    Extract all fields from one bid card.
    header = div.block_header  (top part: bid number)
    card   = parent div        (contains header + card-body with all other fields)
    """
    tender = {}

    # Bid number + detail URL
    try:
        bid_link = header.select_one("a.bid_no_hover")
        if bid_link:
            tender["bid_number"] = clean(bid_link.get_text())
            href = bid_link.get("href", "")
            tender["detail_url"] = (
                "https://bidplus.gem.gov.in" + href
                if href.startswith("/")
                else href
            )
        else:
            tender["bid_number"] = None
            tender["detail_url"] = None
    except Exception:
        tender["bid_number"] = None
        tender["detail_url"] = None

    # Item name — full name is in data-content, visible text is truncated
    try:
        item_el = card.select_one("a[data-toggle='popover']")
        if item_el:
            tender["item_name"] = clean(
                item_el.get("data-content") or item_el.get_text()
            )
        else:
            tender["item_name"] = None
    except Exception:
        tender["item_name"] = None

    # Quantity
    try:
        tender["quantity"] = None
        for row in card.select("div.row"):
            strong = row.find("strong")
            if strong and "Quantity" in strong.get_text():
                parts = list(row.stripped_strings)
                tender["quantity"] = clean(parts[-1]) if len(parts) > 1 else None
                break
    except Exception:
        tender["quantity"] = None

    # Organization / Department name
    try:
        tender["organization"] = None
        for row in card.select("div.row"):
            strong = row.find("strong")
            if strong and "Department" in strong.get_text():
                parts = [t for t in row.stripped_strings if t != strong.get_text().strip()]
                tender["organization"] = clean(" ".join(parts))
                break
    except Exception:
        tender["organization"] = None

    # Start date
    try:
        start_el = card.select_one("span.start_date")
        tender["start_date"] = clean(start_el.get_text()) if start_el else None
    except Exception:
        tender["start_date"] = None

    # End date
    try:
        end_el = card.select_one("span.end_date")
        tender["end_date"] = clean(end_el.get_text()) if end_el else None
    except Exception:
        tender["end_date"] = None

    # Skip cards with no useful data (layout divs etc.)
    if not any([tender.get("bid_number"), tender.get("item_name")]):
        return None

    return tender


def parse_detail_page(html, bid_number):
    """
    Pull extra fields from a tender's detail page.
    """
    soup = BeautifulSoup(html, "lxml")
    extra = {}

    # Estimated / bid value
    try:
        for row in soup.select("div.row, tr"):
            text = row.get_text()
            if "Estimated Value" in text or "Bid Value" in text:
                parts = list(row.stripped_strings)
                if len(parts) >= 2:
                    extra["estimated_value"] = clean(parts[-1])
                break
    except Exception:
        pass

    # Consignee state / delivery location
    try:
        for row in soup.select("div.row, tr"):
            text = row.get_text()
            if "Consignee State" in text or "Delivery State" in text:
                parts = list(row.stripped_strings)
                if len(parts) >= 2:
                    extra["location"] = clean(parts[-1])
                break
    except Exception:
        pass

    log.info(f"    Detail fetched for {bid_number}")
    return extra
