"""
Normalizes bank names (e.g., changing "Rakbank" to "RAKBANK") to ensure consistency.
"""
import sqlite3

db_file = 'credit_card_data.db'

def fix_names():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    updates = [
        ("DIB", "%Dubai Islamic Bank%"),
        ("FAB", "%First Abu Dhabi Bank%"),
        ("CBD", "%Commercial Bank of Dubai%"),
        ("ADIB", "%Abu Dhabi Islamic Bank%"),
        ("CBI", "%Commercial Bank International%"),
        ("NBF", "%National Bank of Fujairah%"),
        ("UAB", "%United Arab Bank%"),
        ("Mashreq", "%Mashreq Bank%"),
        ("Emirates Islamic", "%Emirates Islamic Bank%"),
        ("Standard Chartered", "%Standard Chartered Bank%"),
        ("HSBC", "%HSBC UAE%"),
        ("Citibank", "%Citibank UAE%"),
        ("American Express", "%American Express UAE%"),
        ("ADCB Islamic", "%ADCB Islamic / simplylife%")
    ]
    
    print("Updating card_inventory...")
    for new_name, old_pattern in updates:
        cursor.execute("UPDATE card_inventory SET bank_name = ? WHERE bank_name LIKE ?", (new_name, old_pattern))
        print(f"  Updated {old_pattern} -> {new_name}: {cursor.rowcount} rows")

    print("\nUpdating credit_cards_details...")
    # Check if table exists first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credit_cards_details'")
    if cursor.fetchone():
        for new_name, old_pattern in updates:
            cursor.execute("UPDATE credit_cards_details SET bank_name = ? WHERE bank_name LIKE ?", (new_name, old_pattern))
            print(f"  Updated {old_pattern} -> {new_name}: {cursor.rowcount} rows")
    else:
        print("  Table 'credit_cards_details' does not exist yet.")

    conn.commit()
    conn.close()
    print("\nDatabase update complete.")

if __name__ == "__main__":
    fix_names()
