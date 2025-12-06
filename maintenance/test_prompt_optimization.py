import time
import json
import os
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import toml

# --- CONFIGURATION ---
load_dotenv(override=True)

# Path to ChromeDriver (Hardcoded as per update_cards.py)
chromedriver_path = 'C:/Users/cdf846/Documents/personal/Credit card project/chromedriver.exe'

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

# --- TARGET URL ---
target_url = "https://www.ajmanbank.ae/site/bright-platinum.html"

def get_page_text(url):
    print(f"🌐 Fetching content from: {url}")
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        page_text = driver.find_element(By.TAG_NAME, 'body').text
        return page_text
    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        return None
    finally:
        driver.quit()

def extract_with_new_prompt(page_text_content):
    print("🤖 Sending text to Gemini with NEW prompt...")
    model = genai.GenerativeModel('models/gemini-flash-latest')
    
    # --- USER PROVIDED PROMPT (ITERATION 4) ---
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
    # ----------------------------

    try:
        response = model.generate_content(prompt_text)
        raw_text = response.text.strip()
        
        # Clean markdown
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return raw_text.strip()
    except Exception as e:
        return f"Error: {e}"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    text_content = get_page_text(target_url)
    if text_content:
        # print(f"📄 Extracted {len(text_content)} characters.")
        json_output = extract_with_new_prompt(text_content)
        
        # Write to file with UTF-8 encoding
        with open("llm_output.json", "w", encoding="utf-8") as f:
            f.write(json_output)
            
        print("\n✅ Output written to llm_output.json")
