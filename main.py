import json
import pandas as pd

from scraper import run_scraper
from config import CSV_FILE, JSON_FILE, OUTPUT_DIR
from utils import ensure_output_dir, log


def save_output(tenders):
    ensure_output_dir(OUTPUT_DIR)

    seen = set()
    unique = []
    for t in tenders:
        key = t.get("bid_number") or str(t)
        if key not in seen:
            seen.add(key)
            unique.append(t)

    log.info(f"Saving {len(unique)} unique tenders...")

    df = pd.DataFrame(unique)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    log.info(f"CSV saved → {CSV_FILE}")

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    log.info(f"JSON saved → {JSON_FILE}")

    return unique


def main():
    tenders = run_scraper()

    if not tenders:
        log.warning("No tenders were scraped. Check the site structure or your internet connection.")
        return

    saved = save_output(tenders)

    print("\n========== SCRAPE SUMMARY ==========")
    print(f"Total tenders collected : {len(saved)}")
    print(f"CSV output              : {CSV_FILE}")
    print(f"JSON output             : {JSON_FILE}")
    print("=====================================\n")

    for t in saved[:3]:
        print(t)


if __name__ == "__main__":
    main()
