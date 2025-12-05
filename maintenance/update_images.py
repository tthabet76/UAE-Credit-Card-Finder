"""
[AGENT 3] Image Updater
This agent is responsible for visiting card URLs and extracting the best possible image.
It handles bank-specific logic (like Emirates Islamic tile images) and updates the 'card_images' table.
It is designed to run independently of the main text scraper.
"""
import sqlite3
import time
import re
import os
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

# --- CONFIGURATION ---
from dotenv import load_dotenv
load_dotenv(override=True)

chromedriver_path = 'C:/Users/cdf846/Documents/personal/Credit card project/chromedriver.exe'
db_file = 'credit_card_data.db'

def setup_image_table(database_file):
    """Ensures the card_images table exists."""
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER UNIQUE,
        bank_name TEXT,
        card_name TEXT,
        scraper_image_url TEXT,
        scraper_date TEXT,
        card_url TEXT,
        FOREIGN KEY(card_id) REFERENCES credit_cards_details(id)
    );
    """)
    conn.commit()
    conn.close()

def get_cards_needing_images(database_file):
    """Fetches cards that need image updates (or all cards if we want to refresh)."""
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # For now, let's process ALL active cards to ensure we populate the new table.
    # We join with credit_cards_details to get the stable ID.
    sql = """
    SELECT d.id as card_id, d.url, d.bank_name, d.card_name
    FROM credit_cards_details d
    JOIN card_inventory i ON d.url = i.url
    WHERE i.is_active = 1
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def extract_image_url(driver, bank_name, current_url):
    """
    The core logic for finding the image.
    Contains both GENERIC and BANK-SPECIFIC strategies.
    """
    extracted_image_url = None
    
    try:
        # --- STRATEGY 1: Generic Meta Tags (Works for 80% of sites) ---
        # Try og:image
        meta_og_img = driver.find_elements(By.XPATH, '//meta[@property="og:image"]')
        if meta_og_img:
            extracted_image_url = meta_og_img[0].get_attribute('content')
        
        # Fallback to twitter:image
        if not extracted_image_url:
            meta_tw_img = driver.find_elements(By.XPATH, '//meta[@name="twitter:image"]')
            if meta_tw_img:
                extracted_image_url = meta_tw_img[0].get_attribute('content')

        # --- STRATEGY 2: Bank Specific Logic ---
        
        # [Emirates Islamic] - Tile Image Construction
        if bank_name == 'Emirates Islamic' and extracted_image_url:
            try:
                # The og:image is usually a banner. We want the tile.
                # Example Banner: .../banners/credit-card-banners/skywards_black_credit_card_1920x650_en.jpg
                # Target Tile:    .../tile-images/skywards_black_credit_card_550x346.png
                
                # 1. Replace the path
                if 'banners/credit-card-banners' in extracted_image_url:
                    constructed_url = extracted_image_url.replace('banners/credit-card-banners', 'tile-images')
                    
                    # 2. Replace the dimensions/extension
                    # Regex to find _123x456... and replace with _550x346.png
                    constructed_url = re.sub(r'_\d+x\d+.*$', '_550x346.png', constructed_url)
                    
                    extracted_image_url = constructed_url
            except Exception as e:
                print(f"  Error applying Emirates Islamic logic: {e}")

        # Add other bank logic here...

    except Exception as e:
        print(f"  Error extracting image: {e}")
        
    return extracted_image_url

def update_image_in_db(database_file, card_data, image_url):
    """Saves the found image URL to the database."""
    if not image_url:
        return

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
    INSERT INTO card_images (card_id, bank_name, card_name, scraper_image_url, scraper_date, card_url)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(card_id) DO UPDATE SET
        scraper_image_url = excluded.scraper_image_url,
        scraper_date = excluded.scraper_date,
        card_url = excluded.card_url;
    """
    cursor.execute(sql, (
        card_data['card_id'],
        card_data['bank_name'],
        card_data['card_name'],
        image_url,
        current_time,
        card_data['url']
    ))
    conn.commit()
    conn.close()
    print(f"  > Saved Image for: {card_data['card_name']}")

def run_image_updater():
    setup_image_table(db_file)
    cards = get_cards_needing_images(db_file)
    print(f"--- Starting Agent 3: Image Updater ---")
    print(f"Found {len(cards)} cards to check.")

    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for i, card in enumerate(cards):
            print(f"[{i+1}/{len(cards)}] Visiting: {card['card_name']} ({card['bank_name']})")
            try:
                driver.get(card['url'])
                # Quick wait
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except:
                    pass
                
                image_url = extract_image_url(driver, card['bank_name'], card['url'])
                
                if image_url:
                    # print(f"  Found: {image_url}")
                    update_image_in_db(db_file, card, image_url)
                else:
                    print("  x No image found.")
                    
            except Exception as e:
                print(f"  Error processing card: {e}")
                
    finally:
        driver.quit()
        print("--- Agent 3 Finished ---")

if __name__ == "__main__":
    run_image_updater()
