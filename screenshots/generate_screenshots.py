"""
Generate placeholder screenshots for the README.
Run the actual application to get real screenshots.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_placeholder_screenshot(filename, title, width=1400, height=900):
    """Create a placeholder screenshot image."""
    img = Image.new('RGB', (width, height), color='#0a0a0f')
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fall back to default
    try:
        title_font = ImageFont.truetype("segoeui.ttf", 48)
        text_font = ImageFont.truetype("segoeui.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Draw title
    bbox = draw.textbbox((0, 0), title, font=title_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, 100), title, fill='#00d4ff', font=title_font)
    
    # Draw info text
    info_text = "[ Screenshot to be captured from running application ]"
    bbox = draw.textbbox((0, 0), info_text, font=text_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, 200), info_text, fill='#a0a0b0', font=text_font)
    
    # Draw app name
    app_text = "Network Sniffer"
    bbox = draw.textbbox((0, 0), app_text, font=text_font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    draw.text((x, height - 150), app_text, fill='#7b2cbf', font=text_font)
    
    img.save(filename)
    print(f"Created: {filename}")


if __name__ == "__main__":
    screenshots_dir = os.path.dirname(os.path.abspath(__file__))
    
    create_placeholder_screenshot(
        os.path.join(screenshots_dir, "main_interface.png"),
        "Main Application Interface"
    )
    
    create_placeholder_screenshot(
        os.path.join(screenshots_dir, "packet_details.png"),
        "Packet Details View"
    )
    
    create_placeholder_screenshot(
        os.path.join(screenshots_dir, "export_dialog.png"),
        "Export Data Dialog"
    )
    
    print("\nPlaceholder screenshots created.")
    print("Run the application and capture real screenshots to replace these.")
