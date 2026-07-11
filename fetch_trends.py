import os
import time
import random
import requests

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
OUTPUT_FILENAME = f"{IMAGE_FOLDER}/current_trend.jpg"

# Querying a high-availability public SearXNG instance pool to bypass data center blocks
SEARXNG_API_URL = "https://ononoki.org"

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
    # Covers every target source platform specified in your blueprint
    platforms = [
        "redbubble trending", 
        "etsy best sellers", 
        "teepublic trends", 
        "amazon best sellers pod", 
        "pinterest design trends", 
        "insightfactory pod", 
        "kitto graphic"
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
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(max_pipeline_attempts):
        search_query = get_target_trends()
        
        if search_query in history:
            continue
            
        print(f"[{attempt + 1}/10] Querying SearXNG Meta-Engine for: '{search_query}'")
        
        # Structure the query to fetch json metadata from SearXNG's image category engines
        params = {
            "q": search_query,
            "format": "json",
            "categories": "images",
            "safesearch": "1",
            "language": "en"
        }
        
        try:
            response = requests.get(SEARXNG_API_URL, params=params, headers=headers, timeout=25)
            if response.status_code != 200:
                print(f"SearXNG gateway busy (Status {response.status_code}). Trying next variant...")
                continue
                
            results = response.json().get("results", [])
            if not results:
                print("No image data returned from meta-scrapers for this niche. Advancing loop...")
                continue
                
            # Iterate through the gathered engine image arrays
            for image_metadata in results:
                image_url = image_metadata.get("img_src") or image_metadata.get("url")
                
                # Verify we are targeting direct design assets
                if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    print(f"Found active reference design link: {image_url}")
                    
                    # Stream down the image bytes
                    img_response = requests.get(image_url, timeout=15, headers=headers)
                    if img_response.status_code == 200:
                        
                        # Overwrites 'current_trend.jpg' instantly on every successful loop run
                        with open(OUTPUT_FILENAME, 'wb') as file_handler:
                            file_handler.write(img_response.content)
                            
                        save_to_history(search_query)
                        print(f"🎯 Success! Downloaded and overwrote asset: {OUTPUT_FILENAME}")
                        return True
                        
        except Exception as error:
            print(f"Skipping volatile gateway pipeline link: {error}")
            time.sleep(2)
            
    print("Automation loop finished. No new unique trend targets resolved today.")
    return False

def main():
    print("Initializing SearXNG aggregate scraping matrix...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
