import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def scrape_ps_events_to_csv():
    # Base URL with 'page=' at the end (but not a fixed page number)
    base_url = (
        "https://www.pittsburghsymphony.org/calendar?"
        "end_date=2026%2F09%2F07&filter%5Bcurrent_page%5D=production&"
        "filter%5Bmax%5D=2026-09-07+14%3A22%3A23+-0400&"
        "filter%5Bmin%5D=2025-03-07T14%3A22%3A23-05%3A00&"
        "genre=All+Genres&organization_id=2&start_date=2025%2F03%2F19&page="
    )

    # Configure Selenium (headless mode)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)

    # List to store all event dictionaries
    all_events = []

    # Loop through pages 1 to 6
    for page_num in range(1, 7):
        # Construct the full URL by appending the page number
        url = f"{base_url}{page_num}"
        print(f"Scraping Page {page_num}: {url}")
        driver.get(url)

        # Give the page a few seconds to load
        time.sleep(3)

        # Find all <article class="event"> blocks
        event_articles = driver.find_elements(By.CSS_SELECTOR, "article.event")

        for article in event_articles:
            # Extract the event data
            try:
                title_elem = article.find_element(By.CSS_SELECTOR, ".event-details-wrap h3.title a")
                event_title = title_elem.text.strip()
            except:
                event_title = "N/A"

            # Date from <time class="range" datetime="...">
            try:
                time_elem = article.find_element(By.CSS_SELECTOR, ".time-wrapper time.range")
                date_text = time_elem.text.strip()
                date_attr = time_elem.get_attribute("datetime")
            except:
                date_text = "N/A"
                date_attr = "N/A"

            # Venue from <div class="venue">
            try:
                venue_elem = article.find_element(By.CSS_SELECTOR, ".venue")
                venue_text = venue_elem.text.strip()
            except:
                venue_text = "N/A"

            # Organization from <div class="organization">
            try:
                org_elem = article.find_element(By.CSS_SELECTOR, ".organization")
                org_text = org_elem.text.strip()
            except:
                org_text = "N/A"

            # Categories from <ul class="category-group">
            try:
                cat_elems = article.find_elements(By.CSS_SELECTOR, ".category-group li.category a")
                categories = [c.text.strip() for c in cat_elems]
            except:
                categories = []

            event_info = {
                "page": page_num,
                "title": event_title,
                "date_text": date_text,   # e.g. "Sat, Mar 15, 2025"
                "date_attr": date_attr,   # e.g. "2025-03-15"
                "venue": venue_text,
                "organization": org_text,
                "categories": ", ".join(categories),
            }
            all_events.append(event_info)

    driver.quit()

    # Convert the list of dictionaries into a Pandas DataFrame
    df = pd.DataFrame(all_events)

    # Save the DataFrame to a CSV file
    output_path = "/Users/vkhare26/Documents/anlp/HW2/cmu-advanced-nlp-assignment-2/data/pso_events.csv"
    df.to_csv(output_path, index=False)
    print(f"Scraped events saved to '{output_path}'.")

if __name__ == "__main__":
    scrape_ps_events_to_csv()
