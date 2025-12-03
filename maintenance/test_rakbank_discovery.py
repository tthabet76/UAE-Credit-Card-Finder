"""
Runs a test of the discovery logic specifically for RAKBANK without updating the real database.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time

chromedriver_path = r'C:\Users\cdf846\Documents\personal\Credit card project\chromedriver.exe'

def setup_driver():
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument("--headless") # Run visible for debugging
    return webdriver.Chrome(service=service, options=options)

def test_rakbank():
    print("Testing RAKBANK Discovery...")
    driver = setup_driver()
    try:
        url = "https://www.rakbank.ae/en/personal/cards/credit-cards"
        print(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(10) # Wait for load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # RAKBANK Logic from update_banks.py
        found_cards = []
        card_containers = soup.find_all('div', class_='product-card-horizontal__inner')
        print(f"Found {len(card_containers)} card containers.")
        
        for container in card_containers:
            name_element = container.find('h5', class_='gradient-title')
            link_element = container.find('a', class_='tertiary-cta')
            
            if name_element and link_element and link_element.get('href'):
                raw_url = urljoin(url, link_element['href'])
                p = urlparse(raw_url)
                netloc = p.netloc
                if not netloc.startswith('www.'):
                    netloc = 'www.' + netloc
                full_url = urlunparse(('https', netloc, p.path, p.params, p.query, p.fragment))
                card_name = name_element.text.strip()
                found_cards.append({'url': full_url, 'name': card_name})
        
        print(f"\nFound {len(found_cards)} cards:")
        found_world = False
        for card in found_cards:
            print(f"- [{card['name']}] {card['url']}")
            if "world-credit-card" in card['url']:
                found_world = True
                
        if found_world:
            print("\nSUCCESS: World Credit Card found!")
        else:
            print("\nFAILURE: World Credit Card NOT found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_rakbank()
