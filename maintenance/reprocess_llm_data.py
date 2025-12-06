import sqlite3
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import toml
import threading

# --- CONFIGURATION ---
load_dotenv(override=True)
db_path = r'C:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

# Load API Key
secrets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app', '.streamlit', 'secrets.toml'))
LLM_API_KEY = None

if os.path.exists(secrets_path):
    try:
        data = toml.load(secrets_path)
        if "gemini" in data and "api_key" in data["gemini"]:
            LLM_API_KEY = data["gemini"]["api_key"]
        elif "GEMINI_API_KEY" in data:
            LLM_API_KEY = data["GEMINI_API_KEY"]
    except Exception as e:
        print(f"Error loading secrets.toml: {e}")

if not LLM_API_KEY:
    LLM_API_KEY = os.getenv("GEMINI_API_KEY")

if not LLM_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found.")
    exit()

genai.configure(api_key=LLM_API_KEY)

def extract_with_new_prompt(page_text_content):
    model = genai.GenerativeModel('models/gemini-flash-latest')
    
    # --- PROMPT ITERATION 4 ---
    prompt_text = f"""
You are an expert financial data analyst.
Your goal is to extract **comprehensive and detailed** credit card data from the website text.

**CRITICAL RULES:**
1.  **Do Not Summarize:** Keep details specific (e.g., "4 times/month" instead of just "Yes").
2.  **Missing Data:** If a value is not explicitly stated in the text, return "Not Mentioned".
3.  **Standardization:** For rewards, ALWAYS calculate the "Per 1 Unit" rate if possible (e.g., "2.5 points per 10 AED" -> "0.25 points/AED").

**DATA STRUCTURE TO EXTRACT:**

**1. Identity & Financials**
- "Card Name": Name of the card.
- "Bank Name": Issuing bank.
- "Annual Fee": Specific value or "Free for Life".
- "Minimum Salary": Monthly salary requirement.
- "Minimum Spend": Minimum spend to waive fees or earn bonuses.
- "Foreign Currency Fee": Look for "Foreign Transaction Fees" or "FX Fees". (CRITICAL: If 0%, state "0%").
- "Balance Transfer": Balance transfer offers (months, rate) and 0% Installment plans.

**2. The "Big 3" Benefit Buckets (For UI Sorting)**
*Classify the primary reward type here. If not applicable, return null.*
- "Cashback_Summary": (e.g., "5% on Fuel, 1% General") or null.
- "Travel_Points_Summary": (e.g., "0.25 Miles per AED") or null.
- "Special_Discount_Summary": (e.g., "Buy 1 Get 1 Cinema") or null.

**3. Detailed Benefits (The Rich Data)**
- "Welcome Bonus": Sign-up offers.
- "Lounge Access": Specifics (e.g., "Unlimited LoungeKey", "12 visits via DragonPass").
- "Hotel & Dining Offers": Specifics (e.g., "Discount at IHG", "Booking.com cashback", "Restaurants").
- "Travel Insurance": Travel inconvenience or medical insurance.
- "Airport Transfers": Limo or pick-up services.
- "Valet Parking": Locations and frequency.
- "Cinema Offers": Ticket offers.
- "Golf & Wellness": Golf, Spa, or Gym offers.
- "Purchase Protection": Warranty or theft protection.
- "Other Key Benefits": Any other major perks.

**Output Format:** Provide ONLY a valid, flat JSON object.
    ```json
    {{
      "Card Name": "...",
      "Bank Name": "...",
      "Annual Fee": "...",
      "Minimum Salary": "...",
      "Minimum Spend": "...",
      "Foreign Currency Fee": "...",
      "Balance Transfer": "...",
      "Cashback_Summary": "...",
      "Travel_Points_Summary": "...",
      "Special_Discount_Summary": "...",
      "Welcome Bonus": "...",
      "Lounge Access": "...",
      "Hotel & Dining Offers": "...",
      "Travel Insurance": "...",
      "Airport Transfers": "...",
      "Valet Parking": "...",
      "Cinema Offers": "...",
      "Golf & Wellness": "...",
      "Purchase Protection": "...",
      "Other Key Benefits": "..."
    }}
    ```
    ---
Webpage Text Content:
{page_text_content}
"""
    try:
        response = model.generate_content(prompt_text)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
    except Exception as e:
        print(f"  ⚠️ LLM Error: {e}")
        return None

