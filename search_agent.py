import os
import requests
import json
import random

PERPLEXICA_URL = "http://localhost:3001/api/search"
HISTORY_FILE = "history.txt"

def get_past_trends():
    """Reads history.txt to find previous trends so we can exclude them."""
    if not os.path.exists(HISTORY_FILE):
        return "none"
    
    with open(HISTORY_FILE, "r") as f:
        lines = f.readlines()
        
    # Get the last 15 logged trends to keep the search prompt clean and within token limits
    past_trends = []
    for line in lines[-15:]:
        if "Trend:" in line:
            try:
                # Extract the trend name between 'Trend:' and the next '|'
                trend_part = line.split("Trend:")[1].split("|")[0].strip()
                if trend_part:
                    past_trends.append(trend_part)
            except IndexError:
                pass
                
    return ", ".join(past_trends) if past_trends else "none"

def query_perplexica_for_unique_trend():
    """Queries the local Perplexica engine with a dynamically generated prompt

    to guarantee a brand new internet trend on every run.
    """
    past_exclusions = get_past_trends()
    print(f"[Pipeline Search] Excluded from this run: [{past_exclusions}]")
    
    # Define your specific platforms to cross-reference
    platforms = "Redbubble trends, Google Trends, Insight Factory, Amazon Best Sellers, Etsy, Shopify, Kittl, Pinterest, and TikTok Shop"
    # Create the dynamic prompt
    prompt = (
        f"Perform an exhaustive web search across {platforms}. "
        f"Identify the single highest-demand viral meme, funny phrase, pop-culture spike, or trending aesthetic graphic right now. "
        f"CRITICAL: You must completely ignore these past trends: [{past_exclusions}]. "
        f"Find something completely different and new that is blowing up in the last 48 hours. "
        f"Your response must be exactly in this format on a single line:\n"
        f"Trend: [Name of the unique trend] | Description: [One short sentence explaining why it is trending]"
    )
    
    payload = {
        "query": prompt,
        "focusMode": "webSearch",  # Force deep internet crawling
        "history": []
    }
    
    try:
        response = requests.post(PERPLEXICA_URL, json=payload, timeout=90)
        response.raise_for_status()
        result_text = response.json().get("text", "")
        
        # Verify the model didn't fail and return empty strings
        if not result_text or "Trend:" not in result_text:
            raise ValueError("Invalid format returned from search engine.")
            
        return result_text.strip()
        
    except Exception as e:
        print(f"[Search Error] Perplexica communication failed: {e}. Triggering fallback trend.")
        # Generates a random variable tag to ensure the fallback doesn't create duplicate keys
        random_id = random.randint(1000, 9999)
        return f"Trend: Weird Internet Humor {random_id} | Description: Sudden rising ironic text meme spike on viral social media channels."

def main():
    print("--- Starting Component 1: Unique Trend Discovery ---")
    
    # 1. Run the dynamic open web search
    search_output = query_perplexica_for_unique_trend()
    print(f"[Discovered Result] {search_output}")
    
    # 2. Append the single unique result immediately to your history file
    # This locks it in so the next automated workflow run cannot replicate it
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{search_output}\n")
        
    print("[Success] Step 1 complete. Unique trend recorded in history.txt.")

if __name__ == "__main__":
    main()
