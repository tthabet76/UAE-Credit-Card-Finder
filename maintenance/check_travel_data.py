import pandas as pd
import sqlite3

try:
    conn = sqlite3.connect('credit_card_data.db')
    df = pd.read_sql('SELECT travel_points_summary FROM credit_cards_details WHERE travel_points_summary IS NOT NULL AND travel_points_summary != "Not Mentioned" LIMIT 20', conn)
    print("Sample Travel Points Data:")
    print(df)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
