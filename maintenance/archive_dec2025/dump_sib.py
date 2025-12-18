import sys
import os

# Add maintenance to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from update_images import chromedriver_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def dump_sib():
    url = "https://www.sib.ae/en/SmilesWorld"
    print(f"Visiting: {url}")
    
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        with open('sib_dump.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("Dumped to sib_dump.html")
    finally:
        driver.quit()

if __name__ == "__main__":
    dump_sib()
