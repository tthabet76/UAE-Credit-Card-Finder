import sqlite3
import pandas as pd
import os

db_path = os.path.join(os.getcwd(), 'credit_card_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Local Images
cursor.execute("SELECT COUNT(*) FROM card_images WHERE local_filename IS NOT NULL AND local_filename != ''")
local_count = cursor.fetchone()[0]

# 2. Links (Scraper or Manual URL) where NO local image
cursor.execute("SELECT COUNT(*) FROM card_images WHERE (local_filename IS NULL OR local_filename = '') AND (scraper_image_url IS NOT NULL OR manual_image_url IS NOT NULL)")
link_count = cursor.fetchone()[0]

# 3. Total
cursor.execute("SELECT COUNT(*) FROM card_images")
total_count = cursor.fetchone()[0]

print(f"Local Images: {local_count}")
print(f"Remote Links: {link_count}")
print(f"Total Rows: {total_count}")

# Breakdown
print("\nBreakdown by Bank:")
df = pd.read_sql_query("SELECT bank_name, SUM(CASE WHEN local_filename IS NOT NULL AND local_filename != '' THEN 1 ELSE 0 END) as local, SUM(CASE WHEN (local_filename IS NULL OR local_filename = '') AND scraper_image_url IS NOT NULL THEN 1 ELSE 0 END) as link FROM card_images GROUP BY bank_name", conn)
print(df.to_string())

conn.close()
