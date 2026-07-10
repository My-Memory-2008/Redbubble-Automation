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
    """Uses Playwright to interact directly with the main Perchance page layouts,

    bypassing iframe dependencies to avoid visibility timeouts.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # Inject cookie token to bypass Cloudflare gates smoothly
        context.add_cookies([{
            "name": "cf_clearance",
            "value": cf_token,
            "domain": ".perchance.org",
            "path": "/"
        }])
        
        page = context.new_page()
        print("Navigating directly to Perchance user interface...")
        page.goto("https://perchance.org", wait_until="networkidle")
        
        # STEP 1: Target the main-page element input arrays directly
        print("Locating text prompt areas on main body layer...")
        
        # A resilient selector that catches naked textareas, textareas by ID, or textareas by custom placeholders
        input_selector = "textarea, #prompt-input, textarea[placeholder*='prompt'], [contenteditable='true']"
        page.wait_for_selector(input_selector, timeout=25000)
        
        # Clear out default placeholder examples and enter our fresh trend prompt
        page.focus(input_selector)
        page.fill(input_selector, "")
        page.type(input_selector, image_prompt, delay=40)
        print(f"Prompt successfully written: {image_prompt}")
        
        # STEP 2: Find and trigger the generation action button on the main layout
        button_selector = "button:has-text('Generate'), button:has-text('generate'), button[id*='generate']"
        page.wait_for_selector(button_selector, timeout=10000)
        page.click(button_selector)
        print("Generation initialized. Waiting for image canvas processing...")
        
        # STEP 3: Wait for the compiled output image asset to generate an address
        # Perchance dynamically updates the internal img tag once rendering is complete
        output_img_selector = "div.output-image-container img, img[src*='perchance'], #output img, .image-container img"
        page.wait_for_selector(output_img_selector, timeout=60000)
        
        img_element = page.locator(output_img_selector).first
        img_src = img_element.get_attribute("src")
        
        if not img_src:
            raise Exception("Failed to find a valid image source address inside the DOM output grid.")

        # STEP 4: Download and save the final design asset 
        print(f"Downloading finished design asset: {img_src}")
        headers = {"User-Agent": "Mozilla/5.0"}
        img_data = requests.get(img_src, headers=headers, timeout=20).content
        
        filename = f"{GEN_DIR}/design_{random.randint(1000,9999)}.jpg"
        with open(filename, "wb") as f:
            f.write(img_data)
        
        print(f"Success! Image saved to: {filename}")
        browser.close()
        return filename
        
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
