import sqlite3
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import update_images
except ImportError:
    # If running from root
    from maintenance import update_images

# CONFIG
TARGET_BANK = "Mashreq"
REPORT_FILE = "bank_image_report.txt"

def run_test():
    print(f"--- Testing Images for: {TARGET_BANK} ---")
    
    # 1. Get Cards (Join with details to get stable card_id)
    conn = sqlite3.connect('credit_card_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = """
    SELECT d.id as card_id, i.url, i.bank_name, i.card_name
    FROM card_inventory i
    JOIN credit_cards_details d ON i.url = d.url
    WHERE i.is_active=1 AND i.bank_name=?
    """
    cursor.execute(sql, (TARGET_BANK,))
    cards = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not cards:
        print(f"No active cards found for {TARGET_BANK}")
        return

    print(f"Found {len(cards)} cards.")

    # 2. Setup Driver
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(service=service, options=options)

    # 3. Process & Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"IMAGE EXTRACTION REPORT: {TARGET_BANK}\n")
        f.write("==================================================\n\n")
        
        for i, card in enumerate(cards):
            print(f"[{i+1}/{len(cards)}] Checking: {card['card_name']}")
            try:
                driver.get(card['url'])
                driver.implicitly_wait(5) 
                
                image_url = update_images.extract_image_url(driver, card['bank_name'], card['url'], card['card_name'])
                
                # Update DB
                update_images.update_image_in_db('credit_card_data.db', card, image_url)
                
                f.write(f"Card: {card['card_name']}\n")
                f.write(f"URL:  {card['url']}\n")
                f.write(f"Image: {image_url}\n")
                f.write("-" * 50 + "\n")
                
            except Exception as e:
                print(f"  Error: {e}")
                f.write(f"Card: {card['card_name']}\n")
                f.write(f"Error: {e}\n")
                f.write("-" * 50 + "\n")

    driver.quit()
    print(f"\nDone! Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    run_test()
