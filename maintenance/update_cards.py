"""
[CRITICAL] The main "Scraper". It visits the specific page of each card to extract fees, interest rates, and benefits.
"""
# --- IMPORTS ---
import time
import re
import json
import os
import datetime
import sqlite3
import random
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urljoin
import google.generativeai as genai
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATION SECTION ---
from dotenv import load_dotenv
import toml

load_dotenv(override=True)

chromedriver_path = 'C:/Users/cdf846/Documents/personal/Credit card project/chromedriver.exe'
db_file = 'credit_card_data.db'

# Try loading from secrets.toml first
secrets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app', '.streamlit', 'secrets.toml'))
print(f"DEBUG: Looking for secrets at: {secrets_path}")
LLM_API_KEY = None

if os.path.exists(secrets_path):
    try:
        data = toml.load(secrets_path)
        if "gemini" in data and "api_key" in data["gemini"]:
            LLM_API_KEY = data["gemini"]["api_key"]
            print("DEBUG: Found api_key in [gemini] section of secrets.toml")
        elif "GEMINI_API_KEY" in data:
            LLM_API_KEY = data["GEMINI_API_KEY"]
        elif "connections" in data and "gemini" in data["connections"]:
             LLM_API_KEY = data["connections"]["gemini"].get("api_key")
        elif "openai" in data and "GEMINI_API_KEY" in data["openai"]:
             LLM_API_KEY = data["openai"]["GEMINI_API_KEY"]
    except Exception as e:
        print(f"Error loading secrets.toml: {e}")
else:
    print("DEBUG: secrets.toml not found at path.")

# Fallback to environment variable
if not LLM_API_KEY:
    LLM_API_KEY = os.getenv("GEMINI_API_KEY")
    if LLM_API_KEY:
        print("DEBUG: Found GEMINI_API_KEY in environment variables")

if not LLM_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in secrets.toml or environment variables.")
else:
    print(f"DEBUG: API Key loaded (Length: {len(LLM_API_KEY)})")

genai.configure(api_key=LLM_API_KEY)

# --- AGENT BEHAVIOR CONFIGURATION ---
PAGE_LOAD_DELAY = 5  # Reduced for faster page processing
MAX_RETRIES_PER_URL = 2
MAX_CONSECUTIVE_FAILURES = 5
CACHE_VALIDITY_DAYS = 7 # Skip cards updated within this many days

# --- DATABASE SETUP FUNCTION ---
def setup_database(database_file):
    """Connects to the DB and ensures all necessary tables exist."""
    conn = None
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        print(f"Successfully connected to database: {database_file}")

        # Create the detailed credit card table
        create_details_table_sql = """
        CREATE TABLE IF NOT EXISTS credit_cards_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE NOT NULL, bank_name TEXT, card_name TEXT,
            minimum_salary_requirement TEXT, annual_fee TEXT, minimum_spend_requirement TEXT,
            balance_transfer_eligibility TEXT, welcome_bonus TEXT, cashback_rates TEXT,
            points_earning_rates TEXT, cobrand_rewards TEXT, airport_lounge_access TEXT,
            travel_insurance TEXT, airport_transfers TEXT, hotel_discounts TEXT, cinema_offers TEXT,
            dining_discounts TEXT, golf_privileges TEXT, valet_parking TEXT, purchase_protection TEXT,
            extended_warranty TEXT, other_key_benefits TEXT, last_updated TEXT NOT NULL
        );
        """
        cursor.execute(create_details_table_sql)
        print("Table 'credit_cards_details' is ready.")

        # Create the run summary table
        create_summary_table_sql = """
        CREATE TABLE IF NOT EXISTS run_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_timestamp TEXT NOT NULL,
            total_urls_in_inventory INTEGER,
            urls_processed INTEGER,
            successful_extractions INTEGER,
            failed_urls INTEGER,
            total_retries INTEGER
        );
        """
        cursor.execute(create_summary_table_sql)
        print("Table 'run_summary' is ready.")

        # Create the LLM interaction log table for auditing
        create_log_table_sql = """
        CREATE TABLE IF NOT EXISTS llm_interaction_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_url TEXT NOT NULL,
            bank_name TEXT,
            card_name TEXT,
            run_timestamp TEXT NOT NULL,
            raw_page_text TEXT,
            llm_response_json TEXT,
            status TEXT
        );
        """
        cursor.execute(create_log_table_sql)
        print("Table 'llm_interaction_log' is ready.")

        conn.commit()
    except Exception as e:
        print(f"Database setup error: {e}")
    finally:
        if conn:
            conn.close()

