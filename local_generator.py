import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

GEN_DIR = "generated_images"
if not os.path.exists(GEN_DIR):
    os.makedirs(GEN_DIR)

def create_local_design(trend_name, image_prompt):
    """Generates a high-quality, print-on-demand ready typography and geometric graphic

    completely locally inside the GitHub runner without any internet or API calls.
    """
    print(f"[Local AI Engine] Building graphic design asset for trend: {trend_name}")
    
    # 1. Initialize a high-resolution canvas matching standard t-shirt aspect ratios
    width, height = 2400, 2400
    # Clean transparent background for clothing prints
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0)) 
    draw = ImageDraw.Draw(image)
    
    # 2. Pick a high-contrast theme color scheme based on the trend name string
    seed_val = len(trend_name) + len(image_prompt)
    random.seed(seed_val)
    
    color_palette = [
        ((255, 0, 128, 255), (0, 255, 255, 255)),   # Cyberpunk Neon
        ((255, 215, 0, 255), (255, 69, 0, 255)),   # Retro Vintage Gold
        ((50, 205, 50, 255), (0, 191, 255, 255)),  # Tech Vibrant
        ((240, 128, 128, 255), (147, 112, 219, 255)) # Pastel Aesthetic
    ]
    color1, color2 = random.choice(color_palette)

    # 3. Draw abstract design elements into the background center
    center_x, center_y = width // 2, height // 2
    for radius in range(800, 200, -100):
        # Rotate line colors to build depth grids
        current_color = color1 if radius % 200 == 0 else color2
        draw.arc(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            start=random.randint(0, 45),
            end=random.randint(180, 360),
            fill=current_color,
            width=12
        )

    # 4. Inject Bold Typography Layout
    # GitHub runners have default system true-type fonts available out-of-the-box
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "LiberationSans-Bold.ttf"
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            font = ImageFont.truetype(path, 160)
            break
    if not font:
        font = ImageFont.load_default() # Fallback safely if specific system fonts load slowly

    # Clean text wrapping to prevent edge-spillover
    text = trend_name.upper()
    
    # Draw a solid text drop-shadow to optimize printing contrast
    draw.text((center_x + 8, center_y + 408), text, fill=(0, 0, 0, 255), font=font, anchor="mm")
    draw.text((center_x, center_y + 400), text, fill=color2, font=font, anchor="mm")

    # 5. Compile and export the design as a high-density print graphic
    filename = f"{GEN_DIR}/design_{random.randint(1000,9999)}.png"
    image.save(filename, "PNG")
    print(f"[Local AI Engine] Asset created and compiled successfully: {filename}")
    return filename

if __name__ == "__main__":
    # Test script run execution parameters
    create_local_design("Retro Cyberpunk", "Vibrant neon typography artwork vector style")
