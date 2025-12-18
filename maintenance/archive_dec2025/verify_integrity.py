import os
from supabase import create_client, Client
import toml

try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_data():
    print("--- Verifying Data Integrity ---")
    
    print("Fetching all Cards...")
    cards = supabase.table("credit_cards_details").select("id, bank_name, card_name").execute().data
    
    print("Fetching all Images...")
    images = supabase.table("card_images").select("card_id, bank_name, card_name, image_url").execute().data
    
    cards_map = {str(c['id']): c for c in cards}
    
    mismatches = []
    missing_links = []
    
    for img in images:
        c_id = str(img['card_id'])
        if c_id not in cards_map:
            missing_links.append(f"Image ID {c_id} has no Parent Card!")
            continue
            
        parent = cards_map[c_id]
        
        name_match = (img['card_name'] == parent['card_name'])
        bank_match = (img['bank_name'] == parent['bank_name'])
        
        if not name_match or not bank_match:
            mismatches.append({
                "id": c_id,
                "img_bank": img['bank_name'],
                "parent_bank": parent['bank_name'],
                "img_name": img['card_name'],
                "parent_name": parent['card_name']
            })

    print(f"\n[Results]")
    print(f"Total Parent Cards: {len(cards)}")
    print(f"Total Image Records: {len(images)}")
    
    if len(cards) == len(images):
        print("[OK] Counts Match Perfectly (212 vs 212)")
    else:
        print(f"[!] Count Mismatch! ({len(cards)} vs {len(images)})")
        
    if not missing_links:
        print("[OK] All Images link to a Parent Card")
    else:
        print(f"[X] Found {len(missing_links)} Orphan Images:")
        for m in missing_links: print(f"  - {m}")
        
    if not mismatches:
        print("[OK] All Bank Names and Card Names match perfectly!")
    else:
        print(f"[X] Found {len(mismatches)} Name Discrepancies:")
        for m in mismatches:
            print(f"  ID {m['id']}:")
            print(f"    Bank: '{m['img_bank']}' vs '{m['parent_bank']}'")
            print(f"    Name: '{m['img_name']}' vs '{m['parent_name']}'")

if __name__ == "__main__":
    verify_data()
