import sys
import os

# Add maintenance to path to import update_images
sys.path.append(os.path.join(os.path.dirname(__file__)))

from update_images import extract_generic_image_by_content, chromedriver_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def debug_one_card():
    # ADIB URL (Example)
    url = "https://www.adib.ae/en/pages/cards_covered_booking_signature.aspx" 
    card_name = "ADIB Booking.com Signature Card"
    
    print(f"Testing URL: {url}")
    
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        print("Page loaded.")
        
        # Test Generic Extraction
        print("Running extract_generic_image_by_content...")
        img = extract_generic_image_by_content(driver, card_name)
        print(f"Result: {img}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_one_card()