# --- LLM INTERACTION LOGGING FUNCTION ---
def log_llm_interaction(db_file, card_url, bank_name, card_name, page_text, response_json, status):
    """Logs the input and output of an LLM interaction for auditing."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_sql = """
        INSERT INTO llm_interaction_log (card_url, bank_name, card_name, run_timestamp, raw_page_text, llm_response_json, status)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(log_sql, (card_url, bank_name, card_name, timestamp, page_text, response_json, status))
        conn.commit()
    except Exception as e:
        print(f"  Error logging LLM interaction: {e}")
    finally:
        if conn:
            conn.close()


import threading

# --- LLM EXTRACTION FUNCTION ---
# Global semaphore to limit concurrent LLM calls
llm_semaphore = threading.Semaphore(1) # Limit to 1 concurrent LLM request

def extract_data_with_llm_from_text(page_text_content):
    """
    Sends clean text content to the Gemini LLM and extracts structured data.
    Returns a tuple: (parsed_json_data, raw_response_text)
    """
    model = genai.GenerativeModel('models/gemini-flash-latest')
    prompt_text = f"""
You are an AI assistant specialized in extracting credit card information from website text.
From the following text content of a credit card webpage, extract the data points for the following categories.
If a specific piece of information is not found, state "Not Mentioned".

**Card Identification:**
- Card Name
- Bank Name

**Eligibility & Conditions:**
- Minimum Salary Requirement
- Annual Fee
- Minimum Spend Requirement
- Balance Transfer / 0% Installment Plan Eligibility

**Rewards & Earnings:**
- Welcome Bonus / Sign-up Offer
- Cashback Rates
- Points / Miles Earning Rates
- Co-brand Specific Rewards

**Travel Perks:**
- Airport Lounge Access
- Travel Insurance
- Airport Transfers
- Hotel Discounts / Upgrades

**Lifestyle & Entertainment:**
- Cinema Offers
- Dining Discounts
- Golf Privileges
- Valet Parking

**Purchase & Protection Benefits:**
- Purchase Protection
- Extended Warranty
- Other Key Benefits

**Output Format:** Provide the extracted data as a single, flat JSON object.
    ```json
    {{
      "Card Name": "Example Card",
      "Bank Name": "Example Bank"
    }}
    ```
    ---
Webpage Text Content:
{page_text_content}
"""
    raw_response_text = ""
    try:
        # Acquire semaphore before making the API call
        with llm_semaphore:
            # print("\n  Sending webpage TEXT to Gemini API for parsing...")
            # Add a small delay to respect rate limits
            time.sleep(10) 
            response = model.generate_content(prompt_text, request_options={"timeout": 180})
            raw_response_text = response.text.strip()
        
        if raw_response_text.startswith("```json"):
            json_part = raw_response_text[len("```json"):].strip()
            if json_part.endswith("```"):
                json_part = json_part[:-len("```")].strip()
        else:
            json_part = raw_response_text
            
        extracted_data = json.loads(json_part)
        # print("  Data extracted by LLM successfully.")
        return extracted_data, raw_response_text
    except Exception as e:
        raise Exception(f"LLM Error: {e}\nRaw Response: {raw_response_text}")


