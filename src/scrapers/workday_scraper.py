import csv
import time
from datetime import datetime
import re
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

US_KEYWORDS = {
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
}

def is_us_location(location):
    tokens = set(re.split(r"[\s,\-]+", location.upper()))
    return bool(tokens & US_KEYWORDS)

def scrape_workday_jobs(base_url, search_terms):
    print("test")
    print(f"Scraping Workday jobs from {base_url}...")
    all_jobs = []
    tokens = [term.lower() for term in search_terms]

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(base_url)
    wait = WebDriverWait(driver, 20)

    try:
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-automation-id='keywordSearchInput']")))
        search_input.clear()
        search_input.send_keys(" ".join(search_terms))
        search_btn = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='keywordSearchButton']")
        search_btn.click()
        time.sleep(4)
    except Exception as e:
        print(f"Search input issue: {e}")
        driver.quit()
        return []

    seen_urls = set()

    while True:
        try:
            job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")))
            for card in job_cards:
                title = card.text.strip()
                url = card.get_attribute("href")
                try:
                    location_elem = card.find_element(By.XPATH, ".//following::dd[contains(@class, 'css-129m7dg')][1]")
                    location = location_elem.text.strip()
                except:
                    location = "N/A"

                if url not in seen_urls and any(tok in title.lower() for tok in tokens):
                    seen_urls.add(url)
                    all_jobs.append({
                        "Title": title,
                        "URL": url,
                        "Location": location,
                        "Confirmed_US": is_us_location(location)
                    })

            next_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-uxi-element-id='next']")
            if next_buttons and next_buttons[0].is_enabled():
                next_buttons[0].click()
                time.sleep(4)
            else:
                break
        except Exception as e:
            print(f"Pagination/extraction issue: {e}")
            break
    driver.quit()
    return all_jobs

    
    