from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import unquote, urlparse, parse_qs
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import update_images
except ImportError:
    from maintenance import update_images

URL = "https://www.rakbank.ae/en/cards/credit-cards/red-credit-card/"
CARD_NAME = "Red Credit Card"

def verify():
    print(f"--- Verifying Logic for: {CARD_NAME} ---")
    service = Service(executable_path=update_images.chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(URL)
        
        print("--- Next.js Images Alts ---", flush=True)
        all_imgs = driver.find_elements(By.TAG_NAME, "img")
        print(f"Total images: {len(all_imgs)}", flush=True)
        
        for i, img in enumerate(all_imgs):
            src = img.get_attribute("src")
            if src and "_next/image" in src:
                alt = img.get_attribute("alt")
                # Decode src to see filename
                filename = "unknown"
                if "url=" in src:
                    try:
                        decoded = unquote(src.split("url=")[1].split("&")[0])
                        filename = decoded.split("/")[-1]
                    except:
                        pass
                print(f"[{i}] Alt: '{alt}' | File: {filename}", flush=True)
            
        print("---------------------------", flush=True)

        # Logic: Find img with alt containing card name
        xpath = f"//img[contains(translate(@alt, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{CARD_NAME.lower()}')]"
        print(f"Searching XPath: {xpath}", flush=True)
        
        print("--- Searching Page Source with Regex ---", flush=True)
        import re
        src_code = driver.page_source
        
        # Regex to find img tag with specific alt and capture srcset
        # Note: attributes can be in any order, so this is a bit complex.
        # Simpler: Find the string 'alt="Elevate Credit Card"' and look around it.
        
        # Pattern: <img ... alt="...Elevate Credit Card..." ... srcSet="..." ...>
        # We'll try to match the whole tag roughly
        
        # Find all img tags
        img_tags = re.findall(r'<img[^>]+>', src_code)
        print(f"Found {len(img_tags)} img tags in source.", flush=True)
        
        for tag in img_tags:
            if CARD_NAME.lower() in tag.lower():
                print(f"\nPotential Tag: {tag[:100]}...", flush=True)
                # Extract srcset
                srcset_match = re.search(r'srcSet=["\']([^"\']+)["\']', tag, re.IGNORECASE)
                if srcset_match:
                    srcset = srcset_match.group(1)
                    print(f"Found Srcset in regex: {srcset[:50]}...", flush=True)
                    
                    parts = srcset.split(",")
                    if parts:
                        last_part = parts[-1].strip()
                        target_url = last_part.split(" ")[0]
                        print(f"Selected from Regex Srcset: {target_url}", flush=True)
                        
                        if "/_next/image" in target_url:
                            # We need to unquote it, maybe multiple times or handle HTML entities
                            # The source might have &amp;
                            target_url = target_url.replace("&amp;", "&")
                            parsed = urlparse(target_url)
                            qs = parse_qs(parsed.query)
                            if 'url' in qs:
                                real_url = qs['url'][0]
                                print(f"Decoded URL: {real_url}", flush=True)
                                return # Found it!

    finally:
        driver.quit()

if __name__ == "__main__":
    verify()
