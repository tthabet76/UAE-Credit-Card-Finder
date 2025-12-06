import sqlite3
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import toml

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

def get_random_card_with_text():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get a card that has raw text
    cursor.execute("SELECT card_url, card_name, raw_page_text FROM llm_interaction_log WHERE raw_page_text IS NOT NULL AND raw_page_text != '' ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    
    current_data = None
    if row:
        # Get current details for comparison
        cursor.execute("SELECT * FROM credit_cards_details WHERE url = ?", (row['card_url'],))
        current_data = cursor.fetchone()
        
    conn.close()
    return dict(row) if row else None, dict(current_data) if current_data else None

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
        return {"error": str(e)}

if __name__ == "__main__":
    print("🎲 Selecting a random card with stored text...")
    log_data, current_db_data = get_random_card_with_text()
    
    if not log_data:
        print("❌ No data found in llm_interaction_log.")
        exit()
        
    print(f"\n💳 Selected Card: {log_data['card_name']}")
    print(f"🔗 URL: {log_data['card_url']}")
    
    print("\n🤖 Running New Prompt on Stored Text...")
    new_data = extract_with_new_prompt(log_data['raw_page_text'])
    
    print("\n" + "="*60)
    print(f"COMPARISON FOR: {log_data['card_name']}")
    print("="*60)
    
    # Fields to compare
    comparison_fields = [
        ("Annual Fee", "annual_fee", "Annual Fee"),
        ("Min Salary", "minimum_salary_requirement", "Minimum Salary"),
        ("Welcome Bonus", "welcome_bonus", "Welcome Bonus"),
        ("Valet Parking", "valet_parking", "Valet Parking"),
        ("Foreign Fee", None, "Foreign Currency Fee"), # New field
        ("Cashback Summary", None, "Cashback_Summary"), # New field
        ("Travel Summary", None, "Travel_Points_Summary"), # New field
        ("Dining Offers", "dining_discounts", "Hotel & Dining Offers"), # Merged field
    ]
    
    for label, db_col, json_key in comparison_fields:
        old_val = str(current_db_data.get(db_col, "N/A")) if db_col and current_db_data else "N/A"
        new_val = str(new_data.get(json_key, "N/A"))
        
        # Truncate for display
        old_val = (old_val[:50] + '..') if len(old_val) > 50 else old_val
        new_val = (new_val[:50] + '..') if len(new_val) > 50 else new_val
        
        print(f"\n🔹 {label}:")
        print(f"   OLD: {old_val}")
        print(f"   NEW: {new_val}")
        
    print("\n" + "="*60)
    
    # Save full output for inspection
    with open("comparison_output.json", "w", encoding="utf-8") as f:
        json.dump({"old": dict(current_db_data) if current_db_data else {}, "new": new_data}, f, indent=2)
    print("✅ Full comparison saved to comparison_output.json")
