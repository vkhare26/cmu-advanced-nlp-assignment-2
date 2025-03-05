import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def scrape_events_for_month(driver, month_num):
    # Construct the URL for the given month
    url = f"https://downtownpittsburgh.com/events/?n={month_num}&y=2025&cat=0"
    print(f"Scraping URL: {url}")
    driver.get(url)
    
    # Wait for the page to load. Adjust the sleep time if necessary.
    time.sleep(5)
    
    events = []
    # Find all event containers on the page
    event_items = driver.find_elements(By.CLASS_NAME, "eventitem")
    
    for event in event_items:
        try:
            copy = event.find_element(By.CLASS_NAME, "copyContent")
        except Exception:
            continue
        
        # Extract categories from the 'category' div (each term inside 'term')
        try:
            category_div = copy.find_element(By.CLASS_NAME, "category")
            term_elements = category_div.find_elements(By.CLASS_NAME, "term")
            categories = ", ".join([term.text.strip() for term in term_elements])
        except Exception:
            categories = ""
        
        # Extract the event title and link from the <h1><a> element
        try:
            h1 = copy.find_element(By.TAG_NAME, "h1")
            a_tag = h1.find_element(By.TAG_NAME, "a")
            title = a_tag.text.strip()
            link = a_tag.get_attribute("href")
            if link.startswith("/"):
                link = "https://downtownpittsburgh.com" + link
        except Exception:
            title = ""
            link = ""
        
        # Extract the event date from the element with class 'eventdate'
        try:
            event_date = copy.find_element(By.CLASS_NAME, "eventdate").text.strip()
        except Exception:
            event_date = ""
        
        # Extract a rough description by taking all text and removing known parts
        try:
            full_text = copy.text
            try:
                read_more = copy.find_element(By.CLASS_NAME, "button").text.strip()
            except Exception:
                read_more = ""
            description = full_text.replace(categories, "").replace(title, "").replace(event_date, "").replace(read_more, "").strip()
        except Exception:
            description = ""
        
        events.append({
            "month": month_num,  # storing the month number (3 for March, etc.)
            "categories": categories,
            "title": title,
            "link": link,
            "event_date": event_date,
            "description": description
        })
    return events

def scrape_all_events():
    all_events = []
    # Create a single Chrome driver instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Loop through month numbers 3 (March) to 12 (December)
    for month in range(3, 13):
        month_events = scrape_events_for_month(driver, month)
        print(f"Found {len(month_events)} events for month {month}.")
        all_events.extend(month_events)
    
    driver.quit()
    return all_events

if __name__ == '__main__':
    events = scrape_all_events()
    
    # Create a DataFrame and save the aggregated data to CSV
    df = pd.DataFrame(events)
    df.to_csv("downtownpittsburgh_events.csv", index=False)
    print("Data saved to downtownpittsburgh_events.csv")
