import os
import sys
import json
from update_cards_rest import load_master_context, process_card_data, chromedriver_path

# Mock Card Info (Same as before)
card_info = {
    'url': 'https://www.ajmanbank.ae/site/tariff-of-charges-retail.html', 
    'bank_name': 'Ajman Bank',
    'card_name': 'BRight World Test'
}

print(f"--- TESTING REST API FIX FOR {card_info['bank_name']} ---")

# Run Scraper using the REST-patched file
result = process_card_data(card_info, chromedriver_path)

if result['success']:
    print("\n--- SCRAPE SUCCESS ---")
    llm_data = result['llm_data']
    print(json.dumps(llm_data, indent=2))
    
    # Check for keywords from Tariff
    page_text = result.get('log_data', ["","","",""])[3] # Safe access
    if "=== SHARED BANK MASTER DOCUMENTS" in page_text:
        print("\n[PASS] Shared Master Context WAS injected into the prompt.")
    else:
        print("\n[FAIL] Shared Master Context was NOT injected.")
else:
    print(f"\n--- SCRAPE FAILED: {result.get('error')} ---")
    if result.get('log_data'):
        # Check if it was an LLM error specifically
        print(f"Details: {result['log_data'][4]}") # LLM response/error
