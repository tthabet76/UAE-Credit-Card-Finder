"""
Runs the full scraping process on a *single* card to test if the scraper is working, without waiting for all cards.
"""
import sqlite3
import sys
import os

# Ensure we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from update_cards import process_card_data, chromedriver_path, db_file, setup_database, update_card_in_database

# Setup DB
setup_database(db_file)

# Fetch one card
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT url, bank_name, card_name FROM card_inventory WHERE card_name LIKE '%Skywards Black%' LIMIT 1")
row = cursor.fetchone()

if not row:
    print("No active cards found in database to test.")
    exit()

card = dict(row)
conn.close()

print(f"Testing with card: {card['card_name']}")

# Run process
result = process_card_data(card, chromedriver_path)
print("Result:", result)

if result['success']:
    print("✅ Scraping successful. Saving to database...")
    update_card_in_database(db_file, result, card)
    print("✅ Database updated.")
else:
    print("❌ Scraping failed.")
