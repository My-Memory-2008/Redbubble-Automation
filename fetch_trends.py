import os
import time
import random
import requests

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
OUTPUT_FILENAME = f"{IMAGE_FOLDER}/current_trend.jpg"

# Pool of public SearXNG instances that support clean, raw extraction
SEARXNG_POOL = [
    "https://searx.be",
    "https://ononoki.org",
    "https://baresearch.org",
    "https://priv.au"
]

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
    # Targets all printing design platforms in your prompt
    platforms = [
        "redbubble trending", 
        "etsy best sellers art", 
        "teepublic trends", 
        "amazon best sellers pod", 
        "pinterest aesthetic trend", 
        "insightfactory pod design", 
        "kitto vector graphic"
    ]
    niches = [
        "retro typography logo", 
        "funny viral poster", 
        "minimalist line art aesthetic", 
        "vintage vector layout", 
        "90s bootleg rap tee",
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
            
        # Pick a random gateway instance from the reliable pool to disperse traffic
        current_gateway = random.choice(SEARXNG_POOL)
        print(f"[{attempt + 1}/{max_pipeline_attempts}] Querying node {current_gateway} for: '{search_query}'")
        
        params = {
            "q": search_query,
            "format": "json",
            "categories": "images",
            "safesearch": "1"
        }
        
        try:
            response = requests.get(current_gateway, params=params, headers=headers, timeout=20)
            
            # If a public node throttles or sends a bad response, jump to the next one instantly
            if response.status_code != 200 or "results" not in response.text:
                print("Node busy or returned an empty response stack. Swapping target route...")
                continue
                
            results = response.json().get("results", [])
            if not results:
                print("No active images located in this canvas slice. Advancing loop...")
                continue
                
            for image_metadata in results:
                image_url = image_metadata.get("img_src") or image_metadata.get("url")
                
                # Check for direct file signatures
                if image_url and any(image_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    print(f"Found active reference design link: {image_url}")
                    
                    img_response = requests.get(image_url, timeout=12, headers=headers)
                    if img_response.status_code == 200:
                        
                        # Overwrites 'current_trend.jpg' cleanly every single run
                        with open(OUTPUT_FILENAME, 'wb') as file_handler:
                            file_handler.write(img_response.content)
                            
                        save_to_history(search_query)
                        print(f"🎯 Overwrite Operation Complete! Reference file saved: {OUTPUT_FILENAME}")
                        return True
                        
        except Exception as error:
            print(f"Skipping volatile gateway connection point: {error}")
            time.sleep(2)
            
    print("Automation array exhausted without matching unique content loops today.")
    return False

def main():
    print("Initializing SearXNG aggregate crawling matrix...")
    run_automation_workflow()

if __name__ == "__main__":
    main()
