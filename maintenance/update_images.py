"""
[AGENT 3] Image Updater
This agent is responsible for visiting card URLs and extracting the best possible image.
It handles bank-specific logic (like Emirates Islamic tile images) and updates the 'card_images' table.
It is designed to run independently of the main text scraper.
"""
import sqlite3
import time
import re
import os
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, unquote

# --- CONFIGURATION ---
from dotenv import load_dotenv
load_dotenv(override=True)

chromedriver_path = 'C:/Users/cdf846/Documents/personal/Credit card project/chromedriver.exe'
# Point to the root database
db_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credit_card_data.db')

def setup_image_table(database_file):
    """Ensures the card_images table exists."""
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER UNIQUE,
        bank_name TEXT,
        card_name TEXT,
        scraper_image_url TEXT,
        scraper_date TEXT,
        card_url TEXT,
        FOREIGN KEY(card_id) REFERENCES credit_cards_details(id)
    );
    """)
    conn.commit()
    conn.close()

def get_cards_needing_images(database_file):
    """Fetches cards that need image updates (or all cards if we want to refresh)."""
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # For now, let's process ALL active cards to ensure we populate the new table.
    # We join with credit_cards_details to get the stable ID.
    sql = """
    SELECT d.id as card_id, d.url, d.bank_name, d.card_name
    FROM credit_cards_details d
    JOIN card_inventory i ON d.url = i.url
    WHERE i.is_active = 1
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def extract_nextjs_url(tag):
    """Helper to extract URL from Next.js img tag."""
    try:
        # Extract srcset
        srcset_match = re.search(r'srcSet=["\']([^"\']+)["\']', tag, re.IGNORECASE)
        if srcset_match:
            srcset = srcset_match.group(1)
            
            # Take the last URL in srcset (highest res)
            parts = srcset.split(",")
            if parts:
                last_part = parts[-1].strip()
                target_url = last_part.split(" ")[0]
                
                # Handle Next.js optimized images
                if "/_next/image" in target_url:
                    target_url = target_url.replace("&amp;", "&")
                    parsed = urlparse(target_url)
                    qs = parse_qs(parsed.query)
                    if 'url' in qs:
                        extracted = qs['url'][0]
                        
                        # Fix localhost issue (sometimes appears in extracted URL)
                        if "localhost" in extracted:
                            extracted = extracted.replace("http://localhost:80", "https://www.rakbank.ae")
                            extracted = extracted.replace("http://localhost", "https://www.rakbank.ae")
                        
                        # If relative, prepend domain
                        if extracted.startswith("/"):
                            return f"https://www.rakbank.ae{extracted}"
                        return extracted
                else:
                    return target_url
    except:
        pass
    return None

def extract_rakbank_image(driver, card_name):
    """
    Specific logic for RAKBANK using Regex on page source to find Next.js images.
    """
    try:
        src_code = driver.page_source
        
        # Find all img tags
        img_tags = re.findall(r'<img[^>]+>', src_code)
        
        # Priority 1: Match card name in alt
        for tag in img_tags:
            if card_name.lower() in tag.lower():
                url = extract_nextjs_url(tag)
                if url: return url
        
        # Priority 2: Match any alt containing 'card' (case insensitive)
        # This covers 'card', 'Air Arabia Card', 'World Card', etc.
        for tag in img_tags:
            if 'card' in tag.lower():
                # Verify it has an alt attribute containing 'card'
                if re.search(r'alt=["\'][^"\']*card[^"\']*["\']', tag, re.IGNORECASE):
                    url = extract_nextjs_url(tag)
                    if url: return url
                
    except Exception as e:
        print(f"  Error in RAKBANK extraction: {e}")
    return None