def update_database(url, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql = """
    UPDATE credit_cards_details SET
        annual_fee = ?,
        minimum_salary_requirement = ?,
        minimum_spend_requirement = ?,
        balance_transfer_eligibility = ?,
        welcome_bonus = ?,
        
        foreign_currency_fee = ?,
        cashback_summary = ?,
        travel_points_summary = ?,
        special_discount_summary = ?,
        
        airport_lounge_access = ?,
        hotel_dining_offers = ?,
        travel_insurance = ?,
        airport_transfers = ?,
        valet_parking = ?,
        cinema_offers = ?,
        golf_wellness = ?,
        purchase_protection = ?,
        other_key_benefits = ?
    WHERE url = ?
    """
    
    try:
        cursor.execute(sql, (
            data.get("Annual Fee", "Not Mentioned"),
            data.get("Minimum Salary", "Not Mentioned"),
            data.get("Minimum Spend", "Not Mentioned"),
            data.get("Balance Transfer", "Not Mentioned"),
            data.get("Welcome Bonus", "Not Mentioned"),
            
            data.get("Foreign Currency Fee", "Not Mentioned"),
            data.get("Cashback_Summary", None),
            data.get("Travel_Points_Summary", None),
            data.get("Special_Discount_Summary", None),
            
            data.get("Lounge Access", "Not Mentioned"),
            data.get("Hotel & Dining Offers", "Not Mentioned"),
            data.get("Travel Insurance", "Not Mentioned"),
            data.get("Airport Transfers", "Not Mentioned"),
            data.get("Valet Parking", "Not Mentioned"),
            data.get("Cinema Offers", "Not Mentioned"),
            data.get("Golf & Wellness", "Not Mentioned"),
            data.get("Purchase Protection", "Not Mentioned"),
            data.get("Other Key Benefits", "Not Mentioned"),
            
            url
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"  ❌ DB Error: {e}")
        return False
    finally:
        conn.close()

def main():
    print("🚀 Starting Data Reprocessing...")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Fetch LATEST entry for each card (deduplication)
    # AND exclude cards that have already been processed (foreign_currency_fee IS NOT NULL)
    sql = """
    SELECT l.card_url, l.card_name, l.raw_page_text
    FROM llm_interaction_log l
    LEFT JOIN credit_cards_details d ON l.card_url = d.url
    WHERE l.id IN (
        SELECT MAX(id)
        FROM llm_interaction_log
        WHERE raw_page_text IS NOT NULL AND raw_page_text != ''
        GROUP BY card_url
    )
    AND (d.foreign_currency_fee IS NULL OR d.foreign_currency_fee = '')
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    
    total = len(rows)
    print(f"📊 Found {total} cards to process.")
    
    success_count = 0
    fail_count = 0
    
    for i, row in enumerate(rows):
        url = row['card_url']
        name = row['card_name']
        text = row['raw_page_text']
        
        print(f"\n[{i+1}/{total}] Processing: {name}")
        
        # Rate limiting
        time.sleep(2) 
        
        extracted_data = extract_with_new_prompt(text)
        
        if extracted_data:
            if update_database(url, extracted_data):
                print("  ✅ Updated successfully.")
                success_count += 1
            else:
                print("  ❌ Update failed.")
                fail_count += 1
        else:
            print("  ⚠️ Extraction failed.")
            fail_count += 1
            
    print("\n" + "="*40)
    print(f"🎉 Reprocessing Complete!")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print("="*40)

if __name__ == "__main__":
    main()
