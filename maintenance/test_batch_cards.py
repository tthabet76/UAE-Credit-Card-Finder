"""
Runs the full scraping process on 5 cards to test the scraper.
"""
import sqlite3
import sys
import os
import io

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from update_cards import process_card_data, chromedriver_path, db_file, setup_database, update_card_in_database

# Setup DB
setup_database(db_file)

# Fetch 5 cards
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT url, bank_name, card_name FROM card_inventory WHERE is_active = 1 LIMIT 5")
rows = cursor.fetchall()
conn.close()

if not rows:
    print("No active cards found in database to test.")
    exit()

cards = [dict(row) for row in rows]

print(f"Testing with {len(cards)} cards...\n")

results_summary = []

for card in cards:
    print(f"--- Processing: {card['card_name']} ({card['bank_name']}) ---")
    
    # Run process
    result = process_card_data(card, chromedriver_path)
    
    image_url = "Not Found"
    if result['success']:
        update_card_in_database(db_file, result, card)
        extracted_img = result.get('extracted_image_url')
        if extracted_img:
            image_url = extracted_img
        print(f"  ✅ Success. Image: {image_url}")
    else:
        print(f"  ❌ Failed: {result.get('error')}")
    
    results_summary.append({
        "Bank": card['bank_name'],
        "Card": card['card_name'],
        "Image URL": image_url
    })
    print("-" * 30)

print("\n\n=== BATCH TEST RESULTS ===")
for item in results_summary:
    print(f"Bank: {item['Bank']}")
    print(f"Card: {item['Card']}")
    print(f"Image: {item['Image URL']}")
    print("")
