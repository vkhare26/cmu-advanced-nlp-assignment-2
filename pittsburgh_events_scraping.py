import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_all_events():
    # List of months starting from March (names in lowercase)
    months = ['march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    all_events = []

    # Initialize a single Chrome driver instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    for month in months:
        url = f"https://pittsburgh.events/{month}/"
        print(f"Processing URL: {url}")
        driver.get(url)
        
        # Wait for the page to load initial content
        time.sleep(10)
        
        # Click the "Show More" button repeatedly until it is no longer available
        while True:
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ldm"))
                )
                show_more_button.click()
                # Wait for new events to load
                time.sleep(10)
            except Exception as e:
                print(f"No more 'Show More' button found for {month}: {e}")
                break

        # Get the fully loaded page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        event_elements = soup.find_all('a', class_='v-list-char')
        
        for anchor in event_elements:
            link = anchor.get('href')
            try:
                month_text = anchor.find('div', class_='d-month').get_text(strip=True)
            except Exception:
                month_text = None
            try:
                day = anchor.find('div', class_='d-day').get_text(strip=True)
            except Exception:
                day = None
            try:
                year = anchor.find('div', class_='d-year').get_text(strip=True)
            except Exception:
                year = None
            try:
                name = anchor.find('div', class_='pname').get_text(strip=True)
            except Exception:
                name = None
            try:
                location = anchor.find('span', class_='d-location').get_text(strip=True)
            except Exception:
                location = None
            
            all_events.append({
                "month": month_text,
                "day": day,
                "year": year,
                "name": name,
                "location": location,
                "link": link
            })
    
    driver.quit()
    return all_events

if __name__ == '__main__':
    events = scrape_all_events()
    final_df = pd.DataFrame(events)
    final_df.to_csv('pittsburg_events_in_2025.csv', index=False)
    print("Events saved to pittsburg_events_in_2025.csv")
