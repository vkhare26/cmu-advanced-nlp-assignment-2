import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

def extract_event_details(event_container):
    """Extract details from a single event container."""
    # Initialize empty fields
    title = event_link = event_date = location = image_url = ""
    
    # Extract the event title and link from the 'evt_name' anchor
    try:
        title_elem = event_container.find_element(By.CSS_SELECTOR, "a.evt_name")
        title = title_elem.text.strip()
        event_link = title_elem.get_attribute("href")
    except Exception:
        pass

    # Extract the event date and location from the description div.
    # The div contains a <lightning-formatted-date-time> element and then a pipe and location.
    try:
        desc_div = event_container.find_element(By.CSS_SELECTOR, "div.description")
        # Get the date from the lightning-formatted-date-time element
        try:
            event_date = event_container.find_element(By.TAG_NAME, "lightning-formatted-date-time").text.strip()
        except Exception:
            event_date = ""
        # Get the full description text and split on the pipe symbol "|"
        desc_text = desc_div.text.strip()
        # Look for a pipe separator and extract the part after it as location.
        if "|" in desc_text:
            parts = desc_text.split("|")
            if len(parts) >= 2:
                location = parts[1].strip()
    except Exception:
        pass

    # Extract the background image URL from the featured image div.
    try:
        # Locate the div with class 'featuredImageEvt' and then the inner div with class 'image'
        image_div = event_container.find_element(By.CSS_SELECTOR, "div.featuredImageEvt div.image")
        style_attr = image_div.get_attribute("style")
        # The style attribute looks like: background-image:url(https://...);
        # Use a regex or string manipulation to extract the URL.
        match = re.search(r'url\((.*?)\)', style_attr)
        if match:
            image_url = match.group(1).strip().strip('"').strip("'")
    except Exception:
        pass

    return {
        "title": title,
        "event_link": event_link,
        "event_date": event_date,
        "location": location,
        "image_url": image_url
    }

def scrape_community_events():
    all_events = []
    
    # Initialize a single Chrome driver instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    start_url = "https://community.cmu.edu/s/events"
    driver.get(start_url)
    
    # Allow time for the page to load
    time.sleep(10)
    
    while True:
        print("Scraping current page...")
        # Find all event containers on the current page.
        # In the snippet, each event is contained in a <div> with classes including "cCommunity_Event_Tile"
        event_containers = driver.find_elements(By.CSS_SELECTOR, "div.cCommunity_Event_Tile")
        print(f"Found {len(event_containers)} events on this page.")
        
        # Extract details from each event container.
        for container in event_containers:
            event_data = extract_event_details(container)
            all_events.append(event_data)
        
        # Try to click the Next button. It is a button with class "pre_next_btn" and text "Next".
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button.pre_next_btn")
            # Check if the next button is displayed and enabled
            if next_button.is_displayed() and next_button.is_enabled():
                print("Clicking Next button...")
                next_button.click()
                # Wait for the next page to load.
                time.sleep(5)
            else:
                print("Next button not clickable; ending pagination.")
                break
        except NoSuchElementException:
            print("Next button not found; ending pagination.")
            break
        except ElementClickInterceptedException:
            print("Next button not clickable (click intercepted); ending pagination.")
            break

    driver.quit()
    return all_events

if __name__ == '__main__':
    events = scrape_community_events()
    df = pd.DataFrame(events)
    # Save the aggregated events to a CSV file.
    df.to_csv("campus_events.csv", index=False)
    print("Data saved to pghcitypaper_events.csv")
