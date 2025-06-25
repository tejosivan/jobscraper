###################Import Libraries###################
import csv
import time
from datetime import datetime
import sys
from urllib.parse import quote_plus
import re
import os

#database imports
from dotenv import load_dotenv
import psycopg2
#Selenium Imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
#######################################################
all_jobs = []
###################Helper Functions####################
US_KEYWORDS ={
    "US", "USA", "UNITED", "STATES", "UNITED STATES",
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
    "ALABAMA","ALASKA","ARIZONA","ARKANSAS","CALIFORNIA","COLORADO","CONNECTICUT","DELAWARE",
    "FLORIDA","GEORGIA","HAWAII","IDAHO","ILLINOIS","INDIANA","IOWA","KANSAS","KENTUCKY","LOUISIANA",
    "MAINE","MARYLAND","MASSACHUSETTS","MICHIGAN","MINNESOTA","MISSISSIPPI","MISSOURI","MONTANA",
    "NEBRASKA","NEVADA","NEW HAMPSHIRE","NEW JERSEY","NEW MEXICO","NEW YORK","NORTH CAROLINA",
    "NORTH DAKOTA","OHIO","OKLAHOMA","OREGON","PENNSYLVANIA","RHODE ISLAND","SOUTH CAROLINA",
    "SOUTH DAKOTA","TENNESSEE","TEXAS","UTAH","VERMONT","VIRGINIA","WASHINGTON","WEST VIRGINIA",
    "WISCONSIN","WYOMING","Locations", "Remote", "Anywhere"
} # also includes Locations, Remote, Anywhere

def is_us_location(location):
    tokens = set(re.split(r"[,\s\-]+", location.upper()))
    return bool(tokens & US_KEYWORDS)

def create_jobs_table():
    conn = psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scraped_jobs (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            location TEXT,
            confirmed_us BOOLEAN,scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                """)
    conn.commit()
    cur.close()
    conn.close()
    print("'jobs' table is ready.")

def insert_jobs_to_db(jobs):
    conn = psycopg2.connect(
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname")
    )
    cur = conn.cursor()
    for job in jobs:
        cur.execute("""
            INSERT INTO scraped_jobs (title, url, location, confirmed_us)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """, (job["Title"], job["URL"], job["Location"], job["Confirmed_US"]))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(jobs)} job(s) into the database.")

#################Scraper###############################
def scrape_workday_jobs(base_url, search_query):
    load_dotenv()
    create_jobs_table()
    encoded_query = quote_plus(search_query)
    timestamp = datetime.now().strftime("%Y%m%d")
    output_dir = "scraped_jobs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{base_url.split('//')[1].split('.')[0]}_{search_query.replace(' ', '_').lower()}_jobs_{timestamp}.csv")
    seen_urls = set()


    print("🟪 Launching Selenium browser.\n")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(base_url)
    wait = WebDriverWait(driver, 20)

    # Wait for search box and submit search query
    try:
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-automation-id='keywordSearchInput']")))

        search_input.clear()
        search_input.send_keys(search_query)
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='keywordSearchButton']")
        search_btn.click()
        time.sleep(5)  
    except Exception as e:
        print(f"Search input issue: {e}")
        driver.quit()
        return

    while True:        
        try:
            job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")))
            for card in job_cards:
                title = card.text.strip()
                url = card.get_attribute("href")
                #card_container = card.find_element(By.XPATH, "./ancestor::div[contains(@class, 'css')]")
                #location_elem = card_container.find_element(By.CSS_SELECTOR, "div[data-automation-id='locations'] dd")
                #location = location_elem.text.strip()

                try:
                    location_elem = card.find_element(By.XPATH, ".//following::dd[contains(@class, 'css-129m7dg')][1]")
                    location = location_elem.text.strip()
                except:
                    location = "N/A"

                if url not in seen_urls:
                    seen_urls.add(url)
                    all_jobs.append({"Title": title, "URL": url, "Location": location, "Confirmed_US": is_us_location(location)})

            next_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-uxi-element-id='next']")
            if next_buttons and next_buttons[0].is_enabled():
                next_buttons[0].click()
                time.sleep(4)
            else:
                break   
        except Exception as e:
            print(f"Pagination or extraction failed: {e}")
            break
    driver.quit()
    
    print("🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪")
    print(f"\nFound {len(all_jobs)} {search_query} jobs")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Title", "URL", "Location", "Confirmed_US"])
        writer.writeheader()
        writer.writerows(all_jobs)
    print(f"Saved to {output_file}")
    insert_jobs_to_db(all_jobs)
#######################################################
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("🟪Invokation: python scrape_workday.py <base_url> <search_query>")
        sys.exit(1)

    base_url = sys.argv[1]
    search_query = sys.argv[2]
    scrape_workday_jobs(base_url, search_query)