from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import update_images
except ImportError:
    from maintenance import update_images

URL = "https://www.mashreq.com/en/uae/neo/cards/credit-cards/solitaire-credit-card/"
CARD_NAME = "Solitaire"

def investigate():
    print(f"--- Investigating Mashreq: {CARD_NAME} ---")
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # Mashreq might block headless, let's try to mimic a real browser
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(URL)
        driver.implicitly_wait(10)
        
        # 1. Check Meta Tags
        print("\n--- Meta Tags ---")
        og_img = driver.find_elements(By.XPATH, '//meta[@property="og:image"]')
        if og_img:
            print(f"og:image: {og_img[0].get_attribute('content')}")
        else:
            print("No og:image found.")
            
        # 2. Check All Images
        print("\n--- All Images (First 20) ---")
        imgs = driver.find_elements(By.TAG_NAME, "img")
        print(f"Found {len(imgs)} images.")
        
        for i, img in enumerate(imgs[:20]):
            alt = img.get_attribute("alt")
            src = img.get_attribute("src")
            # Filter empty src
            if src:
                print(f"[{i}] Alt: '{alt}' | Src: {src[:80]}...")
                
        # 3. Search for Card Name in Alt and check srcset
        print(f"\n--- Searching for '{CARD_NAME}' in Alt ---")
        found = False
        
        # Re-fetch images to avoid stale reference
        imgs = driver.find_elements(By.TAG_NAME, "img")
        
        for img in imgs:
            try:
                alt = img.get_attribute("alt")
                if alt and CARD_NAME.lower() in alt.lower():
                    src = img.get_attribute("src")
                    srcset = img.get_attribute("srcset")
                    print(f"MATCH! Alt: '{alt}'")
                    print(f"       Src: {src}")
                    if srcset:
                        print(f"       Srcset: {srcset[:100]}...")
                    found = True
            except Exception as e:
                print(f"Error processing image: {e}")
        
        if not found:
            print("No image found with card name in alt.")

    finally:
        driver.quit()

if __name__ == "__main__":
    investigate()
