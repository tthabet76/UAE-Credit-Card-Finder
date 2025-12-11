import sys
import os

# Add maintenance to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from update_images import db_file, setup_image_table, get_cards_needing_images, chromedriver_path, extract_image_url, update_image_in_db
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_sib_update():
    print("--- Targeted Update: SIB ---")
    cards = get_cards_needing_images(db_file)
    
    # Filter for SIB only
    sib_cards = [c for c in cards if 'SIB' in c['bank_name'] or 'Sharjah Islamic' in c['bank_name']]
    print(f"Found {len(sib_cards)} SIB cards.")

    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        for i, card in enumerate(sib_cards):
            print(f"[{i+1}/{len(sib_cards)}] {card['card_name']}")
            try:
                driver.get(card['url'])
                # Wait for body
                try: 
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "exclusive-bg")))
                except: 
                    pass

                image_url = extract_image_url(driver, card['bank_name'], card['url'], card['card_name'])
                
                if image_url:
                    print(f"  > Found: {image_url}")
                    update_image_in_db(db_file, card, image_url)
                else:
                    print("  x Failed.")
            except Exception as e:
                print(f"  Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_sib_update()