def extract_generic_image_by_content(driver, card_name):
    """
    Scans all images on the page and scores them based on how well
    their alt text or filename matches the card name.
    """
    try:
        # Get all images with their attributes
        images_data = driver.execute_script("""
            var imgs = document.getElementsByTagName("img");
            var result = [];
            for (var i = 0; i < imgs.length; i++) {
                result.push({
                    src: imgs[i].src,
                    alt: imgs[i].alt || "",
                    width: imgs[i].naturalWidth,
                    height: imgs[i].naturalHeight
                });
            }
            return result;
        """)

        best_candidate = None
        best_score = 0
        
        card_parts = card_name.lower().split()
        # Remove common words that might dilute the match
        common_words = {'card', 'credit', 'bank', 'uae', 'the', 'of', 'and'}
        keywords = [w for w in card_parts if w not in common_words]
        
        if not keywords:
            keywords = card_parts

        for img in images_data:
            src = img.get('src', '')
            alt = img.get('alt', '')
            width = img.get('width', 0)
            height = img.get('height', 0)
            
            if not src: continue
            
            # Skip tiny icons & tracking pixels
            if width > 0 and width < 100: continue
            if height > 0 and height < 100: continue

            score = 0
            
            # Score based on Alt text (High weight)
            for part in keywords:
                if part in alt.lower():
                    score += 2
            
            # Score based on filename (Medium weight)
            for part in keywords:
                if part in src.lower():
                    score += 1

            # Bonus for 'card' in src/alt if check fails
            if 'card' in src.lower() or 'card' in alt.lower():
                score += 0.5
            
            if score > best_score:
                best_score = score
                best_candidate = src
        
        # Threshold: At least one strong match required (score > 1)
        if best_score > 1:
            # print(f"  > Generic Best Match (Score {best_score}): {best_candidate}")
            return best_candidate
            
    except Exception as e:
        print(f"  Error in generic content extraction: {e}")
    
    return None

def extract_image_url(driver, bank_name, current_url, card_name):
    """
    The core logic for finding the image.
    Contains both GENERIC and BANK-SPECIFIC strategies.
    """
    extracted_image_url = None
    
    try:
        # --- STRATEGY 1: Bank Specific Logic (Priority) ---
        
        if bank_name == 'RAKBANK':
            extracted_image_url = extract_rakbank_image(driver, card_name)
            if extracted_image_url:
                return extracted_image_url

        # [SIB] - Extract background-image from div.exclusive-bg
        if 'SIB' in bank_name or 'Sharjah Islamic' in bank_name:
            try:
                # Find the div with class 'exclusive-bg'
                element = driver.find_element(By.CLASS_NAME, "exclusive-bg")
                style = element.get_attribute("style")
                # Extract URL from style="background-image: url('...')"
                match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
                if match:
                    # Handle relative URLs if necessary (though user example was absolute)
                    url = match.group(1)
                    if url.startswith('/'):
                        url = f"https://www.sib.ae{url}"
                    return url
            except Exception as e:
                print(f"  SIB extraction failed: {e}")

        # --- STRATEGY 2: Generic Meta Tags (Works for 80% of sites) ---
        # Try og:image
        meta_og_img = driver.find_elements(By.XPATH, '//meta[@property="og:image"]')
        if meta_og_img:
            extracted_image_url = meta_og_img[0].get_attribute('content')
            # If generic extraction returns [object Object] (RAKBANK issue), discard it
            if extracted_image_url == '[object Object]':
                extracted_image_url = None
        
        # Fallback to twitter:image
        if not extracted_image_url:
            meta_tw_img = driver.find_elements(By.XPATH, '//meta[@name="twitter:image"]')
            if meta_tw_img:
                extracted_image_url = meta_tw_img[0].get_attribute('content')
                if extracted_image_url == '[object Object]':
                    extracted_image_url = None

        # --- STRATEGY 3: Generic Content Match (Smart Fallback) ---
        if not extracted_image_url:
            extracted_image_url = extract_generic_image_by_content(driver, card_name)

        # --- STRATEGY 3: Post-Processing Bank Specific Logic ---
        
        # [Emirates Islamic] - Tile Image Construction
        # [Emirates Islamic] - Search for 'mobile-image' or matching Alt text
        if bank_name == 'Emirates Islamic':
            try:
                # Priority 1: Search for img with 'mobile-image' in src AND card name in alt
                imgs = driver.find_elements(By.TAG_NAME, "img")
                best_candidate = None
                
                for img in imgs:
                    src = img.get_attribute("src")
                    alt = img.get_attribute("alt")
                    
                    if not src: continue
                    
                    # Check for 'mobile-image' which seems to be the card tile
                    if 'mobile-image' in src:
                        # If alt matches card name, this is definitely it
                        if alt and card_name.lower() in alt.lower():
                            extracted_image_url = src
                            break
                        # Otherwise keep it as a candidate
                        best_candidate = src
                    
                    # Fallback: Check for 'tile-images'
                    elif 'tile-images' in src:
                         if alt and card_name.lower() in alt.lower():
                            extracted_image_url = src
                            break
                         if not best_candidate:
                             best_candidate = src

                # If we didn't find a perfect match but found a candidate, use it
                if not extracted_image_url and best_candidate:
                    extracted_image_url = best_candidate
                    
            except Exception as e:
                print(f"  Error applying Emirates Islamic logic: {e}")

        # [Mashreq] - Robust JS Extraction & Resolution Priority
        if bank_name == 'Mashreq':
            try:
                # Use JS to get all images safely
                images_data = driver.execute_script("""
                    var imgs = document.getElementsByTagName("img");
                    var result = [];
                    for (var i = 0; i < imgs.length; i++) {
                        result.push({
                            src: imgs[i].src,
                            alt: imgs[i].alt || ""
                        });
                    }
                    return result;
                """)
                
                best_candidate = None
                max_res = 0
                
                for img in images_data:
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    
                    if not src: continue
                    
                    # Check if alt contains card name (relaxed match)
                    card_name_parts = card_name.lower().split()
                    match_score = sum(1 for part in card_name_parts if part in alt.lower())
                    
                    # If good match (e.g. > 50% of words match)
                    if match_score >= len(card_name_parts) / 2:
                        # Check resolution in URL (e.g. 360x315)
                        res_match = re.search(r'(\d+)x(\d+)', src)
                        if res_match:
                            width = int(res_match.group(1))
                            height = int(res_match.group(2))
                            resolution = width * height
                            
                            if resolution > max_res:
                                max_res = resolution
                                best_candidate = src
                        else:
                            # If no resolution in URL, but matches text, keep if we have nothing else
                            if not best_candidate:
                                best_candidate = src
                
                if best_candidate:
                    extracted_image_url = best_candidate
                    # print(f"  > Found better Mashreq image: {extracted_image_url}")

            except Exception as e:
                print(f"  Error applying Mashreq logic: {e}")

    except Exception as e:
        print(f"  Error extracting image: {e}")
        
    return extracted_image_url

