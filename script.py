from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import csv
import time
import os

#Configuration
SEARCH_URL = "https://www.olx.in/items/q-car-cover" # URL Provided
OUTPUT_FILE = "olx_car_covers_filtered.csv" # Output file name
TIMEOUT_SECONDS = 20  
POPUP_TIMEOUT_SECONDS = 15
LOAD_MORE_TIMEOUT = 15 # Timeout for waiting for new items after click
MAX_LOAD_MORE_CLICKS = 15 # Safety break to prevent infinite loops

# Setting relevant IDs for filtering
# Inspect OLX page source for items to find more relevant IDs if needed
ALLOWED_CATEGORY_IDS = {'1585', '1587'} # 1585 (Spare Parts), 1587 (Spare Parts)


# Setting up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless=new") # No web UI
options.add_argument("--no-sandbox") 
options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
options.add_argument("--window-size=1920,1080") # ffor better rendering
options.add_argument("--disable-gpu") # Disable GPU acceleration
options.add_argument("--enable-unsafe-swiftshader") # Enable SwiftShader for WebGL
options.add_argument('--disable-blink-features=AutomationControlled') # Disable automation control
options.add_experimental_option("excludeSwitches", ["enable-automation"])  
options.add_experimental_option('useAutomationExtension', False) # Disable automation extension
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")

