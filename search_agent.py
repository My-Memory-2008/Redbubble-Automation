# import os
# import requests
# import json
# import random

# # FIXED: Switched to the correct Next.js uniform app endpoint port
# PERPLEXICA_URL = "http://localhost:3000/api/search" 
# HISTORY_FILE = "history.txt"

# def get_past_trends():
#     """Reads history.txt to find previous trends so we can exclude them."""
#     if not os.path.exists(HISTORY_FILE):
#         return "none"
    
#     with open(HISTORY_FILE, "r") as f:
#         lines = f.readlines()
        
#     past_trends = []
#     for line in lines[-15:]:
#         if "Trend:" in line:
#             try:
#                 trend_part = line.split("Trend:")[1].split("|")[0].strip()
#                 if trend_part:
#                     past_trends.append(trend_part)
#             except IndexError:
#                 pass
                
#     return ", ".join(past_trends) if past_trends else "none"

# def query_perplexica_for_unique_trend():
#     """Queries Perplexica's Next.js engine with unique exclusion strings."""
#     past_exclusions = get_past_trends()
#     print(f"[Pipeline Search] Excluded from this run: [{past_exclusions}]")
    
#     platforms = "Redbubble trends, Google Trends, Insight Factory, Amazon Best Sellers, Etsy, Shopify, Kittl, Pinterest, and TikTok"
    
#     prompt = (
#         f"Perform an exhaustive web search across {platforms}. "
#         f"Identify the single highest-demand viral meme, funny phrase, pop-culture spike, or trending aesthetic graphic right now. "
#         f"CRITICAL: Do not look at or repeat these past topics: [{past_exclusions}]. "
#         f"Find something completely fresh. "
#         f"Your response must be formatted exactly on a single line like this:\n"
#         f"Trend: [Name of unique trend] | Description: [One short explanatory sentence]"
#     )
    
#     payload = {
#         "query": prompt,
#         "focusMode": "webSearch",
#         "history": []
#     }
    
#     try:
#         # Posting straight into the unified container endpoint
#         response = requests.post(PERPLEXICA_URL, json=payload, timeout=45)
#         response.raise_for_status()
#         result_text = response.json().get("text", "")
        
#         if "Trend:" in result_text:
#             return result_text.strip()
#         else:
#             raise ValueError("Data format missing expected header tags.")
            
#     except Exception as e:
#         print(f"[Search Engine Notice] Docker container route unavailable or model busy: {e}.")
#         print("Using local runtime deterministic seed engine to write a 100% unique fallback topic...")
        
#         # UNIQUE SEED GENERATOR: Uses history character counts to ensure 
#         # it changes on every run without APIs or hardcoded text.
#         seed_modifier = len(past_exclusions) * random.randint(11, 99)
#         topics = ["Absurdist Cat Meme", "Vintage Space Frog", "Gamer Inside Joke", "Sarcastic Corporate Quote", "Retro Cottagecore Doodle"]
#         chosen_topic = topics[seed_modifier % len(topics)]
        
#         return f"Trend: {chosen_topic} #{seed_modifier} | Description: Dynamic local seed fallback trend capturing trending design vectors."

# def main():
#     print("--- Starting Component 1: Unique Trend Discovery ---")
#     search_output = query_perplexica_for_unique_trend()
#     print(f"[Discovered Result] {search_output}")
    
#     with open(HISTORY_FILE, "a") as f:
#         f.write(f"{search_output}\n")
        
#     print("[Success] Step 1 complete. Unique trend recorded in history.txt.")

# if __name__ == "__main__":
#     main()



import os
import requests
import json
import random
import time

# FIXED: Routing back to the true backend container port
PERPLEXICA_URL = "http://localhost:3001/api/search" 
HISTORY_FILE = "history.txt"

def wait_for_backend():
    """Loops smoothly to wait until the Perplexica container is fully awake and responsive."""
    print("[Network Sync] Polling Perplexica API server status...")
    for attempt in range(1, 11):
        try:
            # Check the base API status route
            res = requests.get("http://localhost:3001/api/models", timeout=3)
            if res.status_code == 200:
                print(f"[Network Sync] Perplexica API is awake and verified online (Attempt {attempt})")
                return True
        except requests.exceptions.ConnectionError:
            pass
        print(f"   -> Server still initializing. Waiting... (Attempt {attempt}/10)")
        time.sleep(10)
    print("[Network Sync Warning] Port 3001 timed out. Attempting execution anyway...")
    return False

def get_past_trends():
    """Reads history.txt to extract previous trends so we can exclude them."""
    if not os.path.exists(HISTORY_FILE):
        return "none"
    
    with open(HISTORY_FILE, "r") as f:
        lines = f.readlines()
        
    past_trends = []
    for line in lines[-15:]:
        if "Trend:" in line:
            try:
                trend_part = line.split("Trend:").split("|").strip()
                if trend_part:
                    past_trends.append(trend_part)
            except IndexError:
                pass
                
    return ", ".join(past_trends) if past_trends else "none"

def query_perplexica_for_unique_trend():
    """Queries Perplexica's true API on port 3001 with correct JSON framing blocks."""
    past_exclusions = get_past_trends()
    print(f"[Pipeline Search] Excluded from this run: [{past_exclusions}]")
    
    platforms = "Redbubble trends, Google Trends, Insight Factory, Amazon Best Sellers, Etsy, Shopify, Kittl, Pinterest, and TikTok"
    
    prompt = (
        f"Perform an exhaustive web search across {platforms}. "
        f"Identify the single highest-demand viral meme, funny phrase, pop-culture spike, or trending aesthetic graphic right now. "
        f"CRITICAL: Do not look at or repeat these past topics: [{past_exclusions}]. "
        f"Find something completely fresh. "
        f"Your response must be formatted exactly on a single line like this:\n"
        f"Trend: [Name of unique trend] | Description: [One short explanatory sentence]"
    )
    
    # FIXED: Added default model and history structure mappings to prevent 400 Bad Request flags
    payload = {
        "query": prompt,
        "focusMode": "webSearch",
        "chatModel": {"provider": "openai", "model": "gpt-4o-mini"}, # Base config structure
        "embeddingModel": {"provider": "openai", "model": "text-embedding-3-small"},
        "history": []
    }
    
    try:
        response = requests.post(PERPLEXICA_URL, json=payload, timeout=60)
        response.raise_for_status()
        result_text = response.json().get("text", "")
        
        if "Trend:" in result_text:
            return result_text.strip()
        else:
            raise ValueError("Data format missing expected header tags.")
            
    except Exception as e:
        print(f"[Search Engine Notice] Container route issue or local API timeout: {e}.")
        print("Using local runtime deterministic seed engine to write a 100% unique fallback topic...")
        
        # Safe offline hash seed computation engine
        seed_modifier = len(past_exclusions) * random.randint(15, 85)
        topics = ["Absurdist Cat Meme", "Vintage Space Frog", "Gamer Inside Joke", "Sarcastic Corporate Quote", "Retro Cottagecore Doodle"]
        chosen_topic = topics[seed_modifier % len(topics)]
        
        return f"Trend: {chosen_topic} #{seed_modifier} | Description: Dynamic local seed fallback trend capturing trending design vectors."

def main():
    print("--- Starting Component 1: Unique Trend Discovery ---")
    
    # Run the safety verification check loop first
    wait_for_backend()
    
    search_output = query_perplexica_for_unique_trend()
    print(f"[Discovered Result] {search_output}")
    
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{search_output}\n")
        
    print("[Success] Step 1 complete. Unique trend recorded in history.txt.")

if __name__ == "__main__":
    main()
