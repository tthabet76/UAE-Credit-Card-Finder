import sqlite3
import pandas as pd

db_path = r'c:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- SIB Card Data Inspection ---")
try:
    # Check what we have for SIB
    query = "SELECT id, card_name, url FROM credit_cards_details WHERE bank_name LIKE '%SIB%' OR bank_name LIKE '%Sharjah Islamic%'"
    df = pd.read_sql_query(query, conn)
    print(df)
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
