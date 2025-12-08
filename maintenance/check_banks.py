import sqlite3

def check_banks():
    try:
        conn = sqlite3.connect('credit_card_data.db')
        c = conn.cursor()
        
        # Check specific problematic banks
        c.execute("SELECT DISTINCT bank_name FROM credit_cards_details WHERE bank_name LIKE '%Emirates%' OR bank_name LIKE '%NBD%' OR bank_name LIKE '%HSBC%'")
        rows = c.fetchall()
        
        print(f"Found {len(rows)} distinct matching bank names:")
        for row in rows:
            name = row[0]
            print(f"'{name}' (Length: {len(name)})")
            
            # Print char codes to be sure
            codes = [str(ord(c)) for c in name]
            print(f"   Codes: {', '.join(codes)}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_banks()
