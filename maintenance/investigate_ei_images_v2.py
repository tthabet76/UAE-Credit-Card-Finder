from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import update_images
except ImportError:
    from maintenance import update_images

URL = "https://www.emiratesislamic.ae/en/personal-banking/cards/credit-cards/skywards-black-credit-card"
CARD_NAME = "Skywards Black"

def investigate():
    print(f"--- Investigating Emirates Islamic: {CARD_NAME} ---")
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(URL)
        time.sleep(5) # Wait for dynamic content
        
        with open("ei_urls.txt", "w", encoding="utf-8") as f:
            f.write(f"--- Investigating Emirates Islamic: {CARD_NAME} ---\n")
            
            imgs = driver.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                if src and "skywards" in src.lower():
                    f.write(f"MATCH SRC: {src}\n")
                    f.write(f"      ALT: {alt}\n")
                    
            for img in imgs:
                src = img.get_attribute("src")
                if src and "tile" in src.lower():
                    f.write(f"MATCH TILE: {src}\n")
    finally:
        driver.quit()

if __name__ == "__main__":
    investigate()
