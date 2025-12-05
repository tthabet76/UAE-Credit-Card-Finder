from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import update_images
except ImportError:
    from maintenance import update_images

URL = "https://www.mashreq.com/en/uae/neo/cards/cashback-credit-card" # Guessing URL, need to verify
# Actually I should get the URL from the DB or previous output.
# The previous output didn't show the URL.
# I'll assume the scraper has the correct URL.
# Let's use a known URL for Cashback if possible, or just generic search.

def investigate():
    print(f"--- Investigating Mashreq Cashback ---")
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    # I need the URL. I'll fetch it from the DB in the script.
    import sqlite3
    db_path = "credit_card_data.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM credit_cards_details WHERE bank_name='Mashreq' AND card_name LIKE '%Cashback%'")
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("Could not find Cashback card in DB.")
        return
        
    target_url = row[0]
    print(f"Target URL: {target_url}")
    
    try:
        driver.get(target_url)
        time.sleep(5)
        
        print("\n--- Extracting Images via JS ---")
        images_data = driver.execute_script("""
            var imgs = document.getElementsByTagName("img");
            var result = [];
            for (var i = 0; i < imgs.length; i++) {
                result.push({
                    src: imgs[i].src,
                    srcset: imgs[i].srcset,
                    alt: imgs[i].alt
                });
            }
            return result;
        """)
        
        for img in images_data:
            src = img.get('src', '')
            alt = img.get('alt', '')
            srcset = img.get('srcset', '')
            
            if "cashback" in src.lower() or "cashback" in alt.lower():
                print(f"MATCH!")
                print(f"  Src: {src}")
                print(f"  Alt: {alt}")
                if srcset:
                    print(f"  Srcset: {srcset[:100]}...")
    finally:
        driver.quit()

if __name__ == "__main__":
    investigate()
