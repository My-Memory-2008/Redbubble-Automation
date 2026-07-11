import os
import time
import random
import requests

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
# Fixed filename so that it overwrites every single time
OUTPUT_FILENAME = f"{IMAGE_FOLDER}/current_trend.jpg"
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
            
        print(f"Querying search layer directly for: '{search_query}'")
        
        params = {
            "q": search_query,
            "format": "json",
            "categories": "images"
        }
        
        try:
            response = requests.get(SEARXNG_API_URL, params=params, timeout=20)
            if response.status_code != 200:
                print(f"Engine rejected query (Status {response.status_code}). Advancing loop...")
                continue
                
            results = response.json().get("results", [])
            if not results:
                print("No image data found for this keyword phrase. Retrying...")
                continue
                
            for image_metadata in results:
                image_url = image_metadata.get("img_src") or image_metadata.get("url")
                
                if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    print(f"Discovered matching design link: {image_url}")
                    
                    # Request the actual image bytes safely
                    img_response = requests.get(image_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                    if img_response.status_code == 200:
                        
                        # Overwrites 'current_trend.jpg' instantly on every successful execution
                        with open(OUTPUT_FILENAME, 'wb') as file_handler:
                            file_handler.write(img_response.content)
                            
                        save_to_history(search_query)
                        print(f"Successfully downloaded and overwrote asset: {OUTPUT_FILENAME}")
                        return True
                        
        except Exception as error:
            print(f"Loop error encounter: {error}")
            time.sleep(2)
            
    print("Automation loop exhausted without tracking any new content today.")
    return False

def main():
    print("Initializing isolated scraper workflow...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
