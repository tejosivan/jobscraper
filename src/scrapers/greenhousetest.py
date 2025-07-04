import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from datetime import datetime

US_KEYWORDS = {
    "US", "USA", "STATES", "UNITED STATES",
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
    "ALABAMA","ALASKA","ARIZONA","ARKANSAS","CALIFORNIA","COLORADO","CONNECTICUT","DELAWARE",
    "FLORIDA","GEORGIA","HAWAII","IDAHO","ILLINOIS","INDIANA","IOWA","KANSAS","KENTUCKY","LOUISIANA",
    "MAINE","MARYLAND","MASSACHUSETTS","MICHIGAN","MINNESOTA","MISSISSIPPI","MISSOURI","MONTANA",
    "NEBRASKA","NEVADA","NEW HAMPSHIRE","NEW JERSEY","NEW MEXICO","NEW YORK","NORTH CAROLINA",
    "NORTH DAKOTA","OHIO","OKLAHOMA","OREGON","PENNSYLVANIA","RHODE ISLAND","SOUTH CAROLINA",
    "SOUTH DAKOTA","TENNESSEE","TEXAS","UTAH","VERMONT","VIRGINIA","WASHINGTON","WEST VIRGINIA",
    "WISCONSIN","WYOMING", "Locations", "Remote", "Anywhere"
}

def is_us_location(location):
    tokens = set(re.split(r"[,\s\-]+", location.upper()))
    return bool(tokens & US_KEYWORDS)

def scrape_greenhouse_jobs(base_url, search_terms):
    print(f"Scraping jobs from {base_url}...")
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tokens = [t.lower() for t in search_terms]  

    jobs = []

    for a in soup.select("a[href^='https://job-boards.greenhouse.io']"):
        ps = a.find_all("p")
        if len(ps) < 2:
            continue
        title, location = ps[0].get_text(strip=True), ps[1].get_text(strip=True)
        url = a["href"]

        if any(tok in title.lower() for tok in tokens):
            jobs.append({
                "Title": title,
                "URL": url,
                "Location": location,
                "Confirmed_US": is_us_location(location)
            })

    today = datetime.now().strftime("%Y%m%d")
    filename = f"{base_url.split('/')[-1]}_jobs_{today}.csv"
    filepath = os.path.join(os.path.dirname(__file__), "../scraped_jobs", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "URL", "Location", "Confirmed_US"])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"✅ Found {len(jobs)} job(s). Saved to {filename}.")

if __name__ == "__main__":
    scrape_greenhouse_jobs("https://job-boards.greenhouse.io/financialtimes33", ["data", "engineer", "Acting"])
