import sqlite3
import pandas as pd

DB_FILE = 'credit_card_data.db'

def show_progress():
    conn = sqlite3.connect(DB_FILE)
    
    # Query for completed banks
    sql = """
    SELECT bank_name, card_name, scraper_image_url
    FROM card_images
    WHERE bank_name IN ('Emirates Islamic', 'RAKBANK', 'Mashreq')
    ORDER BY bank_name, card_name
    """
    
    df = pd.read_sql_query(sql, conn)
    conn.close()
    
    if df.empty:
        print("No data found for Emirates Islamic or RAKBANK.")
    else:
        # Simple print
        print(f"{'Bank Name':<20} | {'Card Name':<40}")
        print("-" * 100)
        for index, row in df.iterrows():
            url = row['scraper_image_url']
            print(f"{row['bank_name']:<20} | {row['card_name']:<40}")
            print(f"URL: {url}")
            print("-" * 50)

if __name__ == "__main__":
    show_progress()
