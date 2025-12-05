import re
from urllib.parse import unquote, urlparse, parse_qs

# The HTML snippet for World Card provided by user (reconstructed)
# src="/_next/image?url=https%3A%2F%2Fwww.rakbank.ae%2Fglobalassets%2Frakbank%2Fglobal%2Fall-cards%2Ffinal-card-images%2Fcopy-of-credit-card---world-1.png&amp;w=3840&amp;q=75"
# Note: The user's snippet had "https://www.rakbank.ae/..." encoded.

html_tag = '<img alt="card" src="/_next/image?url=https%3A%2F%2Fwww.rakbank.ae%2Fglobalassets%2Frakbank%2Fglobal%2Fall-cards%2Ffinal-card-images%2Fcopy-of-credit-card---world-1.png&amp;w=3840&amp;q=75" decoding="async" data-nimg="fill" class="custom-img" sizes="100vw" srcset="/_next/image?url=https%3A%2F%2Fwww.rakbank.ae%2Fglobalassets%2Frakbank%2Fglobal%2Fall-cards%2Ffinal-card-images%2Fcopy-of-credit-card---world-1.png&amp;w=640&amp;q=75 640w">'

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
                print(f"Target URL from srcset: {target_url}")
                
                # Handle Next.js optimized images
                if "/_next/image" in target_url:
                    target_url = target_url.replace("&amp;", "&")
                    parsed = urlparse(target_url)
                    qs = parse_qs(parsed.query)
                    if 'url' in qs:
                        extracted = qs['url'][0]
                        print(f"Extracted 'url' param: {extracted}")
                        
                        # If relative, prepend domain
                        if extracted.startswith("/"):
                            return f"https://www.rakbank.ae{extracted}"
                        return extracted
                else:
                    return target_url
    except Exception as e:
        print(f"Error: {e}")
    return None

print("--- Debugging ---")
result = extract_nextjs_url(html_tag)
print(f"Result: {result}")
