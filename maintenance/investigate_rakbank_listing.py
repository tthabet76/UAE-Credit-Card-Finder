from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import sys
import os
from urllib.parse import unquote, urlparse, parse_qs

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import update_images
except ImportError:
    from maintenance import update_images

URL = "https://www.rakbank.ae/en/cards/credit-cards"

def investigate():
    print(f"--- Investigating Listing Page: {URL} ---")
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(URL)
        
        # Find all card containers?
        # Usually listing pages have a grid.
        # Let's look for images and their alt text.
        
        imgs = driver.find_elements(By.TAG_NAME, "img")
        print(f"Found {len(imgs)} images total.")
        
        for i, img in enumerate(imgs):
            src = img.get_attribute("src")
            alt = img.get_attribute("alt")
            
            # Filter for likely card images (Next.js images)
            if src and "_next/image" in src:
                # Decode to check filename
                filename = "unknown"
                if "url=" in src:
                    try:
                        decoded = unquote(src.split("url=")[1].split("&")[0])
                        filename = decoded.split("/")[-1]
                    except:
                        pass
                
                print(f"[{i}] Alt: '{alt}' | File: {filename}")
                print(f"    Src: {src[:100]}...")

    finally:
        driver.quit()

if __name__ == "__main__":
    investigate()
