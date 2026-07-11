import os
import time
import random
import requests
from datetime import datetime

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
# Targeting the newly exposed backend gateway port
SEARXNG_API_URL = "http://localhost:8888/search"

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
    platforms = ["redbubble", "etsy", "teepublic", "amazon best sellers", "pinterest trend"]
    niches = ["retro logo design", "funny typography poster", "minimalist aesthetic graphic", "vintage vector art"]
    return f"trending {random.choice(platforms)} {random.choice(niches)}"

def run_automation_workflow():
    history = load_history()
    max_pipeline_attempts = 5
    
    for _ in range(max_pipeline_attempts):
        search_query = get_target_trends()
        
        if search_query in history:
            continue
            
        print(f"Querying unblocked engine gateway for: '{search_query}'")
        
        params = {
            "q": search_query,
            "format": "json",
            "categories": "images"
        }
        
        try:
            response = requests.get(SEARXNG_API_URL, params=params, timeout=20)
            if response.status_code != 200:
                print(f"Search indexer rejected query (Status {response.status_code}). Advancing loop...")
                continue
                
            results = response.json().get("results", [])
            if not results:
                print("No active images found for this category niche. Retrying...")
                continue
                
            # Iterate through the returned raw image URLs from the query loop
            for image_metadata in results:
                image_url = image_metadata.get("img_src") or image_metadata.get("url")
                
                if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    print(f"Discovered matching design image: {image_url}")
                    
                    img_response = requests.get(image_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                    if img_response.status_code == 200:
                        clean_title = "".join(c for c in search_query if c.isalnum() or c in (' ', '_')).rstrip()
                        filename = f"{IMAGE_FOLDER}/{clean_title.replace(' ', '_')}_{int(time.time())}.jpg"
                        
                        with open(filename, 'wb') as file_handler:
                            file_handler.write(img_response.content)
                            
                        save_to_history(search_query)
                        print(f"Successfully downloaded asset to: {filename}")
                        return True
                        
        except Exception as error:
            print(f"Skipping volatile loop point: {error}")
            time.sleep(2)
            
    print("Automation loop exhausted without tracking any new content today.")
    return False

def main():
    print("Initializing customized scraping routine...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