# --- WORKER FUNCTION: PROCESS SINGLE CARD ---
def process_card_data(card_info, chrome_driver_path):
    """
    Scrapes a single card URL and returns the extracted data.
    Does NOT write to the database to avoid locking issues.
    """
    target_url = card_info['url']
    bank_name_from_inventory = card_info['bank_name']
    card_name_from_inventory = card_info['card_name']
    
    print(f"--- Processing: {card_name_from_inventory} ({bank_name_from_inventory}) ---")
    
    page_text = ""
    llm_response_json = ""
    llm_data = {}
    status = 'FAILED'
    driver = None

    try:
        service = Service(executable_path=chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
        options.add_argument('--log-level=3') 
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.get(target_url)

        # Smart Wait
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2) # Short buffer
        except:
            print(f"  Timeout loading {target_url}")

        # Intelligent redirection check
        final_url = driver.current_url
        target_path_slug = urlparse(target_url).path.rstrip('/').split('/')[-1].split('.')[0]
        final_path_slug = urlparse(final_url).path.rstrip('/').split('/')[-1].split('.')[0]
        
        if target_path_slug.lower() != final_path_slug.lower():
             # print(f"  !!! WARNING: Redirected from '{target_path_slug}' to '{final_path_slug}' !!!")
             return {'success': False, 'url': target_url, 'error': 'Redirect Failure', 'log_data': (target_url, bank_name_from_inventory, card_name_from_inventory, "", "", 'REDIRECT_FAILURE')}

        page_text = driver.find_element(By.TAG_NAME, 'body').text
        if page_text and len(page_text) > 100:
            llm_data, llm_response_json = extract_data_with_llm_from_text(page_text)
            if llm_data:
                return {
                    'success': True,
                    'url': target_url,
                    'llm_data': llm_data,
                    'log_data': (target_url, bank_name_from_inventory, card_name_from_inventory, page_text, llm_response_json, 'SUCCESS')
                }
        else:
            return {'success': False, 'url': target_url, 'error': 'Page Empty', 'log_data': (target_url, bank_name_from_inventory, card_name_from_inventory, page_text, "", 'PAGE_EMPTY')}

    except Exception as e:
        error_str = str(e)
        # print(f"  Error processing {target_url}: {error_str}")
        if "LLM Error" in error_str:
            # Log the full error string if raw response is empty
            llm_response_json = error_str.split("Raw Response:")[-1].strip()
            if not llm_response_json:
                llm_response_json = error_str # Fallback to full error message
            return {'success': False, 'url': target_url, 'error': 'LLM Error', 'log_data': (target_url, bank_name_from_inventory, card_name_from_inventory, page_text, llm_response_json, 'LLM_ERROR')}
        else:
            return {'success': False, 'url': target_url, 'error': 'Selenium Error', 'log_data': (target_url, bank_name_from_inventory, card_name_from_inventory, page_text, "", 'SELENIUM_ERROR')}
    
    finally:
        if driver:
            driver.quit()
    
    return {'success': False, 'url': target_url, 'error': 'Unknown Error', 'log_data': None}


