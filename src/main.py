# imports
import sys
from urllib.parse import urlparse
#from scrapers.workday_scraper import scrape_workday_jobs
from scrapers.workday import scrape_workday_jobs
from scrapers.greenhouse_scraper import scrape_greenhouse_jobs
import csv
import os
from datetime import datetime

def detect_platform(url):
    netloc = urlparse(url).netloc
    if "workday" in netloc:
        return "workday"
    elif "greenhouse" in netloc:
        return "greenhouse"
    else:
        return "unknown"

def write_csv(jobs, base_url, search_term):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{base_url.split('//')[1].split('.')[0]}_{search_term.replace(' ', '_').lower()}_jobs_{today}.csv"
    filepath = os.path.join(os.path.dirname(__file__), "scraped_jobs", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "URL", "Location", "Confirmed_US"])
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)
    print(f" {len(jobs)} jobs saved to {filepath}")


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <base_url> \"<search_term>\"")
        sys.exit(1)

    print("test main.py 1")

    base_url = sys.argv[1]
    search_term = sys.argv[2]
    platform = detect_platform(base_url)

    if platform == "workday":
        print("test main.py 2 calling workday scraper")
        jobs = scrape_workday_jobs(base_url, search_term)
    elif platform == "greenhouse":
        jobs = scrape_greenhouse_jobs(base_url, search_term.split())
        print("test main.py 3 calling greenhouse scraper")
    else:
        print("Currently unsupported job platform.")
        sys.exit(1)

    if jobs:
        write_csv(jobs, base_url, search_term)
    else:
        print("No jobs found")

if __name__ == "__main__":
    main()
