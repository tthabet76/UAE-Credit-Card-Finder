import sqlite3
import os

db_path = r'C:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("📊 Database Statistics:")

# 1. Total rows in log
cursor.execute("SELECT COUNT(*) FROM llm_interaction_log WHERE raw_page_text IS NOT NULL AND raw_page_text != ''")
total_log_rows = cursor.fetchone()[0]
print(f"  - Total entries in 'llm_interaction_log' (with text): {total_log_rows}")

# 2. Unique URLs in log
cursor.execute("SELECT COUNT(DISTINCT card_url) FROM llm_interaction_log WHERE raw_page_text IS NOT NULL AND raw_page_text != ''")
unique_log_urls = cursor.fetchone()[0]
print(f"  - Unique URLs in 'llm_interaction_log': {unique_log_urls}")

# 3. Active Inventory
cursor.execute("SELECT COUNT(*) FROM card_inventory WHERE is_active = 1")
active_inventory = cursor.fetchone()[0]
print(f"  - Active cards in 'card_inventory': {active_inventory}")

# 4. Total Details
cursor.execute("SELECT COUNT(*) FROM credit_cards_details")
total_details = cursor.fetchone()[0]
print(f"  - Total cards in 'credit_cards_details': {total_details}")

# Check for duplicates
if total_log_rows > unique_log_urls:
    print(f"\n⚠️ DUPLICATION DETECTED: {total_log_rows - unique_log_urls} redundant entries found.")
    print("   The reprocessing script is likely processing the same card multiple times (history).")
else:
    print("\n✅ No duplication found in logs.")

conn.close()
