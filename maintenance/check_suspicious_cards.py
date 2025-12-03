"""
Scans the database for cards with names like "Not Found" or "Not Mentioned" to identify scraping errors.
"""
import sqlite3

DB_PATH = r'C:\Users\cdf846\Documents\personal\Credit card project\credit_card_data.db'

def check_cards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking for suspicious card names...")
    cursor.execute("SELECT id, bank_name, card_name, url FROM card_inventory WHERE card_name LIKE '%Not Mentioned%' OR card_name = 'Not Found'")
    rows = cursor.fetchall()
    
    if not rows:
        print("No suspicious card names found.")
    else:
        print(f"Found {len(rows)} suspicious cards:")
        for r in rows:
            print(f"ID: {r[0]} | Bank: {r[1]} | Name: {r[2]} | URL: {r[3]}")

    conn.close()

if __name__ == "__main__":
    check_cards()
