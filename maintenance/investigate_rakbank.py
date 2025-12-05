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

URL = "https://www.rakbank.ae/en/cards/credit-cards/elevate-credit-card/"

def investigate():
    print(f"--- Investigating: {URL} ---")
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(URL)
        
        print("\n--- Meta Tags ---")
        metas = driver.find_elements(By.TAG_NAME, "meta")
        for m in metas:
            prop = m.get_attribute("property")
            name = m.get_attribute("name")
            content = m.get_attribute("content")
            if prop in ["og:image", "twitter:image"] or name in ["og:image", "twitter:image"]:
                print(f"{prop or name}: {content}")

        print("\n--- Dumping Page Source ---")
        with open("rakbank_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved to rakbank_source.html")

    finally:
        driver.quit()

if __name__ == "__main__":
    investigate()
