import os
import time
import requests
import subprocess
from datetime import datetime

HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
LOCAL_PERPLEXICA_API = "http://localhost:3001/api/search"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def wait_for_perplexica(timeout_seconds=180):
    """Loops and validates if the Perplexica port is reachable, printing container stats if failing."""
    print("Waiting for local Perplexica container map to stabilize...")
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        try:
            # Check if the API port interface is accepting network connection sockets
            response = requests.get("http://localhost:3001/api/models", timeout=3)
            if response.status_code < 500:
                print("Perplexica API Engine is fully active and reachable!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(5)
        
    print("\n❌ Timeout: Perplexica Core failed to respond on port 3001 within the window.")
    print("--- Debugging Container System Status ---")
    try:
        # Diagnostic printing to catch compilation or startup loop crashes
        print(subprocess.check_output("docker ps -a", shell=True).decode())
        print(subprocess.check_output("docker compose -f perplexica-core/docker-compose.yaml logs --tail=20", shell=True).decode())
    except Exception as debug_error:
        print(f"Could not fetch container logs: {debug_error}")
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
    """Queries the local search engine interface directly for trending keywords."""
    prompt = "trending designs redbubble teepublic etsy amazon best sellers pinterest posters logos"
    payload = {
        "query": prompt,
        "focusMode": "webSearch",
        "optimizationMode": "speed",
        "history": []
    }
    try:
        res = requests.post(LOCAL_PERPLEXICA_API, json=payload, timeout=45)
        if res.status_code == 200:
            data = res.json()
            sources = data.get("sources", [])
            for source in sources:
                title = source.get("title", "").strip()
                if title and len(title.split()) > 2:
                    return " ".join(title.split()[:4])
        return None
    except Exception as e:
        print(f"Error querying search stack: {e}")
        return None

def download_trend_image(keyword):
    print(f"Attempting image resolution for: {keyword}")
    payload = {
        "query": f"{keyword} product photography layout reference design",
        "focusMode": "webSearch",
        "optimizationMode": "speed",
        "history": []
    }
    try:
        res = requests.post(LOCAL_PERPLEXICA_API, json=payload, timeout=45)
        if res.status_code != 200:
            return False
            
        sources = res.json().get("sources", [])
        image_url = None
        
        for src in sources:
            url = src.get("url", "")
            if any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                image_url = url
                break
                
        if not image_url and sources:
            # Fallback to the first available parsed link from the crawler context array
            image_url = sources[0].get("url")
            
        if image_url:
            print(f"Targeting download URL: {image_url}")
            img_res = requests.get(image_url, stream=True, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            if img_res.status_code == 200:
                clean_name = "".join(c for c in keyword if c.isalnum() or c in (' ', '_')).rstrip()
                filename = f"{IMAGE_FOLDER}/{clean_name.replace(' ', '_')}_{int(time.time())}.jpg"
                with open(filename, 'wb') as f:
                    for chunk in img_res.iter_content(1024):
                        f.write(chunk)
                print(f"Successfully processed image file: {filename}")
                return True
        return False
    except Exception as e:
        print(f"Image saving sequence interrupted: {e}")
        return False

def main():
    if not wait_for_perplexica():
        return
        
    history = load_history()
    max_attempts = 5
    
    for _ in range(max_attempts):
        detected_trend = get_trends_from_engine()
        if not detected_trend:
            print("Engine returned empty matrix. Retrying sequence...")
            time.sleep(5)
            continue
            
        if detected_trend in history:
            print(f"Skipping known trend: '{detected_trend}'")
            continue
            
        if download_trend_image(detected_trend):
            save_to_history(detected_trend)
            print("Workflow run completed successfully.")
            break
    else:
        print("Workflow completed processing iterations. No new unique designs resolved.")

if __name__ == "__main__":
    main()
