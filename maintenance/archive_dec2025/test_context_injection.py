import os
import sys
import json
from update_cards import load_master_context, process_card_data, chromedriver_path

# Mock Card Info
card_info = {
    'url': 'https://www.ajmanbank.ae/site/tariff-of-charges-retail.html', 
    'bank_name': 'Ajman Bank',
    'card_name': 'BRight World Test'
}

print(f"--- TESTING CONTEXT INJECTION FOR {card_info['bank_name']} ---")

# Run Scraper
result = process_card_data(card_info, chromedriver_path)

if result['success']:
    print("\n--- SCRAPE SUCCESS ---")
    llm_data = result['llm_data']
    print(json.dumps(llm_data, indent=2))
    
    # Check for keywords from Tariff
    raw_response = result['log_data'][4]
    
    # We can also check the page_text in log_data[3] to see if context was injected
    page_text = result['log_data'][3]
    if "=== SHARED BANK MASTER DOCUMENTS" in page_text:
        print("\n[PASS] Shared Master Context WAS injected into the prompt.")
    else:
        print("\n[FAIL] Shared Master Context was NOT injected.")
else:
    print(f"\n--- SCRAPE FAILED: {result.get('error')} ---")
    if result.get('log_data'):
        page_text = result['log_data'][3]
        if "=== SHARED BANK MASTER DOCUMENTS" in page_text:
             print("\n[PARTIAL SUCCESS] Shared Master Context WAS injected into the prompt (despite LLM failure).")
             # Print a snippet
             start_idx = page_text.find("=== SHARED")
             print(f"Snippet: {page_text[start_idx:start_idx+200]}...")
        else:
             print("\n[FAIL] Shared Master Context was NOT injected.")
