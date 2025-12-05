import sys
import os
import random
import sqlite3
import json
import time

# Ensure we can import from the current directory if running from maintenance/
# or from maintenance/ if running from root.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Helper to write to results file
RESULTS_FILE = "test_results.txt"

def log_result(header, content):
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*20}\n{header}\n{'='*20}\n")
        if isinstance(content, (dict, list)):
            f.write(json.dumps(content, indent=2))
        else:
            f.write(str(content))
        f.write("\n")
    print(f"Logged: {header}")

def test_agent_1():
    print("\n--- Testing Agent 1 (Discovery) ---")
    try:
        import update_banks
        
        # Pick random bank
        bank_name, url = random.choice(list(update_banks.bank_listing_urls.items()))
        print(f"Selected Bank: {bank_name}")
        
        # Run discovery
        found_cards = update_banks.discover_cards_from_listing(bank_name, url)
        
        log_result(f"AGENT 1 TEST: {bank_name}", found_cards)
        return found_cards
    except Exception as e:
        log_result("AGENT 1 ERROR", str(e))
        print(f"Error: {e}")

def test_agent_2():
    print("\n--- Testing Agent 2 (Details) ---")
    try:
        import update_cards
        
        # Get random card from DB
        conn = sqlite3.connect('credit_card_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM card_inventory WHERE is_active=1 ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("No active cards found in DB.")
            return

        card_info = dict(row)
        print(f"Selected Card: {card_info['card_name']}")
        
        # Run processing
        result = update_cards.process_card_data(card_info, update_cards.chromedriver_path)
        
        log_result(f"AGENT 2 TEST: {card_info['card_name']}", result)
        return card_info # Return for Agent 3 to use
    except Exception as e:
        log_result("AGENT 2 ERROR", str(e))
        print(f"Error: {e}")

def test_agent_3(card_info=None):
    print("\n--- Testing Agent 3 (Images) ---")
    try:
        import update_images
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        if not card_info:
             # Get random card from DB
            conn = sqlite3.connect('credit_card_data.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM card_inventory WHERE is_active=1 ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            card_info = dict(row)

        print(f"Selected Card: {card_info['card_name']}")
        
        # Setup Driver
        service = Service(executable_path=update_images.chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(card_info['url'])
            time.sleep(2)
            image_url = update_images.extract_image_url(driver, card_info['bank_name'], card_info['url'])
            log_result(f"AGENT 3 TEST: {card_info['card_name']}", f"Image URL: {image_url}")
        finally:
            driver.quit()
            
    except Exception as e:
        log_result("AGENT 3 ERROR", str(e))
        print(f"Error: {e}")

if __name__ == "__main__":
    # Clear previous results
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("TEST SUITE RESULTS\n")
        
    test_agent_1()
    card_used = test_agent_2()
    test_agent_3(card_used) # Try to use the same card if possible, or random
    
    print(f"\nDone! Check {RESULTS_FILE} for details.")
