import sqlite3
import os

db_path = r'c:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM card_images WHERE scraper_image_url IS NOT NULL AND scraper_image_url != ''")
    valid_count = cursor.fetchone()[0]

    print(f"Total Valid Images: {valid_count}")
    print("-" * 20)
    print("Valid Images per Bank:")

    cursor.execute("""
        SELECT bank_name, COUNT(*) 
        FROM card_images 
        WHERE scraper_image_url IS NOT NULL AND scraper_image_url != '' 
        GROUP BY bank_name
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]}")

except Exception as e:
    print(f"Error: {e}")

conn.close()
