import sqlite3
import os

db_path = r'C:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Columns to add
new_columns = [
    ("foreign_currency_fee", "TEXT"),
    ("cashback_summary", "TEXT"),
    ("travel_points_summary", "TEXT"),
    ("special_discount_summary", "TEXT"),
    ("hotel_dining_offers", "TEXT"),
    ("golf_wellness", "TEXT")
]

print(f"Checking schema for 'credit_cards_details'...")
cursor.execute("PRAGMA table_info(credit_cards_details);")
existing_columns = [col[1] for col in cursor.fetchall()]

for col_name, col_type in new_columns:
    if col_name not in existing_columns:
        print(f"➕ Adding column: {col_name} ({col_type})")
        try:
            cursor.execute(f"ALTER TABLE credit_cards_details ADD COLUMN {col_name} {col_type}")
            print("   ✅ Done.")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"ℹ️ Column {col_name} already exists.")

conn.commit()
conn.close()
print("\n✅ Schema update completed.")
