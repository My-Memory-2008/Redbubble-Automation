import os
import time
import random
import requests
from datetime import datetime

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
# Directly leveraging the unlimiter-patched SearXNG backend for rapid image parsing
SEARXNG_API_URL = "http://localhost:8080/search"

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
    """Generates varied platform queries targeting trending designs."""
    platforms = ["redbubble", "etsy", "teepublic", "amazon best sellers", "pinterest trend"]
    niches = ["retro logo design", "funny typography poster", "minimalist aesthetic graphic", "vintage vector art"]
    
    # Generate variations dynamically so you never query the exact same prompt structure
    chosen_platform = random.choice(platforms)
    chosen_niche = random.choice(niches)
    return f"trending {chosen_platform} {chosen_niche}"

def run_automation_workflow():
    history = load_history()
    max_pipeline_attempts = 5
    
    for _ in range(max_pipeline_attempts):
        search_query = get_target_trends()
        
        if search_query in history:
            continue
            
        print(f"Querying search layer for: '{search_query}'")
        
        # We explicitly request image engine schemas to bring back direct image links
        params = {
            "q": search_query,
            "format": "json",
            "categories": "images"
        }
        
        try:
            response = requests.get(SEARXNG_API_URL, params=params, timeout=20)
            if response.status_code != 200:
                print(f"Search indexer rejected query (Status {response.status_code}). Retrying next matrix...")
                continue
                
            results = response.json().get("results", [])
            if not results:
                print("No active images found for this niche selection. Advancing loop...")
                continue
                
            # Grab a valid image resource candidate
            for image_metadata in results:
                image_url = image_metadata.get("img_src") or image_metadata.get("url")
                
                if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    print(f"Found reference asset candidate: {image_url}")
                    
                    # Stream and save the file safely
                    img_response = requests.get(image_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                    if img_response.status_code == 200:
                        clean_title = "".join(c for c in search_query if c.isalnum() or c in (' ', '_')).rstrip()
                        filename = f"{IMAGE_FOLDER}/{clean_title.replace(' ', '_')}_{int(time.time())}.jpg"
                        
                        with open(filename, 'wb') as file_handler:
                            file_handler.write(img_response.content)
                            
                        save_to_history(search_query)
                        print(f"Successfully processed and committed reference image: {filename}")
                        return True
                        
        except Exception as error:
            print(f"Skipping volatile loop point: {error}")
            time.sleep(2)
            
    print("Automation loop exhausted without downloading a new unique asset today.")
    return False

def main():
    print("Initializing customized scraping routine...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
