import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta

def scrape_cmu_events_for_date(driver, date_str):
    """
    Given a Selenium driver and a date string (YYYYMMDD), load the page and scrape event details.
    Returns a list of dictionaries with event data.
    """
    url = f"https://events.cmu.edu/day/date/{date_str}"
    print(f"Scraping URL: {url}")
    driver.get(url)
    
    # Wait for the page to load completely (adjust if necessary)
    time.sleep(5)
    
    events_for_date = []
    try:
        # Locate all event containers on the page
        event_containers = driver.find_elements(By.CSS_SELECTOR, "div.lw_cal_event")
    except Exception as e:
        print(f"Error finding event containers for {date_str}: {e}")
        event_containers = []
    
    for event in event_containers:
        try:
            location = event.find_element(By.CSS_SELECTOR, "div.lw_events_location").text.strip()
        except Exception:
            location = ""
        try:
            start_time = event.find_element(By.CSS_SELECTOR, "span.lw_start_time").text.strip()
        except Exception:
            start_time = ""
        try:
            end_time = event.find_element(By.CSS_SELECTOR, "span.lw_end_time").text.strip()
        except Exception:
            end_time = ""
        try:
            title_element = event.find_element(By.CSS_SELECTOR, "div.lw_events_title a")
            title = title_element.text.strip()
            event_link = title_element.get_attribute("href")
        except Exception:
            title = ""
            event_link = ""
        try:
            summary = event.find_element(By.CSS_SELECTOR, "div.lw_events_summary p").text.strip()
        except Exception:
            summary = ""
        try:
            img_element = event.find_element(By.CSS_SELECTOR, "span.lw_item_thumb img")
            img_url = img_element.get_attribute("src")
        except Exception:
            img_url = ""
        
        events_for_date.append({
            "page_date": date_str,  # the date for which this page was scraped
            "location": location,
            "start_time": start_time,
            "end_time": end_time,
            "title": title,
            "event_link": event_link,
            "summary": summary,
            "image_url": img_url
        })
    return events_for_date

if __name__ == '__main__':
    # Define the start and end dates
    start_date = datetime(2025, 3, 19)
    end_date = datetime(2025, 12, 31)
    delta = end_date - start_date
    
    all_events = []
    
    # Initialize a single Chrome driver instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Loop over every day in the range
    for i in range(delta.days + 1):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d")
        events_for_date = scrape_cmu_events_for_date(driver, date_str)
        print(f"Found {len(events_for_date)} events for {date_str}")
        all_events.extend(events_for_date)
    
    driver.quit()
    
    # Create a DataFrame from the collected events and save to CSV
    df = pd.DataFrame(all_events)
    csv_filename = "cmu_events_20250319_to_20251231.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")
