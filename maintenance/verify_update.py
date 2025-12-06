import sqlite3
import os

db_path = r'C:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Checking 'Adib Visa Cashback Card'...")
cursor.execute("SELECT card_name, cashback_summary, special_discount_summary, foreign_currency_fee FROM credit_cards_details WHERE card_name LIKE '%Adib Visa Cashback%'")
row = cursor.fetchone()

if row:
    print(f"Card: {row['card_name']}")
    print(f"Cashback Summary: {row['cashback_summary']}")
    print(f"Special Discount: {row['special_discount_summary']}")
    print(f"Foreign Fee: {row['foreign_currency_fee']}")
else:
    print("Card not found.")

conn.close()
