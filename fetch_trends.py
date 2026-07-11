import os
import time
import requests
from datetime import datetime

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
LOCAL_PERPLEXICA_API = "http://localhost:3001/api/search"
LOCAL_HEALTH_CHECK = "http://localhost:3001/api/status" # Adjust if your version uses a different health endpoint

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def wait_for_perplexica(timeout_seconds=120):
    """Loops and verifies if the local Perplexica container is awake before querying."""
    print("Waiting for local Perplexica container to initialize...")
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        try:
            # Fallback to checking the base port if /status isn't configured
            response = requests.get("http://localhost:3001", timeout=5)
            if response.status_code < 500:
                print("Perplexica Core is up and responding!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(5)
    print("Timeout: Perplexica Core failed to start in time.")
    return False

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_history(search_term):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{search_term}\n")

def get_trends_from_engine():
    """Queries the local search stack for trending structural keywords."""
    prompt = "trending designs redbubble teepublic etsy amazon best sellers pinterest posters logos"
    payload = {
        "query": prompt,
        "focusMode": "webSearch"
    }
    try:
        res = requests.post(LOCAL_PERPLEXICA_API, json=payload, timeout=30)
        if res.status_code == 200:
            data = res.json()
            # Extract names from metadata sources fetched by the engine
            sources = data.get("sources", [])
            for source in sources:
                title = source.get("title", "").strip()
                if title:
                    # Clean up string to serve as a keyword phrase
                    short_title = " ".join(title.split()[:4])
                    return short_title
        return None
    except Exception as e:
        print(f"Error querying search layer: {e}")
        return None

def download_trend_image(keyword):
    print(f"Attempting to discover unique image reference for: {keyword}")
    payload = {
        "query": f"{keyword} product image design filetype:jpg",
        "focusMode": "webSearch"
    }
    try:
        res = requests.post(LOCAL_PERPLEXICA_API, json=payload, timeout=30)
        if res.status_code != 200:
            return False
            
        sources = res.json().get("sources", [])
        image_url = None
        
        # Look for images indexed by the local crawler engine
        for src in sources:
            url = src.get("url", "")
            if any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                image_url = url
                break
                
        if not image_url and sources:
            # Fallback strategy: download target page imagery if direct resource link isn't parsed
            image_url = sources[0].get("url")
            
        if image_url:
            img_res = requests.get(image_url, stream=True, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if img_res.status_code == 200:
                clean_name = "".join(c for c in keyword if c.isalnum() or c in (' ', '_')).rstrip()
                filename = f"{IMAGE_FOLDER}/{clean_name.replace(' ', '_')}_{int(time.time())}.jpg"
                with open(filename, 'wb') as f:
                    for chunk in img_res.iter_content(1024):
                        f.write(chunk)
                print(f"Saved reference design image: {filename}")
                return True
        return False
    except Exception as e:
        print(f"Download sequencing error: {e}")
        return False

def main():
    if not wait_for_perplexica():
        return
        
    history = load_history()
    max_attempts = 10
    
    for _ in range(max_attempts):
        detected_trend = get_trends_from_engine()
        if not detected_trend:
            print("Engine returned empty indexing matrix. Retrying loop...")
            time.sleep(2)
            continue
            
        if detected_trend in history:
            print(f"Skipping duplicate context: '{detected_trend}'")
            continue
            
        if download_trend_image(detected_trend):
            save_to_history(detected_trend)
            print("Successfully processed target workflow item.")
            break
    else:
        print("Completed processing loops. No new unique image sets were found today.")

if __name__ == "__main__":
    main()
