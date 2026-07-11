import os
import time
import random
import requests
from duckduckgo_search import DDGS

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
    # Covers every source platform you requested
    platforms = ["redbubble", "etsy", "teepublic", "amazon best sellers", "pinterest trend", "insightfactory", "kitto"]
    niches = ["retro logo design", "funny typography poster", "minimalist aesthetic graphic", "vintage vector art", "trending design layout"]
    return f"trending {random.choice(platforms)} {random.choice(niches)}"

def run_automation_workflow():
    history = load_history()
    max_pipeline_attempts = 10
    
    # Initialize the high-speed search extraction matrix
    with DDGS() as ddgs:
        for _ in range(max_pipeline_attempts):
            search_query = get_target_trends()
            
            if search_query in history:
                continue
                
            print(f"Querying unblocked engine matrix for: '{search_query}'")
            
            try:
                # Direct image extraction targeting active layouts
                results = list(ddgs.images(search_query, max_results=10))
                if not results:
                    print("No image data found for this keyword phrase. Advancing loop...")
                    continue
                    
                for image_metadata in results:
                    image_url = image_metadata.get("image")
                    
                    if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                        print(f"Discovered matching production reference asset: {image_url}")
                        
                        # Request the actual image bytes using standard browser impersonation
                        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                        img_response = requests.get(image_url, timeout=15, headers=headers)
                        
                        if img_response.status_code == 200:
                            # Overwrites the target file instantly
                            with open(OUTPUT_FILENAME, 'wb') as file_handler:
                                file_handler.write(img_response.content)
                                
                            save_to_history(search_query)
                            print(f"Successfully downloaded and overwrote trend file: {OUTPUT_FILENAME}")
                            return True
                            
            except Exception as error:
                print(f"Skipping volatile network point: {error}")
                time.sleep(2)
                
    print("Automation loop exhausted without tracking any new content today.")
    return False

def main():
    print("Initializing isolated scraper workflow...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
