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
    """Uses Playwright to correctly target the inner Perchance generator iframe, 

    bypasses obstacles using your token, and downloads the output asset.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Inject cookie state 
        context.add_cookies([{
            "name": "cf_clearance",
            "value": cf_token,
            "domain": ".perchance.org",
            "path": "/"
        }])
        
        page = context.new_page()
        print("Navigating to Perchance generator interface...")
        page.goto("https://perchance.org", wait_until="networkidle")
        
        # STEP 1: Locate and attach to the primary interaction iframe element
        print("Scanning for the interactive generation frame elements...")
        page.wait_for_selector("iframe", timeout=20000)
        
        # Target the specific platform generator frame
        generator_frame = None
        for frame in page.frames:
            if "ai-text-to-image-generator" in frame.url or "perchance" in frame.url:
                generator_frame = frame
                break
                
        # Fallback to the first available content frame if named URL routing differs
        if not generator_frame and len(page.frames) > 1:
            generator_frame = page.frames[1]
        elif not generator_frame:
            generator_frame = page.main_frame

        print("Frame isolated. Interacting with input targets inside the frame context...")
        
        # STEP 2: Use highly descriptive fallback combinations to find the prompt area
        # This checks for placeholders, generic inputs, or textareas inside the isolated frame
        input_selector = "textarea, input[placeholder*='prompt'], [contenteditable='true']"
        generator_frame.wait_for_selector(input_selector, timeout=25000)
        
        # Clear out existing template text and type the fresh trend prompt
        generator_frame.focus(input_selector)
        generator_frame.fill(input_selector, "")
        generator_frame.type(input_selector, image_prompt, delay=50)
        
        # STEP 3: Click the target generation trigger
        button_selector = "button:has-text('Generate'), button:has-text('generate'), #generate-button"
        generator_frame.wait_for_selector(button_selector, timeout=10000)
        generator_frame.click(button_selector)
        print("Generation triggered successfully. Compiling image output...")
        
        # STEP 4: Wait for the image tag to compile down to a viewable source file
        output_img_selector = "div.output-image-container img, img[src*='perchance'], #output img"
        generator_frame.wait_for_selector(output_img_selector, timeout=60000)
        
        img_element = generator_frame.locator(output_img_selector).first
        img_src = img_element.get_attribute("src")
        
        if not img_src:
            raise Exception("Failed to scrape valid image source attribute from frame output grid.")

        # Download the completed design file asset
        print(f"Downloading finished design asset from source link: {img_src}")
        headers = {"User-Agent": "Mozilla/5.0"}
        img_data = requests.get(img_src, headers=headers, timeout=20).content
        
        filename = f"{GEN_DIR}/design_{random.randint(1000,9999)}.jpg"
        with open(filename, "wb") as f:
            f.write(img_data)
        
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