# Initializeing WebDriver
driver = None
try:
    print("Setting up ChromeDriver...")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("WebDriver initialized.")

    # Main Scraper Logic 
    scraped_links = set() # To avoid duplicates
    results = []
    print(f"Loading page: {SEARCH_URL}")
    driver.get(SEARCH_URL)
    print(f"Page title: {driver.title}")

    print("Initial pause for page rendering (3s)...")
    time.sleep(3)

    # Handle Location Pop-up 
    location_popup_closed = False
    location_popup_close_button_selector = (By.XPATH, "//button[@data-aut-id='location_//_close']")
    try:
        print(f"Waiting for location pop-up close button (max {POPUP_TIMEOUT_SECONDS}s)...")
        close_button = WebDriverWait(driver, POPUP_TIMEOUT_SECONDS).until(
            EC.element_to_be_clickable(location_popup_close_button_selector)
        )
        close_button.click()
        print("Location pop-up closed by CLICK.")
        location_popup_closed = True
        time.sleep(2)
    except TimeoutException:
        print("Location pop-up close button NOT found or NOT clickable.")
        if not location_popup_closed:
            print("Attempting to close potential pop-up with ESCAPE key...")
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                print("ESCAPE key sent.")
                location_popup_closed = True
                time.sleep(2)
            except Exception as e_esc:
                print(f"Error sending ESCAPE key: {e_esc}")
    except Exception as e_popup:
        print(f"An error occurred handling the location pop-up: {e_popup}")

    if not location_popup_closed:
        print("Could not confirm pop-up closure. Proceeding.")

    # Load More & Scraping Loop 
    load_more_button_selector = (By.XPATH, "//button[@data-aut-id='btnLoadMore']")
    list_item_container_selector = (By.XPATH, "//li[starts-with(@data-aut-id, 'itemBox')]")
    load_more_clicks = 0

    while load_more_clicks < MAX_LOAD_MORE_CLICKS:
        print(f"\nScraping page/batch {load_more_clicks + 1}...")
        initial_item_count = len(driver.find_elements(*list_item_container_selector))
        print(f"Items currently on page: {initial_item_count}")

        # Wait for items to be stable before scraping this batch
        try:
             WebDriverWait(driver, TIMEOUT_SECONDS).until(
                 EC.presence_of_element_located(list_item_container_selector)
             )
             time.sleep(2) # Give extra time for potential JS rendering
             items = driver.find_elements(*list_item_container_selector)
        except TimeoutException:
             print("Warning: Timed out waiting for items on this batch. Skipping batch.")
             items = []

        new_items_found_in_batch = 0
        for item_element in items:
            # Initialize variables
            title, price, link, location, date_posted, category_id = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
            try:
                # Get category ID from the item element
                try:
                    category_id = item_element.get_attribute('data-aut-category-id')
                except Exception:
                    category_id = None # Handle if attribute doesn't exist

                # Filter by category ID
                if not category_id or category_id not in ALLOWED_CATEGORY_IDS:
                    continue # Skip this item if category doesn't match

                # Link
                try:
                    link_element = item_element.find_element(By.XPATH, ".//a")
                    link = link_element.get_attribute("href")
                    if not link: link = "N/A"
                except NoSuchElementException:
                    continue # Must have a link

                # Avoid duplicates
                if link in scraped_links:
                    continue

                # Title
                try:
                    title_element = item_element.find_element(By.XPATH, ".//span[@data-aut-id='itemTitle']")
                    title = title_element.text.strip()
                except NoSuchElementException: pass

                # Price
                try:
                    price_element = item_element.find_element(By.XPATH, ".//span[@data-aut-id='itemPrice']")
                    price = price_element.text.strip()
                except NoSuchElementException: pass

                # Location
                try:
                    location_element = item_element.find_element(By.XPATH, ".//span[@data-aut-id='item-location']")
                    location = location_element.text.strip()
                except NoSuchElementException: pass

                # Date Posted
                try:
                    date_element = item_element.find_element(By.XPATH, ".//div[span[@data-aut-id='item-location']]/span[last()]")
                    date_posted = date_element.text.strip()
                except NoSuchElementException: pass

                if link != "N/A":
                    results.append({
                        "title": title,
                        "price": price,
                        "location": location,
                        "date_posted": date_posted,
                        "link": link,
                        "category_id": category_id # Optional: Keeping for reference
                    })
                    scraped_links.add(link)
                    new_items_found_in_batch += 1

            except Exception as e_item:
                print(f"Error scraping individual item details (Link: {link}): {e_item}")
                continue

        print(f"Scraped {new_items_found_in_batch} new items in this batch (Category IDs: {ALLOWED_CATEGORY_IDS}). Total results: {len(results)}")

        #  Attempt to Click "Load More" 
        try:
            print("Looking for 'Load More' button...")
            load_more_button = WebDriverWait(driver, 5).until( # Short wait for button
                EC.element_to_be_clickable(load_more_button_selector)
            )
            # Scroll button into view slightly - sometimes needed for click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
            time.sleep(1) # Pause after scroll before click
            load_more_button.click()
            print("'Load More' button clicked.")
            load_more_clicks += 1

            # Wait for new content to load by checking if item count increases
            print(f"Waiting for new items to load (max {LOAD_MORE_TIMEOUT}s)...")
            WebDriverWait(driver, LOAD_MORE_TIMEOUT).until(
                lambda d: len(d.find_elements(*list_item_container_selector)) > initial_item_count
            )
            print("New items detected.")
            time.sleep(3) # Pause after new items load

        except TimeoutException:
            print("'Load More' button not found or no new items loaded after click. Assuming end of results.")
            break # Exit loop if button isn't found or clickable
        except ElementClickInterceptedException:
             print("'Load More' button was intercepted (likely by an overlay). Trying again after a pause...")
             time.sleep(5) # Wait longer if intercepted
             # If it keeps happening, break the loop

             if load_more_clicks > 1 and load_more_clicks % 3 == 0: # Break after 3 consecutive intercepts
                 print("Button click intercepted multiple times. Stopping.")
                 break
        except Exception as e_load:
            print(f"An error occurred during 'Load More': {e_load}")
            break # Exit loop on other errors

    print(f"\nFinished loading items after {load_more_clicks} clicks.")

except TimeoutException as e_timeout:
    print(f"Script timed out: {e_timeout}. Check network or increase TIMEOUT_SECONDS.")
except Exception as e_main:
    print(f"An unexpected main error occurred: {e_main}")

finally:
    # Save results to CSV file
    if results:
        print(f"\nSaving {len(results)} results to {OUTPUT_FILE}...")
        try:
            # Include category_id in output if you want to check it
            fieldnames = ["title", "price", "location", "date_posted", "link", "category_id"]
            with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Successfully saved results to {OUTPUT_FILE}")
        except IOError as e_io:
            print(f"Error writing to file {OUTPUT_FILE}: {e_io}")
    else:
        print("No results matching the allowed categories were scraped.")

    # Clean up WebDriver
    if driver:
        print("Closing WebDriver.")
        driver.quit()