# --- MAIN THREAD: DATABASE UPDATE ---
def update_card_in_database(database_file, result, card_info):
    """Writes the extracted data to the database."""
    if not result['success']:
        return

    llm_data = result['llm_data']
    bank_name_from_inventory = card_info['bank_name']
    card_name_from_inventory = card_info['card_name']
    target_url = card_info['url']

    conn = None
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        
        card_name = llm_data.get('Card Name') or card_name_from_inventory
        bank_name = bank_name_from_inventory # Always use the canonical bank name from inventory

        # Sanitize data before insertion
        data_to_insert = {}
        for key, value in llm_data.items():
            if isinstance(value, (dict, list)):
                data_to_insert[key] = json.dumps(value)
            else:
                data_to_insert[key] = value

        # Parse numeric salary
        raw_salary = data_to_insert.get('Minimum Salary Requirement', '-')
        min_salary_numeric = 0.0
        try:
            if raw_salary and raw_salary not in ["Not Mentioned", "Not Found", "-"]:
                clean_str = str(raw_salary).replace(',', '')
                matches = re.findall(r'\d+\.?\d*', clean_str)
                if matches:
                    min_salary_numeric = min([float(m) for m in matches])
        except:
            pass

        # Parse Cashback
        raw_cashback = data_to_insert.get('Cashback Rates', '-')
        max_cashback_rate = 0.0
        is_uncapped = False
        cashback_type = 'Variable'
        
        try:
            if raw_cashback and raw_cashback not in ["Not Mentioned", "Not Found", "-"]:
                text_lower = str(raw_cashback).lower()
                # Max Rate
                rates = re.findall(r'(\d+(?:\.\d+)?)%', str(raw_cashback))
                if rates:
                    max_cashback_rate = max([float(r) for r in rates])
                # Uncapped
                if 'unlimited' in text_lower or 'no cap' in text_lower:
                    is_uncapped = True
                    
                # Type
                if 'flat' in text_lower:
                    cashback_type = 'Flat'
                elif len(set(rates)) == 1 and 'up to' not in text_lower:
                    cashback_type = 'Flat'
        except:
            pass

        insert_sql = """
        INSERT INTO credit_cards_details (
            url, bank_name, card_name, minimum_salary_requirement, min_salary_numeric, annual_fee,
            minimum_spend_requirement, balance_transfer_eligibility, welcome_bonus,
            cashback_rates, max_cashback_rate, is_uncapped, cashback_type,
            points_earning_rates, cobrand_rewards, airport_lounge_access,
            travel_insurance, airport_transfers, hotel_discounts, cinema_offers,
            dining_discounts, golf_privileges, valet_parking, purchase_protection,
            extended_warranty, other_key_benefits, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            bank_name=excluded.bank_name,
            card_name=excluded.card_name,
            minimum_salary_requirement=excluded.minimum_salary_requirement,
            min_salary_numeric=excluded.min_salary_numeric,
            annual_fee=excluded.annual_fee,
            minimum_spend_requirement=excluded.minimum_spend_requirement,
            balance_transfer_eligibility=excluded.balance_transfer_eligibility,
            welcome_bonus=excluded.welcome_bonus,
            cashback_rates=excluded.cashback_rates,
            max_cashback_rate=excluded.max_cashback_rate,
            is_uncapped=excluded.is_uncapped,
            cashback_type=excluded.cashback_type,
            points_earning_rates=excluded.points_earning_rates,
            cobrand_rewards=excluded.cobrand_rewards,
            airport_lounge_access=excluded.airport_lounge_access,
            travel_insurance=excluded.travel_insurance,
            airport_transfers=excluded.airport_transfers,
            hotel_discounts=excluded.hotel_discounts,
            cinema_offers=excluded.cinema_offers,
            dining_discounts=excluded.dining_discounts,
            golf_privileges=excluded.golf_privileges,
            valet_parking=excluded.valet_parking,
            purchase_protection=excluded.purchase_protection,
            extended_warranty=excluded.extended_warranty,
            other_key_benefits=excluded.other_key_benefits,
            last_updated=excluded.last_updated;
        """

        cursor.execute(insert_sql, (
            target_url, bank_name, card_name,
            data_to_insert.get('Minimum Salary Requirement', '-'),
            min_salary_numeric,
            data_to_insert.get('Annual Fee', '-'),
            data_to_insert.get('Minimum Spend Requirement', '-'),
            data_to_insert.get('Balance Transfer / 0% Installment Plan Eligibility', '-'),
            data_to_insert.get('Welcome Bonus / Sign-up Offer', '-'),
            data_to_insert.get('Cashback Rates', '-'),
            max_cashback_rate,
            is_uncapped,
            cashback_type,
            data_to_insert.get('Points / Miles Earning Rates', '-'),
            data_to_insert.get('Co-brand Specific Rewards', '-'),
            data_to_insert.get('Airport Lounge Access', '-'),
            data_to_insert.get('Travel Insurance', '-'),
            data_to_insert.get('Airport Transfers', '-'),
            data_to_insert.get('Hotel Discounts / Upgrades', '-'),
            data_to_insert.get('Cinema Offers', '-'),
            data_to_insert.get('Dining Discounts', '-'),
            data_to_insert.get('Golf Privileges', '-'),
            data_to_insert.get('Valet Parking', '-'),
            data_to_insert.get('Purchase Protection', '-'),
            data_to_insert.get('Extended Warranty', '-'),
            data_to_insert.get('Other Key Benefits', '-'),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        print(f"  > Saved: {card_name}")
    except Exception as e:
        print(f"  Database insertion error: {e}")
    finally:
        if conn: conn.close()


# --- DATA FETCHING & EXECUTION ---
def get_cards_from_inventory(database_file):
    """
    Fetches a list of all active cards (url, bank_name, card_name) from the inventory.
    Also fetches the last_updated date from the details table to enable smart caching.
    """
    conn = None
    cards = []
    try:
        conn = sqlite3.connect(database_file)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        print("\nFetching active cards and checking cache status...")
        
        # Join inventory with details to check last_updated
        sql = """
        SELECT i.url, i.bank_name, i.card_name, d.last_updated
        FROM card_inventory i
        LEFT JOIN credit_cards_details d ON i.url = d.url
        WHERE i.is_active = 1;
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cards = [dict(row) for row in rows]
    except Exception as e:
        print(f"  Database error fetching URLs from inventory: {e}")
    finally:
        if conn:
            conn.close()
    return cards

def save_summary(database_file, summary):
    """Saves the final run summary to the database."""
    conn = None
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        insert_sql = """
        INSERT INTO run_summary (
            run_timestamp, total_urls_in_inventory, urls_processed,
            successful_extractions, failed_urls, total_retries
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_sql, (
            summary["run_timestamp"],
            summary["total_urls_in_inventory"],
            summary["urls_processed"],
            summary["successful_extractions"],
            summary["failed_urls"],
            summary["total_retries"]
        ))
        conn.commit()
        print("\nRun summary saved to database.")
    except Exception as e:
        print(f"\nError saving run summary: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    setup_database(db_file)
    start_time = time.time()
    
    all_cards = get_cards_from_inventory(db_file)
    
    # --- SMART CACHING LOGIC ---
    cards_to_process = []
    skipped_count = 0
    
    print(f"Total active cards in inventory: {len(all_cards)}")
    
    for card in all_cards:
        should_process = True
        last_updated_str = card.get('last_updated')
        
        if last_updated_str:
            try:
                last_updated = datetime.datetime.strptime(last_updated_str, "%Y-%m-%d %H:%M:%S")
                days_diff = (datetime.datetime.now() - last_updated).days
                if days_diff < CACHE_VALIDITY_DAYS:
                    should_process = False
            except ValueError:
                pass # If date format is wrong, re-process
        
        if should_process:
            cards_to_process.append(card)
        else:
            skipped_count += 1
            
    print(f"Skipping {skipped_count} cards (Updated within last {CACHE_VALIDITY_DAYS} days).")
    print(f"Queuing {len(cards_to_process)} cards for scraping...")

    run_summary = {
        "run_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_urls_in_inventory": len(all_cards),
        "urls_processed": 0,
        "successful_extractions": 0,
        "failed_urls": 0,
        "total_retries": 0
    }
    
    if not cards_to_process:
        print("\nAll cards are up to date! Nothing to do.")
    else:
        # --- PARALLEL EXECUTION ---
        print("\n--- Starting Parallel Detail Scraper (5 Workers) ---")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tasks
            future_to_card = {executor.submit(process_card_data, card, chromedriver_path): card for card in cards_to_process}
            
            for future in concurrent.futures.as_completed(future_to_card):
                card_info = future_to_card[future]
                run_summary["urls_processed"] += 1
                try:
                    result = future.result()
                    
                    # Log interaction (Main thread handles this safely)
                    if result.get('log_data'):
                        log_llm_interaction(db_file, *result['log_data'])
                    
                    if result['success']:
                        update_card_in_database(db_file, result, card_info)
                        run_summary["successful_extractions"] += 1
                    else:
                        print(f"  x Failed: {card_info['card_name']} ({result['error']})")
                        run_summary["failed_urls"] += 1
                        
                except Exception as exc:
                    print(f"  ! Exception for {card_info['card_name']}: {exc}")
                    run_summary["failed_urls"] += 1

    end_time = time.time()
    total_time = end_time - start_time

    print("\n\n--- FINAL RUN SUMMARY ---")
    for key, value in run_summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"Total Run Time: {total_time:.2f} seconds")
    save_summary(db_file, run_summary)
    print("\nCredit Card Detail Scraper run finished.")
