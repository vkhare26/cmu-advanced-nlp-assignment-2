import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_pghcitypaper_events():
    events = []
    
    # Initialize a single Chrome driver instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Loop through pages 1 to 22
    for page in range(1, 23):
        url = f"https://www.pghcitypaper.com/pittsburgh/EventSearch?page={page}&v=d"
        print(f"Scraping page {page}: {url}")
        driver.get(url)
        
        # Wait for the page to load; adjust sleep time if needed
        time.sleep(5)
        
        # Find all event containers on the page
        event_items = driver.find_elements(By.CSS_SELECTOR, "li.fdn-pres-item")
        print(f"Found {len(event_items)} events on page {page}.")
        
        for item in event_items:
            # Extract the event title and link from the headline element
            try:
                headline = item.find_element(By.CSS_SELECTOR, "p.fdn-teaser-headline a")
                title = headline.text.strip()
                link = headline.get_attribute("href")
            except Exception:
                title, link = "", ""
            
            # Extract schedule info
            try:
                schedule = item.find_element(By.CSS_SELECTOR, "p.fdn-teaser-subheadline").text.strip()
            except Exception:
                schedule = ""
            
            # Extract location details: name and address
            try:
                location_block = item.find_element(By.CSS_SELECTOR, "div.fdn-event-teaser-location-block")
                try:
                    location_name = location_block.find_element(By.CSS_SELECTOR, "p.fdn-event-teaser-location a").text.strip()
                except Exception:
                    location_name = ""
                try:
                    address = location_block.find_element(By.CSS_SELECTOR, "p.fdn-inline-split-list").text.strip()
                except Exception:
                    address = ""
            except Exception:
                location_name, address = "", ""
            
            # Extract tag (if available)
            try:
                tag = item.find_element(By.CSS_SELECTOR, "p.fdn-teaser-infoline.uk-text-break.uk-margin-xsmall-top a").text.strip()
            except Exception:
                tag = ""
            
            # Extract description text
            try:
                description = item.find_element(By.CSS_SELECTOR, "div.fdn-teaser-description").text.strip()
            except Exception:
                description = ""
            
            events.append({
                "title": title,
                "link": link,
                "schedule": schedule,
                "location_name": location_name,
                "address": address,
                "tag": tag,
                "description": description
            })
    
    driver.quit()
    return events

if __name__ == '__main__':
    event_data = scrape_pghcitypaper_events()
    
    # Create a DataFrame from the scraped events and save it to CSV
    df = pd.DataFrame(event_data)
    df.to_csv("pghcitypaper_events.csv", index=False)
    print("Data saved to pghcitypaper_events.csv")