def update_image_in_db(database_file, card_data, image_url):
    """Saves the found image URL to the database."""
    if not image_url:
        return

    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
    INSERT INTO card_images (card_id, bank_name, card_name, scraper_image_url, scraper_date, card_url)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(card_id) DO UPDATE SET
        scraper_image_url = excluded.scraper_image_url,
        scraper_date = excluded.scraper_date,
        card_url = excluded.card_url;
    """
    cursor.execute(sql, (
        card_data['card_id'],
        card_data['bank_name'],
        card_data['card_name'],
        image_url,
        current_time,
        card_data['url']
    ))
    conn.commit()
    conn.close()
    print(f"  > Saved Image for: {card_data['card_name']}")

def run_image_updater():
    setup_image_table(db_file)
    cards = get_cards_needing_images(db_file)
    print(f"--- Starting Agent 3: Image Updater ---")
    print(f"Found {len(cards)} cards to check.")

    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)

    try:
        for i, card in enumerate(cards):
            print(f"[{i+1}/{len(cards)}] Visiting: {card['card_name']} ({card['bank_name']})")
            try:
                driver.get(card['url'])
                # Quick wait
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except:
                    pass
                
                image_url = extract_image_url(driver, card['bank_name'], card['url'], card['card_name'])
                
                if image_url:
                    # print(f"  Found: {image_url}")
                    update_image_in_db(db_file, card, image_url)
                else:
                    print("  x No image found.")
                    
            except Exception as e:
                print(f"  Error processing card: {e}")
                
    finally:
        driver.quit()
        print("--- Agent 3 Finished ---")

if __name__ == "__main__":
    run_image_updater()
