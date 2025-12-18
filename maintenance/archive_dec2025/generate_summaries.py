import sqlite3
import os
import toml
from openai import OpenAI
import json
import time

# --- CONFIGURATION ---
DB_FILE = 'credit_card_data.db'
SECRETS_PATH = os.path.join('streamlit_app', '.streamlit', 'secrets.toml')



def load_openai_key():
    """Lengths to find the key in secrets.toml"""
    print(f"Loading secrets from {SECRETS_PATH}...")
    if not os.path.exists(SECRETS_PATH):
        raise FileNotFoundError(f"Secrets file not found at {SECRETS_PATH}")
    
    with open(SECRETS_PATH, 'r') as f:
        secrets = toml.load(f)
        
    # DEBUG: Print structure
    print(f"Found Root Keys: {list(secrets.keys())}")
    if 'openai' in secrets:
        print(f"Found [openai] Keys: {list(secrets['openai'].keys())}")
    
    # Check [openai] section first, then global, then [connections.openai]
    key = None
    if 'openai' in secrets:
        if 'OPENAI_API_KEY' in secrets['openai']:
            key = secrets['openai']['OPENAI_API_KEY']
        elif 'api_key' in secrets['openai']:
            key = secrets['openai']['api_key']
            
    if not key and 'OPENAI_API_KEY' in secrets:
        key = secrets['OPENAI_API_KEY']
    # Check case variations
    elif 'openai' in secrets and 'openai_api_key' in secrets['openai']:
         key = secrets['openai']['openai_api_key'] # Lowercase
    elif 'openai_api_key' in secrets:
         key = secrets['openai_api_key'] # Lowercase
    
    if not key:
        raise ValueError("OPENAI_API_KEY not found in secrets.toml")
    
    print("OpenAI Key loaded successfully.")
    return key

def generate_shoutout(client, card_name, raw_text):
    """Generates a summary using the Financial Analyst Agent prompt."""
    prompt = f"""
[SYSTEM INSTRUCTION]
You are a highly specialized Financial Analyst Agent. Your sole task is to analyze the provided raw HTML content of a single credit card product page and determine the card's primary value proposition. You must output a concise, actionable marketing summary of the card's 3-4 most important features. Your output MUST be in a strict JSON format.

## TASK GOAL
Identify and synthesize the 3-4 most unique and financially attractive selling points (differentiators) of the credit card described in the HTML content below.

## PRIORITIZATION RULES (Weighting Importance):
The final summary MUST prioritize features in this order, selecting the most prominent information for each category:

1.  **FINANCIAL VALUE (Top Priority):** The highest, most specific cashback percentage (e.g., 5% on Groceries) OR the maximum point multiplier (e.g., 10x Miles).
2.  **PREMIUM ACCESS (Second Priority):** Any "Unlimited" or high-tier privileges (e.g., Unlimited golf, Unlimited airport lounge access, Free Valet Parking).
3.  **CORE COST/BONUS:** The Annual Fee status (e.g., Free for Life, AED 0) OR the largest Welcome Bonus value (e.g., AED 1,500 bonus).
4.  **UNIQUE CO-BRAND/SERVICE:** Any unique partnership (e.g., Etihad Guest, noon, LuLu, Careem) or specialized feature (e.g., 0% Forex Fee).

## SYNTHESIS CONSTRAINTS
1.  The output for "Differentiator Summary" must be concise and easily readable for a customer (maximum 3 lines, sentence format).
2.  If the Annual Fee is non-zero, include it in the summary sentence (e.g., "...with an annual fee of AED 95.").
3.  The LLM must successfully find and output ALL fields defined in the JSON schema below, using "Not Found" if a required item is genuinely missing.

---
[INPUT DATA]

Webpage Content:
{raw_text[:8000]} (Truncated to fit context)

---
[OUTPUT FORMAT CONTRACT]

Provide the extracted data as a single JSON object (DO NOT use markdown delimiters like ```json):

{{
    "Card Name": "The official product name (e.g., FAB Elite Credit Card)",
    "Annual Fee": "The annual fee amount or status (e.g., Free for Life, AED 1,500 + VAT)",
    "Differentiator Summary": "Synthesized 2-3 line summary based on PRIORITIZATION RULES, suitable for a headline.",
    "Minimum Salary": "The required monthly income (e.g., AED 5,000)",
    "Key Perks List": [
        "Major perk 1 (e.g., 10% Cashback on dining)",
        "Major perk 2 (e.g., Complimentary airport lounge access)"
    ]
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst agent. Output JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        
        # We only return the summary for now to fit the existing db column
        return data.get("Differentiator Summary")
    except Exception as e:
        print(f"  OpenAI Error: {e}")
        return None

def main():
    try:
        api_key = load_openai_key()
        
        # SSL Bypass Configuration
        import httpx
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get cards that need summaries (or all active cards)
        # We join details with log to get raw text
        print("Fetching cards...")
        sql = """
        SELECT d.url, d.card_name, d.ai_summary, l.raw_page_text
        FROM credit_cards_details d
        JOIN llm_interaction_log l ON d.url = l.card_url
        WHERE d.ai_summary IS NULL OR d.ai_summary = '';
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} cards needing summaries.")
        
        print(f"Found {len(rows)} cards needing summaries.")
        
        # FULL RUN
        print(f"Starting generation for all {len(rows)} cards...")

        for row in rows:
            card_name = row['card_name']
            raw_text = row['raw_page_text']
            
            if not raw_text:
                print(f"Skipping {card_name} (No raw text available).")
                continue
                
            print(f"Generating summary for: {card_name}...")
            if "gpt-4o" in  str(client): time.sleep(1) # Rate limit safety
            
            summary = generate_shoutout(client, card_name, raw_text)
            
            if summary:
                # Update DB
                update_sql = "UPDATE credit_cards_details SET ai_summary = ? WHERE url = ?"
                cursor.execute(update_sql, (summary, row['url']))
                conn.commit()
                print(f"  > Saved summary for {card_name}")
            else:
                print(f"  > Failed to generate summary for {card_name}")
                
        conn.close()
        print("Done.")
        
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
