import os
import re
import time
import random
import requests

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
OUTPUT_FILENAME = f"{IMAGE_FOLDER}/current_trend.jpg"

# Targeting the core internal web server gateway
SEARXNG_URL = "http://127.0.0"

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
    # Covers every requested source platform from your operational layout blueprint
    platforms = [
        "redbubble trending design", 
        "etsy best sellers art", 
        "teepublic top trends", 
        "amazon best sellers pod", 
        "pinterest aesthetic trend", 
        "insightfactory pod graphic", 
        "kitto vector design"
    ]
    niches = [
        "retro typography logo", 
        "funny viral poster", 
        "minimalist line art graphic", 
        "vintage vector layout", 
        "90s bootleg rap tee pattern",
        "cottagecore graphic aesthetic"
    ]
    return f"{random.choice(platforms)} {random.choice(niches)}"

def run_automation_workflow():
    history = load_history()
    max_pipeline_attempts = 10
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(max_pipeline_attempts):
        search_query = get_target_trends()
        
        if search_query in history:
            continue
            
        print(f"[{attempt + 1}/{max_pipeline_attempts}] Scanning SearXNG Core Grid for: '{search_query}'")
        
        # Pulling the raw unblocked structural html engine view to bypass JSON blocks completely
        params = {
            "q": search_query,
            "categories": "images",
            "safesearch": "1"
        }
        
        try:
            response = requests.get(SEARXNG_URL, params=params, headers=headers, timeout=25)
            if response.status_code != 200:
                print(f"SearXNG local core busy (Status {response.status_code}). Advancing loop...")
                continue
            
            # Use string parsing patterns to isolate design asset links from SearXNG image elements
            html_content = response.text
            image_urls = re.findall(r'src="([^"]+)"', html_content)
            image_urls += re.findall(r'href="([^"]+\.(?:jpg|jpeg|png|webp))"', html_content, re.IGNORECASE)
            
            # Clean and filter image matches
            valid_urls = []
            for url in image_urls:
                if "proxy" in url or "searxng" in url:
                    continue
                if any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    valid_urls.append(url)

            if not valid_urls:
                print("No unique asset markers located in current engine layout canvas. Retrying...")
                continue
                
            # Target the topmost matching design asset returned by the multi-engine aggregator
            target_image_url = valid_urls[0]
            print(f"Isolating trending design item asset link: {target_image_url}")
            
            img_response = requests.get(target_image_url, timeout=15, headers=headers)
            if img_response.status_code == 200:
                # Instantly overwrites the target file to prevent repository bloat
                with open(OUTPUT_FILENAME, 'wb') as file_handler:
                    file_handler.write(img_response.content)
                    
                save_to_history(search_query)
                print(f"🎯 Overwrite Operation Complete! Saved reference file: {OUTPUT_FILENAME}")
                return True
                        
        except Exception as error:
            print(f"Skipping volatile extraction coordinate: {error}")
            time.sleep(2)
            
    print("Automation array exhausted without matching unique content loops today.")
    return False

def main():
    print("Initializing SearXNG aggregate crawling matrix...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
