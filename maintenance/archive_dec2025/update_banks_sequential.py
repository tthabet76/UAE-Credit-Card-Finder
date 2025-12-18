"""
A backup version of update_banks.py that runs one browser at a time (slower but safer if parallel fails).
"""
# --- IMPORTS SECTION ---
import time
import re
import datetime
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse

# from webdriver_manager.chrome import ChromeDriverManager
chromedriver_path = r'C:\Users\cdf846\Documents\personal\Credit card project\chromedriver.exe' # Make sure this path is correct for your system
db_file = 'credit_card_data.db'

# This is the final, comprehensive list of credit card pages to target.
bank_listing_urls = {
    "RAKBANK": "https://rakbank.ae/wps/portal/retail-banking/cards/credit-cards",
    "Mashreq": "https://www.mashreq.com/en/uae/neo/cards/",
    "Arab Bank": "https://arabbank.ae/mainmenu/home/Consumer-Banking/cards/card-type",
    "NBF": "https://nbf.ae/personal/cards/",
    "ADCB Islamic": "https://www.adcb.com/en/islamic/personal/cards/credit-cards/",
    "ADCB": "https://www.adcb.com/en/personal/cards/credit-cards/",
    "ADIB": "https://www.adib.ae/personal/cards/",
    "Ajman Bank": "https://www.ajmanbank.ae/site/bright-card.html",
    "Al Hilal Bank": "https://www.alhilalbank.ae/en/personal/cards/credit-cards/",
    "American Express": "https://www.americanexpress.ae/en-ae/cards/",
    "FAB": "https://www.bankfab.com/en-ae/personal/credit-cards",
    "CBD": "https://www.cbd.ae/personal/cards/credit-cards",
    "CBI": "https://www.cbiuae.com/en/personal/products-and-services/cards/",
    "Citibank": "https://www.citibank.ae/credit-cards",
    "DIB": "https://www.dib.ae/personal/cards/?cardType=credit-cards&incomeMax=Any&incomeMin=Any&cardBenefit=All-Benefits&visible=24",
    "Dubai First": "https://www.dubaifirst.com/en-ae",
    "Emirates Islamic": "https://www.emiratesislamic.ae/en/personal-banking/cards/credit-cards",
    "Emirates NBD": "https://www.emiratesnbd.com/en/cards/credit-cards",
    "Finance House": "https://www.financehouse.ae/en/personal-finance/credit-cards/",
    "HSBC": "https://www.hsbc.ae/credit-cards/products/",
    "Standard Chartered": "https://www.sc.com/ae/personal/cards/credit-cards/",
    "UAB": "https://www.uab.ae/Compare-Credit-Cards",
    "SIB": "https://www.sib.ae/personal-banking/cards",
    "NBQ": "https://nbq.ae/personal/cards"
}


