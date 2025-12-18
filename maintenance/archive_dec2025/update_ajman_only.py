import os
import sqlite3
import time
import concurrent.futures
from update_cards_rest import (
    setup_database, 
    get_cards_from_inventory, 
    process_card_data, 
    update_card_in_database, 
    db_file, 
    chromedriver_path,
    log_llm_interaction
)

def run_ajman_update():
    print("--- STARTING TARGETED UPDATE: AJMAN BANK ONLY ---")
    setup_database(db_file)
    
    all_cards = get_cards_from_inventory(db_file)
    # Filter for Ajman Bank
    ajman_cards = [c for c in all_cards if "Ajman" in c['bank_name']]
    
    if not ajman_cards:
        print("No Ajman Bank cards found in inventory!")
        return

    print(f"Found {len(ajman_cards)} Ajman Bank cards to update.")
    
    # Run sequentially or parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_card = {executor.submit(process_card_data, card, chromedriver_path): card for card in ajman_cards}
        
        for future in concurrent.futures.as_completed(future_to_card):
            card_info = future_to_card[future]
            try:
                result = future.result()
                if result.get('log_data'):
                    log_llm_interaction(db_file, *result['log_data'])
                
                if result['success']:
                    update_card_in_database(db_file, result, card_info)
                    print(f"[SUCCESS] Updated: {card_info['card_name']}")
                else:
                    print(f"[FAILED] {card_info['card_name']} - Error: {result.get('error')}")
            except Exception as exc:
                print(f"[EXCEPTION] {card_info['card_name']}: {exc}")

    print("--- AJMAN BANK UPDATE COMPLETE ---")

if __name__ == "__main__":
    run_ajman_update()
