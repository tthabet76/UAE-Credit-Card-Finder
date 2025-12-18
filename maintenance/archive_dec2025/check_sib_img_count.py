import sqlite3
import os

db_path = r'c:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT scraper_image_url FROM card_images WHERE bank_name LIKE '%SIB%' OR bank_name LIKE '%Sharjah Islamic%'")
    rows = cursor.fetchall()
    print(f"SIB Images Found: {len(rows)}")
    for row in rows:
        print(f"  {row[0]}")
except Exception as e:
    print(e)
conn.close()
