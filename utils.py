import time
import os
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


def wait(seconds):
    """Pause between requests so we don't hammer the server."""
    time.sleep(seconds)


def clean(text):
    """Strip whitespace and return None if empty."""
    if text is None:
        return None
    cleaned = " ".join(text.split())
    return cleaned if cleaned else None


def ensure_output_dir(path):
    """Create the output folder if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def normalize_date(text):
    """Standardize date format."""
    if not text:
        return "N/A"
    return clean(text)

def normalize_currency(text):
    """Strip symbols, keep the number."""
    if not text:
        return "N/A"
    cleaned = re.sub(r'[₹$,\s]', '', str(text))
    return cleaned if cleaned else "N/A"

def fill_missing(value):
    """Replace None with N/A."""
    return value if value else "N/A"