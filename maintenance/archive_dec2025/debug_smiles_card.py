import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup path to chromedriver (assuming it's in the same dir or known location)
chromedriver_path = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')

def debug_scrape(url):
    print(f"--- Debug Scrape for: {url} ---")
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument('window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        print("  Page loaded, waiting for body...")
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3) # Extra buffer
        except:
            print("  Timeout waiting for body.")
            
        final_url = driver.current_url
        print(f"  Final URL: {final_url}")
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        print(f"  \n--- RAW TEXT CONTENT (Length: {len(body_text)}) ---")
        try:
            print(body_text.encode('utf-8', errors='ignore').decode('utf-8'))
        except:
            print(body_text.encode('ascii', errors='ignore').decode('ascii'))
        print("--------------------------------------------------")
        
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    target_url = "https://www.sib.ae/en/SmilesWorld"
    debug_scrape(target_url)
