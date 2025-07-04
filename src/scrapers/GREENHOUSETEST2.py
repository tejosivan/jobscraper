import requests
import csv
import os
from datetime import datetime

def scrape_greenhouse_jobs(company_name, search_terms):
    print(f"🔍 Scraping jobs for '{company_name}' from API…")
    api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_name}/jobs"
    response = requests.get(api_url)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch data: {response.status_code}")
        return

    data = response.json()
    jobs = []

    tokens = [t.lower() for t in search_terms] if isinstance(search_terms, list) else search_terms.lower().split()

    for job in data.get("jobs", []):
        title = job.get("title", "").strip()
        location = job.get("location", {}).get("name", "N/A")
        url = job.get("absolute_url", "")
        title_lc = title.lower()

        print(f"🔎 Checking: {title}")

        if not any(tok in title_lc for tok in tokens):
            continue

        jobs.append({
            "Title": title,
            "URL": url,
            "Location": location
        })

    today = datetime.now().strftime("%Y%m%d")
    filename = f"{company_name}_jobs_{today}.csv"
    filepath = os.path.join(os.path.dirname(__file__), "../scraped_jobs", filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "URL", "Location"])
        writer.writeheader()
        writer.writerows(jobs)

    print(f"✅ {len(jobs)} jobs saved to {filepath}")

if __name__ == "__main__":
    scrape_greenhouse_jobs("canonical", ["data", "engineer"])
