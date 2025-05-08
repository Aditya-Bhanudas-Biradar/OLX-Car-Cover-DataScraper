# OLX Car Cover Scraper

## Project Overview

This project contains a Python script designed to scrape search results for "Car Cover" from the Indian OLX website (`www.olx.in`). The primary goal was to automate the collection of relevant listings, including details like title, price, location, date posted, and direct link, and save this data into a structured CSV file.

This script was developed as part of an internship assignment, demonstrating web scraping techniques using Python, Selenium, and ChromeDriver.

## Problem Statement

The task was to create a program that could automatically gather listings for "car covers" from OLX India. Manually searching and copying this data is time-consuming and inefficient. The program needed to handle dynamic web content, potential pop-ups, pagination (loading more results), and filter out irrelevant listings (e.g., real estate ads mentioning "covered car parking"). The final output should be a clean, usable CSV file.

## Features

*   **Searches OLX:** Performs a search for "car cover" on `www.olx.in`.
*   **Handles Pop-ups:** Attempts to detect and close the initial location selection pop-up.
*   **Pagination:** Automatically clicks the "Load More" button repeatedly to fetch as many results as possible (up to a defined limit).
*   **Category Filtering:** Filters scraped items based on a predefined list of relevant OLX category IDs (e.g., Spare Parts) to exclude irrelevant results like real estate.
*   **Data Extraction:** Extracts the following details for each relevant ad:
    *   Title
    *   Price
    *   Location
    *   Date Posted
    *   Direct Link to the ad
    *   Category ID (for reference)
*   **CSV Output:** Saves the scraped and filtered data into a structured CSV file (`olx_car_covers_filtered.csv`) using `utf-8-sig` encoding for better compatibility with spreadsheet software like Microsoft Excel (handles currency symbols correctly).
*   **Automated Driver Management:** Uses `webdriver-manager` to automatically download and manage the correct ChromeDriver version compatible with the installed Chrome browser.
*   **Headless Operation:** Configured to run headlessly (without opening a visible browser window).
*   **Anti-Detection Measures:** Includes basic measures like setting a common User-Agent and disabling some automation flags in Selenium.

## Prerequisites

Before running the script, ensure you have the following installed:

1.  **Python:** Version 3.7 or higher is recommended. You can download it from [python.org](https://www.python.org/).
2.  **Pip:** Python's package installer (usually comes with Python).
3.  **Google Chrome:** The script uses ChromeDriver, which requires Google Chrome to be installed. Download it from [google.com/chrome](https://www.google.com/chrome/).
4.  **Git:** For cloning the repository (optional if you download the code directly).

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/olx-scraper-assignment.git
    cd olx-scraper-assignment
    ```

2.  **Create a Virtual Environment (Recommended):**
    This isolates project dependencies.

    *   **On macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **On Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    You should see `(venv)` prepended to your terminal prompt.

3.  **Install Dependencies:**
    Install the required Python packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    This will install `selenium` and `webdriver-manager`.

## Usage

Once the setup is complete, simply run the script from your terminal within the project directory (and with the virtual environment activated):

```bash
python olx_scraper.py
```

## Development Challenges & Solutions

During the development of this script, several common web scraping challenges were encountered and addressed:

1.  **Dynamic Selectors:** Initial attempts using CSS class names failed because OLX uses dynamically generated classes.
    *   **Solution:** Switched to using more stable `data-aut-id` attributes and structural XPath selectors identified by inspecting the page source.
2.  **Pop-up Handling:** An initial location selection pop-up often blocked interactions.
    *   **Solution:** Implemented explicit waits (`WebDriverWait`) to detect and click the pop-up's close button, with an ESC key press as a fallback.
3.  **Irrelevant Results:** The broad search term "car cover" included listings for unrelated items like real estate.
    *   **Solution:** Implemented filtering *within the script* based on the `data-aut-category-id` attribute of each listing, keeping only items from predefined relevant categories (`ALLOWED_CATEGORY_IDS`). A previous attempt to filter via URL parameters proved too restrictive.
4.  **Incomplete Data:** Only the initially loaded ads were being scraped.
    *   **Solution:** Added logic to repeatedly find and click the "Load More" button until all available ads are loaded (or a limit is reached), ensuring comprehensive data collection.
5.  **Encoding Issues:** The Rupee currency symbol (₹) displayed incorrectly in some spreadsheet programs.
    *   **Solution:** Changed the output file encoding from `utf-8` to `utf-8-sig` to add a Byte Order Mark (BOM), improving compatibility, especially with Microsoft Excel.

## Potential Future Errors

Web scraping scripts rely heavily on the target website's structure. This script might break or produce fewer/incorrect results in the future if:

*   **OLX changes its website structure:** Modifications to HTML tags, `data-aut-id` attributes, or the layout of listings will require updating the script's selectors (XPATHs).
*   **OLX updates its anti-scraping measures:** Websites often implement techniques to detect and block automated scraping. If this happens, the script might be blocked or fail to load data correctly.
*   **Changes to "Load More" mechanism:** If the way new ads are loaded changes (e.g., different button selector, infinite scroll instead of a button), the pagination logic will need adjustments.
*   **New mandatory pop-ups:** Additional pop-ups (like cookie consent changes) might interfere with the script's flow.

If you encounter errors, inspecting the page source on OLX and comparing it to the selectors used in the script is the first step in debugging.