# --- SECTION 2: DATABASE SETUP ---
# This function creates our database and the table schema.
# ===================================================================
def setup_database():
    """Initializes the database and ensures the schema is up-to-date."""
    print("--- Setting up database ---")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_inventory (
            id INTEGER PRIMARY KEY, url TEXT UNIQUE NOT NULL, bank_name TEXT,
            first_discovered_date TEXT, last_verified_date TEXT, is_active BOOLEAN,
            card_name TEXT
        );
    ''')
    conn.commit()
    conn.close()
    print(f"  Database '{db_file}' is ready.\n")

def clear_inventory_table():
    """Deletes all records from the card_inventory table for a fresh run."""
    print("--- Clearing card inventory table for a fresh run ---")
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM card_inventory;")
        conn.commit()
        print("  All previous records have been deleted from card_inventory.")
    except Exception as e:
        print(f"  Error clearing inventory table: {e}")
    finally:
        if conn:
            conn.close()


# --- SECTION 3: CORE DISCOVERY LOGIC ---
# This function now accepts a driver instance to avoid creating a new one for each bank.
# ===================================================================
def discover_cards_from_listing(driver, bank_name, listing_url):
    """Uses a shared Selenium driver to get the page and extract card data."""
    print(f"--- Discovering cards for {bank_name} ---")
    try:
        driver.get(listing_url)
        print(f"  Navigated to {listing_url}")
        time.sleep(10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        found_cards = []
        used_specific_strategy = True  # Assume specific strategy is used first

        # --- Bank-Specific Parsing Strategies ---
        if bank_name == "Mashreq":
            print("  Using specific parsing strategy for Mashreq Bank...")
            card_containers = soup.find_all('div', class_=re.compile('ProductCard_card__'))
            for container in card_containers:
                link_element = container.find('a', class_=re.compile('Button_secondary__'))
                if link_element:
                    full_url = urljoin(listing_url, link_element['href'])
                    name_element = container.find('h5', class_=re.compile('ProductCardTop_title__'))
                    card_name = name_element.text.strip() if name_element else "Name Not Found"
                    found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name in ["ADCB", "ADCB Islamic"]:
            print(f"  Using specific parsing strategy for {bank_name}...")
            card_containers = soup.find_all('div', class_=re.compile(r'\bc-card\b'))
            for container in card_containers:
                link_element = container.find('div', class_='c-card__image')
                if link_element and link_element.get('data-href'):
                    href = link_element.get('data-href')
                    if 'credit-cards/' in href and 'debit-cards/' not in href:
                        full_url = urljoin(listing_url, href)
                        name_element = container.find('h3', class_='c-card__title')
                        card_name = name_element.text.strip() if name_element else "Name Not Found"
                        found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "RAKBANK":
            print("  Using specific parsing strategy for RAKBANK...")
            card_containers = soup.find_all('div', class_='product-card-horizontal__inner')
            for container in card_containers:
                name_element = container.find('h5', class_='gradient-title')
                link_element = container.find('a', class_='tertiary-cta')
                if name_element and link_element and link_element.get('href'):
                    # First, resolve the relative URL to an absolute one
                    raw_url = urljoin(listing_url, link_element['href'])
                    
                    # Targeted fix: Ensure RAKBANK URLs have 'https' and 'www'
                    p = urlparse(raw_url)
                    netloc = p.netloc
                    if not netloc.startswith('www.'):
                        netloc = 'www.' + netloc
                    
                    # Rebuild the URL with the correct scheme and subdomain
                    full_url = urlunparse(('https', netloc, p.path, p.params, p.query, p.fragment))
                    
                    card_name = name_element.text.strip()
                    found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "Emirates NBD":
            print("  Using specific parsing strategy for Emirates NBD...")
            card_containers = soup.find_all('div', class_='cc-block')
            for container in card_containers:
                link_element = container.find('a', class_='link-arrow')
                if link_element and link_element.get('href'):
                    full_url = urljoin(listing_url, link_element['href'])
                    name_element = container.find('h3', class_='cc-block__title')
                    card_name = name_element.text.strip() if name_element else "Name Not Found"
                    found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "FAB":
            print("  Using specific parsing strategy for FAB...")
            card_containers = soup.find_all('div', class_='credit-card-item')
            for container in card_containers:
                title_element = container.find('h3', class_='card-title')
                link_element = container.find('a', class_='read-more')
                if title_element and link_element:
                    full_url = urljoin(listing_url, link_element.get('href'))
                    found_cards.append({'url': full_url, 'name': title_element.text.strip()})

        elif bank_name == "HSBC":
            print("  Using specific parsing strategy for HSBC...")
            card_containers = soup.find_all('li', class_='M-CNT-ITEM-ART-DEV')
            for container in card_containers:
                link_element = container.find('h3', class_='link-header').find('a')
                if link_element and '/compare/' not in link_element.get('href', ''):
                    full_url = urljoin(listing_url, link_element['href'])
                    name_element = link_element.find('span', class_='link text')
                    card_name = name_element.text.strip() if name_element else "Name Not Found"
                    found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "Standard Chartered":
            print("  Using specific parsing strategy for Standard Chartered...")
            card_containers = soup.find_all('div', class_='product-action')
            for container in card_containers:
                link_element = container.find('a', title='Find out more')
                if link_element:
                    full_url = urljoin(listing_url, link_element['href'])
                    name_container = container.find_previous_sibling('div', class_='product-box-content')
                    name_element = name_container.find('p', class_='img-text') if name_container else None
                    card_name = name_element.text.strip() if name_element else "Name Not Found"
                    found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "CBD":
            print("  Using specific parsing strategy for CBD...")
            card_containers = soup.find_all('div', class_='card-box')
            for container in card_containers:
                name_element = container.find('h3', class_='c-card-heading')
                if name_element:
                    title_link_element = name_element.find_parent('a')
                    if title_link_element:
                        full_url = urljoin(listing_url, title_link_element['href'])
                        card_name = name_element.text.strip()
                        found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "Emirates Islamic":
            print("  Using specific parsing strategy for Emirates Islamic Bank...")
            card_containers = soup.find_all('div', class_='card')
            for container in card_containers:
                card_body = container.find('div', class_='card-body')
                if card_body:
                    name_element = card_body.find('h5', class_='card-title')
                    link_element = card_body.find('a', class_='link')
                    if name_element and link_element:
                        full_url = urljoin(listing_url, link_element['href'])
                        card_name = name_element.text.strip()
                        found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "Arab Bank":
            print("  Using specific parsing strategy for Arab Bank...")
            card_containers = soup.find_all('div', class_='listingItem')
            for container in card_containers:
                title_div = container.find('div', class_='listingTitle')
                if title_div:
                    link_element = title_div.find('a')
                    if link_element and link_element.get('href'):
                        href_lower = link_element['href'].lower()
                        if any(keyword in href_lower for keyword in ["credit-card", "visa", "mastercard"]):
                            full_url = urljoin(listing_url, link_element['href'])
                            card_name = link_element.text.strip()
                            found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "NBF":
            print("  Using specific parsing strategy for National Bank of Fujairah...")
            card_containers = soup.find_all('div', class_='elementor-widget-heading')
            for container in card_containers:
                name_element = container.find('h2', class_='elementor-heading-title')
                if name_element:
                    card_name = name_element.text.strip()
                    if "debit" in card_name.lower():
                        continue 
                    if "card" not in card_name.lower():
                        continue
                    parent_container = container.find_parent(class_='e-con-full')
                    if parent_container:
                        read_more_span = parent_container.find('span', class_='elementor-button-text', string=re.compile(r'Read More', re.IGNORECASE))
                        if read_more_span:
                            link_element = read_more_span.find_parent('a')
                            if link_element and link_element.get('href'):
                                full_url = urljoin(listing_url, link_element['href'])
                                found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "ADIB":
            print("  Using specific parsing strategy for Abu Dhabi Islamic Bank (ADIB)...")
            card_containers = soup.find_all('div', class_='covered-wrapper')
            for container in card_containers:
                name_element = container.find('h4', class_='new-covered-card__title')
                link_element = container.find('a', class_='arrow-anchor black')

                if name_element and link_element and link_element.get('href'):
                    card_name = name_element.text.strip()
                    if "card" in card_name.lower():
                        full_url = urljoin(listing_url, link_element['href'])
                        found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "Ajman Bank":
            print("  Using hybrid parsing strategy for Ajman Bank...")
            found_cards.append({
                'url': 'https://www.ajmanbank.ae/site/mastercard_ultracash/en',
                'name': 'ULTRACASH Mastercard'
            })
            card_containers = soup.find_all('div', class_='js-scroll')
            for container in card_containers:
                name_element = container.find('h5', class_='card-title')
                link_element = container.find('a', class_='InnerPageBoxLink')
                if name_element and link_element and link_element.get('href'):
                    card_name = name_element.text.strip()
                    full_url = urljoin(listing_url, link_element['href'])
                    found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "Al Hilal Bank":
            print("  Using specific parsing strategy for Al Hilal Bank...")
            card_containers = soup.find_all('div', class_='c-discover-card-list__item')
            for container in card_containers:
                name_element = container.find('h3', class_='c-discover-card__title')
                link_element = container.find('a', class_='o-btn', string=re.compile(r'Learn more', re.IGNORECASE))
                if name_element and link_element and link_element.get('href'):
                    card_name = name_element.text.strip()
                    full_url = urljoin(listing_url, link_element['href'])
                    found_cards.append({'url': full_url, 'name': card_name})

        elif bank_name == "American Express":
            print("  Using specific parsing strategy for American Express UAE...")
            card_containers = soup.find_all('div', class_='dls-white-bg')
            for container in card_containers:
                name_element = container.find('a', class_='heading-3')
                link_element = container.find('a', class_='btn-secondary', string=re.compile(r'Learn More', re.IGNORECASE))
                if name_element and link_element and link_element.get('href'):
                    card_name = name_element.text.strip()
                    full_url = urljoin(listing_url, link_element['href'])
                    found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "CBI":
            print("  Using specific parsing strategy for Commercial Bank International (CBI)...")
            owl_containers = soup.find_all('div', class_='owl-item')
            for container in owl_containers:
                link_element = container.find('a', class_='marketing-link')
                if link_element:
                    name_element = link_element.find('h4')
                    if name_element and link_element.get('href'):
                        card_name = name_element.text.strip()
                        if "card" in card_name.lower() and "debit" not in card_name.lower():
                            full_url = urljoin(listing_url, link_element['href'])
                            found_cards.append({'url': full_url, 'name': card_name})
            compare_containers = soup.find_all('div', class_='compare-product')
            for container in compare_containers:
                name_element = container.find('p', class_='sub')
                link_element = container.find('a', class_='btn-secondary')
                if name_element and link_element and link_element.get('href'):
                    card_name = name_element.text.strip()
                    if "card" in card_name.lower() and "debit" not in card_name.lower():
                        full_url = urljoin(listing_url, link_element['href'])
                        found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "Citibank":
            print("  Using simplified static parsing strategy for Citibank UAE...")
            card_containers = soup.find_all('article', class_=re.compile(r'cmp-contentfragment--citi'))
            for container in card_containers:
                title_element = container.find('h3', class_='cmp-contentfragment__title')
                learn_more_link = container.find('a', class_='bg-primary')
                if title_element and learn_more_link and learn_more_link.get('href'):
                    raw_name = title_element.text.strip()
                    card_name = raw_name.replace("(Opens In A New Tab)", "").strip()
                    if "card" in card_name.lower() or "citi" in card_name.lower():
                        full_url = urljoin(listing_url, learn_more_link['href'])
                        found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "DIB":
            print("  Using specific parsing strategy for Dubai Islamic Bank (DIB)...")
            card_containers = soup.find_all('div', class_='card-list-item')
            for container in card_containers:
                title_div = container.find('div', class_='card-title-info')
                if title_div:
                    link_element = title_div.find('a')
                    if link_element and link_element.get('href'):
                        card_name = link_element.text.strip()
                        full_url = urljoin(listing_url, link_element['href'])
                        found_cards.append({'url': full_url, 'name': card_name})
            
        elif bank_name == "Dubai First":
            print("  Using specific parsing strategy for Dubai First...")
            card_containers = soup.find_all('div', class_='cards-list-grid-card')
            for container in card_containers:
                name_element = container.find('h3', class_='cl-card-desc-title')
                link_container = container.find('div', class_='cl-card-desc-link')
                if name_element and link_container:
                    link_element = link_container.find('a')
                    if link_element and link_element.get('href'):
                        full_url = urljoin(listing_url, link_element['href'])
                        card_name = name_element.text.strip()
                        found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "Finance House":
            print("  Using special manual strategy for Finance House...")
            found_cards.append({
                'url': listing_url,
                'name': 'Finance House Credit Cards'
            })

        elif bank_name == "UAB":
            print("  Using static menu parsing strategy for United Arab Bank...")
            card_links = soup.select("div.nav__col a.nav__sublink")
            for link in card_links:
                href = link.get('href')
                if href and 'Credit-Cards' in href:
                    card_name_span = link.find('span')
                    if card_name_span:
                        card_name = card_name_span.text.strip()
                        if card_name and card_name.lower() != 'cards' and 'shield' not in card_name.lower():
                            full_url = urljoin(listing_url, href)
                            found_cards.append({'url': full_url, 'name': card_name})
        
        elif bank_name == "SIB":
            # Strategy for Sharjah Islamic Bank (SIB)
            card_containers = soup.find_all('div', class_='card-item') # Generic guess, will fallback if not found
            # Actually, let's use a more generic link finder for SIB if specific structure is unknown or complex
            # But based on typical structure, let's try to find links with 'card' in text
            pass # Fallback will handle it if specific logic isn't perfect yet

        elif bank_name == "NBQ":
             # Strategy for National Bank of Umm Al Quwain (NBQ)
             pass # Fallback will handle it

        # --- Fallback Strategy ---
        if not found_cards:
            used_specific_strategy = False
            print("  No specific strategy found or it failed. Attempting Fallback...")
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if 'credit-card' in href and href.count('/') >= 3:
                    if not href.endswith(('/cards/', '/credit-cards/')):
                        full_url = urljoin(listing_url, href)
                        card_name_slug = full_url.rstrip('/').split('/')[-1].replace('-', ' ').title()
                        found_cards.append({'url': full_url, 'name': card_name_slug})

        unique_cards = list({card['url']: card for card in found_cards}.values())

        if unique_cards:
            print(f"  Found {len(unique_cards)} unique cards.")
            update_database_with_cards(bank_name, unique_cards)
        else:
            print(f"  No card links found for {bank_name} with any strategy.")
        
        return {
            'bank_name': bank_name,
            'card_count': len(unique_cards),
            'method': 'Specific' if used_specific_strategy and unique_cards else 'Fallback' if not used_specific_strategy and unique_cards else 'None'
        }

    except Exception as e:
        print(f"  An error occurred during discovery for {bank_name}: {e}")
        return {
            'bank_name': bank_name,
            'card_count': 0,
            'method': 'Error'
        }


# --- SECTION 4: DATABASE UPDATE LOGIC ---
# This function takes the data found by the discovery function
# and saves it to our SQLite database file.
# ===================================================================
def update_database_with_cards(bank_name, cards):
    """Saves or updates discovered cards (URL and Name) in the database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for card in cards:
        raw_name = card.get('name', 'Name Not Found')
        cleaned_name = raw_name.title().replace('–', '-').replace('/', ' / ')
        final_name = re.sub(r'\s+', ' ', cleaned_name).strip()

        cursor.execute("""
            INSERT INTO card_inventory (url, bank_name, card_name, first_discovered_date, last_verified_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (url) DO UPDATE SET
                card_name = excluded.card_name,
                last_verified_date = excluded.last_verified_date,
                is_active = 1;
        """, (card['url'], bank_name, final_name, current_datetime, current_datetime, 1))
    conn.commit()
    conn.close()
    print(f"  Database updated for {bank_name}.")


# --- SECTION 5: MAIN EXECUTION LOOP ---
# This is the entry point that runs everything when you execute the script.
# ===================================================================
if __name__ == "__main__":
    setup_database()
    clear_inventory_table() # Clear the inventory for a fresh run
    start_time = time.time() # Start the timer
    
    print("--- Initializing Selenium WebDriver ---")
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)
    
    run_summary = []

    try:
        for i, (bank_name, url) in enumerate(bank_listing_urls.items()):
            summary = discover_cards_from_listing(driver, bank_name, url)
            run_summary.append(summary)
            
    finally:
        if driver:
            print("\n--- Closing WebDriver ---")
            driver.quit()

    end_time = time.time() # Stop the timer
    total_time = end_time - start_time

    print("\n\n--- DISCOVERY AGENT RUN SUMMARY ---")
    print("===================================")
    total_cards_found = 0
    for report in run_summary:
        print(f"- {report['bank_name']}: Found {report['card_count']} cards (Method: {report['method']})")
        total_cards_found += report['card_count']
    print("===================================")
    print(f"Total Unique Cards Discovered Across All Banks: {total_cards_found}")
    print(f"Total Run Time: {total_time:.2f} seconds") # Display total run time
    print("--- Main Discovery Agent run has finished. ---")
