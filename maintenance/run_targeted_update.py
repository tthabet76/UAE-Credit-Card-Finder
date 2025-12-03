"""
Allows you to force an update for a specific list of URLs or banks.
"""
import sqlite3
import time
import concurrent.futures
import os
import update_banks # Import module to patch db_file

# Absolute path to DB
DB_PATH = r'C:\Users\cdf846\Documents\personal\Credit card project\credit_card_data.db'
update_banks.db_file = DB_PATH # Patch the module variable

from update_banks import (
    discover_cards_from_listing, 
    update_database_with_cards, 
    bank_listing_urls
)

TARGET_BANKS = ["Emirates Islamic", "NBQ", "RAKBANK", "SIB", "Standard Chartered"]

def mark_specific_banks_inactive(banks):
    """Sets is_active=0 only for the specified banks."""
    print(f"--- Soft Resetting Inactive Status for: {', '.join(banks)} ---")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        placeholders = ', '.join(['?'] * len(banks))
        sql = f"UPDATE card_inventory SET is_active = 0 WHERE bank_name IN ({placeholders})"
        cursor.execute(sql, banks)
        conn.commit()
        print(f"  > Cards for target banks marked as inactive. They will be reactivated if found.")
    except Exception as e:
        print(f"  Error marking cards inactive: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # 1. Soft Reset Target Banks
    mark_specific_banks_inactive(TARGET_BANKS)
    
    start_time = time.time()
    
    # 2. Filter URLs
    target_urls = {bank: url for bank, url in bank_listing_urls.items() if bank in TARGET_BANKS}
    
    print(f"\n--- Starting Targeted Discovery for {len(target_urls)} Banks ---")
    
    run_summary = []
    total_cards_found = 0

    # 3. Run Parallel Discovery
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_bank = {executor.submit(discover_cards_from_listing, bank, url): bank for bank, url in target_urls.items()}
        
        for future in concurrent.futures.as_completed(future_to_bank):
            bank_name = future_to_bank[future]
            try:
                result = future.result()
                run_summary.append(result)
                
                if result['cards']:
                    update_database_with_cards(bank_name, result['cards'])
                    print(f"  > {bank_name}: Found {result['card_count']} cards ({result['method']})")
                else:
                    print(f"  > {bank_name}: No cards found.")
                    
                total_cards_found += result['card_count']
                
            except Exception as exc:
                print(f"  > {bank_name} generated an exception: {exc}")

    end_time = time.time()
    total_time = end_time - start_time

    print("\n\n--- TARGETED RUN SUMMARY ---")
    print("===================================")
    for report in run_summary:
        print(f"- {report['bank_name']}: Found {report['card_count']} cards (Method: {report['method']})")
    print("===================================")
    print(f"Total Cards Found: {total_cards_found}")
    print(f"Total Run Time: {total_time:.2f} seconds")
