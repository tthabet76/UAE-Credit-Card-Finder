import sqlite3
import pandas as pd

db_path = r'c:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get samples for a few "Generic" banks
banks = ['ADIB', 'Citi', 'HSBC', 'FAB']
print("--- Sample Image URLs ---")
for bank in banks:
    print(f"\nBank: {bank}")
    # Note: DB might store 'Citibank' instead of 'Citi'
    cursor.execute(f"SELECT card_name, scraper_image_url FROM card_images WHERE bank_name LIKE '%{bank}%' LIMIT 3")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]}: {row[1]}")

conn.close()
