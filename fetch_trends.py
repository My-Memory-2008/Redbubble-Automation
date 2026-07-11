import os
import re
import time
import random
import requests
import urllib.parse

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
OUTPUT_FILENAME = f"{IMAGE_FOLDER}/current_trend.jpg"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_history(search_term):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{search_term}\n")

def get_target_trends():
    # Covers every source platform requested in your blueprint
    platforms = [
        "redbubble trending", 
        "etsy best sellers art", 
        "teepublic trends", 
        "amazon best sellers pod", 
        "pinterest aesthetic trend", 
        "insightfactory pod", 
        "kitto graphic design"
    ]
    niches = [
        "retro typography logo", 
        "funny viral poster design", 
        "minimalist line art aesthetic", 
        "vintage vector graphic", 
        "90s bootleg rap tee layout",
        "cottagecore aesthetic pattern"
    ]
    return f"{random.choice(platforms)} {random.choice(niches)}"

def run_automation_workflow():
    history = load_history()
    max_pipeline_attempts = 10
    
    # Using an Android Mobile user agent forces Google to serve basic, unblocked lightweight HTML layouts
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }

    for attempt in range(max_pipeline_attempts):
        search_query = get_target_trends()
        
        if search_query in history:
            continue
            
        print(f"[{attempt + 1}/{max_pipeline_attempts}] Querying Unblocked Core Engine for: '{search_query}'")
        
        # Build an authentic Google Mobile Image search parameter string
        encoded_query = urllib.parse.quote_plus(search_query)
        google_url = f"https://google.com{encoded_query}&tbm=isch&asearch=ichunk&async=_id:rg_s,_pms:s,_fmt:pc"
        
        try:
            response = requests.get(google_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Engine busy (Status {response.status_code}). Advancing loop...")
                continue
                
            # Isolate direct image links out of the raw response layout strings
            html_content = response.text
            raw_links = re.findall(r'imgurl=(.*?)(?:&amp;|\")', html_content)
            
            valid_urls = []
            for url in raw_links:
                decoded_url = urllib.parse.unquote(url)
                if decoded_url.startswith("http") and any(decoded_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    valid_urls.append(decoded_url)
            
            if not valid_urls:
                print("No clear design image extensions located in this canvas layer. Retrying...")
                continue
                
            # Take the highest ranking search item link matched by the aggregator
            target_image_url = valid_urls[0]
            print(f"Isolating trending design asset: {target_image_url}")
            
            # Download the actual image file bytes using standard browser emulation
            browser_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            img_response = requests.get(target_image_url, timeout=12, headers=browser_headers)
            
            if img_response.status_code == 200:
                # Overwrites the target file instantly
                with open(OUTPUT_FILENAME, 'wb') as file_handler:
                    file_handler.write(img_response.content)
                    
                save_to_history(search_query)
                print(f"🎯 Success! Downloaded and overwrote asset: {OUTPUT_FILENAME}")
                return True
                
        except Exception as error:
            print(f"Skipping unstable network target coordinate: {error}")
            time.sleep(2)
            
    print("Automation array exhausted without matching unique content loops today.")
    return False

def main():
    print("Initializing high-availability scraping matrix...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
