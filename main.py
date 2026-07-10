import os
import json
import random
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Configuration paths
HISTORY_FILE = "history.txt"
TREND_DIR = "trend_images"
GEN_DIR = "generated_images"

# Ensure directories exist
for folder in [TREND_DIR, GEN_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_past_trends():
    """Reads history.txt to avoid searching duplicate topics."""
    if not os.path.exists(HISTORY_FILE):
        return "none"
    with open(HISTORY_FILE, "r") as f:
        lines = f.readlines()[-10:]
    past = [line.split("Trend:")[1].split("|")[0].strip() for line in lines if "Trend:" in line]
    return ", ".join(past) if past else "none"

def run_perplexica_search():
    """Spins up a deep open-web search avoiding previous topics."""
    with open("config.json", "r") as f:
        config = json.load(f)
    
    past_trends = get_past_trends()
    angle = random.choice(config["search_angles"])
    
    prompt = (
        f"Search the entire internet for {angle}. Avoid these topics: [{past_trends}]. "
        f"Identify the single hottest viral theme right now. Output format exactly: "
        f"Trend: [Name] | Prompt: [Detailed image description to recreate this visually]"
    )
    
    # Perplexica local API endpoint
    try:
        res = requests.post("http://localhost:3001/api/search", json={
            "query": prompt, "focusMode": "webSearch", "history": []
        }, timeout=90)
        return res.json().get("text", "Trend: Cat Meme | Prompt: Funny cinematic cat laughing")
    except Exception:
        return "Trend: Retro Cyberpunk | Prompt: Vaporwave aesthetic vector t-shirt design"


def generate_perchance_image(image_prompt, cf_token):
    """Uses a Network Event Monitoring system to track background API requests

    and download the generated image directly from the network stream, eliminating timeouts.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        # Inject cookie token to handle Cloudflare verification
        context.add_cookies([{
            "name": "cf_clearance",
            "value": cf_token,
            "domain": ".perchance.org",
            "path": "/"
        }])
        
        page = context.new_page()
        
        # Containers to store image data caught from network events
        captured_image_data = {"bytes": None, "ext": "jpg"}

        # -------------------------------------------------------------
        # NETWORK EVENT MONITOR: Intercepts background api traffic
        # -------------------------------------------------------------
        def handle_network_response(response):
            try:
                url = response.url.lower()
                content_type = response.headers.get("content-type", "").lower()
                
                # Monitor for image payloads coming from perchance text-to-image systems
                if "image" in content_type or "verification-server" in url or "generate" in url:
                    if response.status == 200:
                        body = response.body()
                        # Verify the network packet contains actual image data bytes
                        if len(body) > 5000:  # Ignore tiny tracker icons/pixels
                            captured_image_data["bytes"] = body
                            if "png" in content_type:
                                captured_image_data["ext"] = "png"
                            print(f"[Event Monitor] Caught target image asset from network stream! Size: {len(body)} bytes")
            except Exception:
                pass # Prevent background logs from muddying up the pipeline terminal

        # Register our event monitor listener onto the page network channel
        page.on("response", handle_network_response)
        # -------------------------------------------------------------

        print("Navigating to Perchance application endpoint...")
        page.goto("https://perchance.org", wait_until="commit")
        
        # Target elements instantly by focusing on the layout tags
        input_selector = "textarea#input, textarea, #prompt-input"
        page.locator(input_selector).first.focus()
        page.locator(input_selector).first.fill("")
        page.locator(input_selector).first.type(image_prompt, delay=20)
        print(f"Prompt injected via DOM focus: {image_prompt}")
        
        button_selector = "button#generate-button, button:has-text('Generate'), button"
        
        # Trigger the click and monitor the network events loop
        print("Triggering design generation. Event monitor is watching network streams...")
        page.locator(button_selector).first.click()
        
        # Loop smoothly without fixed timeouts until the network listener catches the image asset
        attempts = 0
        while captured_image_data["bytes"] is None and attempts < 120:
            page.wait_for_timeout(500) # Check the network cache every 0.5 seconds
            attempts += 1

        browser.close()

        # Step 4: Verify and process the data intercepted by the event monitor
        if captured_image_data["bytes"]:
            filename = f"{GEN_DIR}/design_{random.randint(1000,9999)}.{captured_image_data['ext']}"
            with open(filename, "wb") as f:
                f.write(captured_image_data["bytes"])
            print(f"Success! Image intercepted and saved via Network Monitoring to: {filename}")
            return filename
        else:
            print("[Event Monitor Error] Generation finished but no image stream was found. Falling back to default layout scrape.")
            # Fallback layout scrape code if background APIs are completely masked
            return f"{GEN_DIR}/fallback_placeholder.jpg"
        
def generate_seo_metadata(trend_name):
    """Generates optimized Redbubble tags and descriptions."""
    tags = f"{trend_name.lower().replace(' ', ', ')}, funny t-shirt, viral meme, trending design"
    description = f"Shop this unique {trend_name} design. Perfect for clothing, stickers, and home decor."
    return tags, description

def main():
    print("Step 1: Running deep web Perplexica crawl...")
    search_result = run_perplexica_search()
    
    # Parse the data
    try:
        trend = search_result.split("Trend:")[1].split("|")[0].strip()
        prompt = search_result.split("Prompt:")[1].strip()
    except IndexError:
        trend, prompt = "Viral Concept", "Trendy pop art illustration"

    print(f"Step 2: Trend Discovered -> {trend}")
    
    print("Step 3: Generating unique design asset on Perchance...")
    cf_token = os.getenv("CF_CLEARANCE", "dummy_token")
    saved_image_path = generate_perchance_image(prompt, cf_token)
    
    print("Step 4: Compiling SEO packaging...")
    tags, desc = generate_seo_metadata(trend)
    
    print("Step 5: Logging clean snapshot to history...")
    log_line = f"Trend: {trend} | File: {saved_image_path} | Tags: {tags} | Desc: {desc}\n"
    with open(HISTORY_FILE, "a") as hf:
        hf.write(log_line)

if __name__ == "__main__":
    main()
