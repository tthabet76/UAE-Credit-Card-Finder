import sqlite3
import pandas as pd
import os

DB_FILE = 'credit_card_data.db'

def generate_report():
    print("--- Pre-Migration Data Health Check ---\n")
    conn = sqlite3.connect(DB_FILE)
    
    # Load all data
    cards_df = pd.read_sql_query("SELECT * FROM credit_cards_details", conn)
    images_df = pd.read_sql_query("SELECT * FROM card_images", conn)
    conn.close()
    
    # Ensure types match for merge
    cards_df['id'] = cards_df['id'].astype(int)
    # card_images 'card_id' might be mingled types, force to int
    images_df['card_id'] = pd.to_numeric(images_df['card_id'], errors='coerce').fillna(0).astype(int)

    # Merge
    merged = pd.merge(cards_df, images_df, left_on='id', right_on='card_id', how='left')
    
    # Stats
    total_cards = len(cards_df)
    ready_images = len(merged[merged['local_filename'].notnull()])
    
    print(f"Total Cards: {total_cards}")
    print(f"Cards with Local Images Ready: {ready_images}")
    
    print("\n[Breakdown by Bank (Images Ready)]")
    # Count how many images per bank
    ready_df = merged[merged['local_filename'].notnull()]
    print(ready_df['bank_name_x'].value_counts().to_string())
    
    print("\n[Sample: 5 Ready-to-Migrate Cards]")
    sample = ready_df.head(5)
    for _, row in sample.iterrows():
        print(f"  [OK] Card {row['id_x']}: {row['bank_name_x']} - {row['card_name_x']}")
        print(f"       File: {row['local_filename']}")

if __name__ == "__main__":
    generate_report()
