import sqlite3
import pandas as pd

db_path = 'maintenance/credit_card_data.db'

def check_counts():
    conn = sqlite3.connect(db_path)
    
    # Check if table exists
    try:
        query = "SELECT bank_name, COUNT(*) as count FROM card_images GROUP BY bank_name"
        df = pd.read_sql_query(query, conn)
        print("--- Images per Bank in 'card_images' ---")
        print(df)
        print("-" * 30)
        
        # Also check total cards per bank to see coverage
        query_total = "SELECT bank_name, COUNT(*) as total FROM credit_cards_details GROUP BY bank_name"
        df_total = pd.read_sql_query(query_total, conn)
        print("--- Total Cards per Bank ---")
        print(df_total)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_counts()
