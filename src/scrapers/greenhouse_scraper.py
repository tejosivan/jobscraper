import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

US_KEYWORDS = {
    "US", "USA", "UNITED", "STATES", "UNITED STATES",
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "ALABAMA", "ALASKA", "ARIZONA", "ARKANSAS", "CALIFORNIA", "COLORADO", "CONNECTICUT", "DELAWARE",
    "FLORIDA", "GEORGIA", "HAWAII", "IDAHO", "ILLINOIS", "INDIANA", "IOWA", "KANSAS", "KENTUCKY", "LOUISIANA",
    "MAINE", "MARYLAND", "MASSACHUSETTS", "MICHIGAN", "MINNESOTA", "MISSISSIPPI", "MISSOURI", "MONTANA",
    "NEBRASKA", "NEVADA", "NEW HAMPSHIRE", "NEW JERSEY", "NEW MEXICO", "NEW YORK", "NORTH CAROLINA",
    "NORTH DAKOTA", "OHIO", "OKLAHOMA", "OREGON", "PENNSYLVANIA", "RHODE ISLAND", "SOUTH CAROLINA",
    "SOUTH DAKOTA", "TENNESSEE", "TEXAS", "UTAH", "VERMONT", "VIRGINIA", "WASHINGTON", "WEST VIRGINIA",
    "WISCONSIN", "WYOMING", "Locations", "Remote", "Anywhere"
}

def is_us_location(location):
    tokens = set(re.split(r"[\s,\-]+", location.upper()))
    return bool(tokens & US_KEYWORDS)

def scrape_greenhouse_jobs(base_url: str, search_terms: list[str]) -> list[dict]:
    print(f"\nScraping jobs from {base_url}...")
    all_jobs = []
    try:
        # Extract job board token from URL
        board = base_url.rstrip('/').split('/')[-1]
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
        response = requests.get(api_url)
        data = response.json()

        tokens = [t.lower() for t in search_terms]
        for job in data.get("jobs", []):
            title = job.get("title", "")
            location = job.get("location", {}).get("name", "N/A")
            url = job.get("absolute_url", "")

            if any(tok in title.lower() for tok in tokens):
                all_jobs.append({
                    "Title": title,
                    "URL": url,
                    "Location": location,
                    "Confirmed_US": is_us_location(location)
                })

        print(f"Found {len(all_jobs)} job(s).")
    except Exception as e:
        print(f"Error: {e}")
    return all_jobs
