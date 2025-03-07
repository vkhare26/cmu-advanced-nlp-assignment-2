import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

def scrape_opera_calendar_5_months():
    # Initial page (March)
    url = "https://pittsburghopera.org/calendar?timequery=month&prev=-1&start=1740805200000&end=1743393600000"
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    all_events = []

    # We'll scrape the initial page + 4 more "Next" clicks (total 5 months).
    # If you literally want 5 "Next" clicks after March, do range(5).
    # If you only want 4 clicks total (March -> July), do range(4).
    for i in range(5):
        # Wait for the page to load
        time.sleep(3)

        # SCRAPE events on the current page
        event_containers = driver.find_elements(By.CSS_SELECTOR, "div.event-container")
        for container in event_containers:
            try:
                event_block = container.find_element(By.CSS_SELECTOR, "div.event")
            except:
                continue

            # Title
            try:
                title_elem = event_block.find_element(By.TAG_NAME, "h4")
                event_title = title_elem.text.strip()
            except:
                event_title = "N/A"

            # Dates/Times from <p class="date">
            try:
                date_elems = event_block.find_elements(By.CSS_SELECTOR, "p.date")
                date_times = [d.text.strip() for d in date_elems]
            except:
                date_times = []

            # Location (any <p> not class="date")
            location = "N/A"
            try:
                all_paragraphs = event_block.find_elements(By.TAG_NAME, "p")
                for p in all_paragraphs:
                    if "date" not in p.get_attribute("class"):
                        text_ = p.text.strip()
                        if text_:
                            location = text_
            except:
                pass

            # Link
            try:
                link_elem = event_block.find_element(By.TAG_NAME, "a")
                event_link = link_elem.get_attribute("href")
            except:
                event_link = "N/A"

            # Image
            try:
                image_block = container.find_element(By.CSS_SELECTOR, "div.event-container__img img")
                image_src = image_block.get_attribute("src")
            except:
                image_src = "N/A"

            event_info = {
                "month_click": i,  # which iteration
                "title": event_title,
                "dates": " | ".join(date_times),
                "location": location,
                "link": event_link,
                "image": image_src
            }
            all_events.append(event_info)

        # CLICK "NEXT" if it's not the last iteration
        if i < 5:  # only click "Next" 4 times if you want total 5 months
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "div.next a.button.button--primary")
                print(f"Clicking 'Next' (iteration {i+1})...")
                next_button.click()
            except NoSuchElementException:
                print("No Next button found. Stopping early.")
                break

    driver.quit()

    # Convert to DataFrame and save
    df = pd.DataFrame(all_events)
    df.to_csv("pittsburgh_opera_5months.csv", index=False)
    print("Scraped events saved to 'pittsburgh_opera_5months.csv'.")

if __name__ == "__main__":
    scrape_opera_calendar_5_months()
