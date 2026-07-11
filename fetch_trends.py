import os
import requests
import json
from datetime import datetime

# Configuration
HISTORY_FILE = "history.txt"
IMAGE_FOLDER = "downloaded_images"
# Replace with your Perplexica or fallback Search API endpoint
API_URL = os.getenv("PERPLEXICA_API_URL", "http://localhost:3001/api/search") 

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_history(search_term):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{search_term}\n")

def fetch_trending_term():
    """
    Asks the AI engine to find a trending Print-on-Demand (POD) product design topic.
    """
    prompt = (
        "Identify one highly specific trending design, logo, poster, or product topic "
        "currently popular or best-selling on platforms like Redbubble, Etsy, Amazon Best Sellers, "
        "Teepublic, Pinterest, and Google Trends. Return ONLY the name of the trend/phrase, "
        "nothing else. Do not include quotes."
    )
    
    payload = {
        "query": prompt,
        "focusMode": "webSearch" # Adjust based on Perplexica's specific API documentation
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            # Adjust JSON parsing depending on your Perplexica API response structure
            trend = response.json().get("text", "").strip()
            return trend
        return None
    except Exception as e:
        print(f"Error fetching trend from AI: {e}")
        return None

def download_image(search_term):
    """
    Searches for an image URL for the specific term and downloads it.
    """
    print(f"Searching image for: {search_term}")
    
    # Querying for an image link using the search backend
    image_query = f"{search_term} trending design product photo"
    payload = {"query": image_query, "focusMode": "webSearch"}
    
    try:
        res = requests.post(API_URL, json=payload, timeout=30)
        # Assuming the AI engine returns source links in the response
        data = res.json()
        
        # Fallback/Target: Extract the first image link from the search engine's context metadata
        sources = data.get("sources", [])
        image_url = None
        
        for source in sources:
            url = source.get("url", "")
            if url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                image_url = url
                break
        
        if not image_url:
            print("No direct image URL found in sources. Skipping.")
            return False

        # Download the image
        img_res = requests.get(image_url, stream=True, timeout=15)
        if img_res.status_code == 200:
            clean_name = "".join(c for c in search_term if c.isalnum() or c in (' ', '_')).rstrip()
            filename = f"{IMAGE_FOLDER}/{clean_name.replace(' ', '_')}_{int(datetime.timestamp(datetime.now()))}.jpg"
            
            with open(filename, 'wb') as f:
                for chunk in img_res.iter_content(1024):
                    f.write(chunk)
            print(f"Successfully downloaded: {filename}")
            return True
            
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False

def main():
    history = load_history()
    max_attempts = 5
    
    for attempt in range(max_attempts):
        trend = fetch_trending_term()
        if not trend:
            print("Could not retrieve a trend. Retrying...")
            continue
            
        if trend in history:
            print(f"'{trend}' already exists in history.txt. Searching for a new trend...")
            continue
            
        # If it's a new trend, attempt download
        success = download_image(trend)
        if success:
            save_to_history(trend)
            break
    else:
        print("Reached maximum attempts without finding a new unique trend.")

if __name__ == "__main__":
    main()
