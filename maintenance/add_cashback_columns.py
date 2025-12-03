"""
[Run Once] Adds columns for max_cashback_rate, is_uncapped, etc., to the database.
"""
import sqlite3
import re

DB_PATH = r'C:\Users\cdf846\Documents\personal\Credit card project\credit_card_data.db'

def parse_cashback(text):
    """
    Parses cashback text to extract:
    - max_rate (float): Highest percentage found.
    - is_uncapped (bool): True if 'unlimited' or 'no cap' found.
    - cashback_type (str): 'Flat' or 'Variable'.
    """
    if not text or text in ["Not Mentioned", "Not Found", "-"]:
        return 0.0, False, 'Variable'

    text_lower = text.lower()
    
    # 1. Max Rate
    # Find all percentages (e.g. 5%, 1.5%)
    rates = re.findall(r'(\d+(?:\.\d+)?)%', text)
    max_rate = 0.0
    if rates:
        max_rate = max([float(r) for r in rates])
        
    # 2. Is Uncapped
    is_uncapped = False
    if 'unlimited' in text_lower or 'no cap' in text_lower:
        is_uncapped = True
        
    # 3. Cashback Type
    # Heuristic: If "flat" is mentioned OR only one rate is found and it's not clearly tiered
    cashback_type = 'Variable'
    if 'flat' in text_lower:
        cashback_type = 'Flat'
    elif len(set(rates)) == 1 and 'up to' not in text_lower:
        # If only one unique rate is mentioned (e.g. "1% on everything"), assume Flat
        cashback_type = 'Flat'
        
    return max_rate, is_uncapped, cashback_type

def migrate_cashback_columns():
    print("--- Adding and Populating Cashback Columns ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Add Columns (ignore if exists)
        columns_to_add = [
            ("max_cashback_rate", "REAL DEFAULT 0.0"),
            ("is_uncapped", "BOOLEAN DEFAULT 0"),
            ("cashback_type", "TEXT DEFAULT 'Variable'")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE credit_cards_details ADD COLUMN {col_name} {col_type}")
                print(f"Column '{col_name}' added.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"Column '{col_name}' already exists.")
                else:
                    raise e
        
        # 2. Fetch all rows
        cursor.execute("SELECT url, cashback_rates FROM credit_cards_details")
        rows = cursor.fetchall()
        print(f"Processing {len(rows)} records...")
        
        updated_count = 0
        for row in rows:
            url = row['url']
            raw_text = row['cashback_rates']
            
            max_rate, is_uncapped, cb_type = parse_cashback(raw_text)
            
            # Update the row
            cursor.execute("""
                UPDATE credit_cards_details 
                SET max_cashback_rate = ?, is_uncapped = ?, cashback_type = ? 
                WHERE url = ?
            """, (max_rate, is_uncapped, cb_type, url))
            updated_count += 1
            
        conn.commit()
        print(f"Successfully updated {updated_count} records.")
        
        # Verification
        print("\nSample Verification:")
        cursor.execute("SELECT cashback_rates, max_cashback_rate, is_uncapped, cashback_type FROM credit_cards_details LIMIT 5")
        for row in cursor.fetchall():
            print(f"  Text: {row[0][:50]}...")
            print(f"  -> Max: {row[1]}%, Uncapped: {row[2]}, Type: {row[3]}\n")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_cashback_columns()
