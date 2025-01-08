#!/usr/bin/env python
import time
import niquests as requests
from bh1745 import BH1745
from luma.core import cmdline
from PIL import Image, ImageDraw, ImageFont

# Set up the BH1745 sensor
bh1745 = BH1745()
bh1745.setup()
bh1745.set_leds(1)

# Set up the display
display_args = [
    '--display', 'sh1106',
    '--height', '128',
    '--rotate', '2',
    '--interface', 'spi',
    '--gpio-data-command', '9',
    '--spi-device', '1'
]

device = cmdline.create_device(cmdline.create_parser(description='LRV display').parse_args(display_args))

# Create fonts - default for bars, larger for color display
font = ImageFont.load_default()
# Try to load a larger font - you might need to adjust the path based on your system
try:
    large_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except IOError:
    large_font = font  # Fallback to default if the font isn't available

def get_color_name(hex_color):
    """Get the color name from the Color API"""
    try:
        response = requests.get(f'https://www.thecolorapi.com/id?hex={hex_color[1:]}')
        if response.status_code == 200:
            return response.json()['name']['value']
        return None
    except:
        return None

def draw_bar(draw, y_position, value, label):
    """Draw a progress bar at the given y position for the given value (0-255)"""
    # Bar container coordinates
    left_border = 19
    right_border = 119  # 100 pixels wide plus left border
    bar_height = 8
    
    # Draw container borders
    draw.line([(left_border, y_position), (left_border, y_position + bar_height)], fill="white")  # Left border
    draw.line([(right_border, y_position), (right_border, y_position + bar_height)], fill="white")  # Right border
    
    # Calculate fill width based on value
    fill_width = int((value / 255.0) * 100)  # Scale value to 0-100 pixels
    
    # Draw the filled portion
    if fill_width > 0:
        draw.rectangle([
            (left_border + 1, y_position),
            (left_border + fill_width, y_position + bar_height)
        ], fill="white")
    
    # Draw label
    draw.text((0, y_position), label, font=font, fill="white")

time.sleep(1.0)  # Skip the reading that happened before the LEDs were enabled

try:
    while True:
        # Create a new image with mode '1' for 1-bit color
        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        # Get the RGB reading
        r, g, b = bh1745.get_rgb_scaled()
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        
        # Get color name
        color_name = get_color_name(color_hex)
        
        # Draw the hex color value with larger font
        draw.text((0, 0), color_hex, font=large_font, fill="white")
        if color_name:
            # Draw color name below hex value
            draw.text((0, 20), color_name, font=font, fill="white")
        
        # Draw the bars
        draw_bar(draw, 40, r, "R:")
        draw_bar(draw, 55, g, "G:")
        draw_bar(draw, 70, b, "B:")
        
        # Display the image on the OLED
        device.display(image)
        
        # Print to console for debugging
        print(f"\033[2J\033[H")  # Clear console
        print(f"Color: {color_hex}")
        if color_name:
            print(f"Name:  {color_name}")
        print(f"Red:   {r}")
        print(f"Green: {g}")
        print(f"Blue:  {b}")
        
        time.sleep(1.0)  # Changed to 1 second update frequency

except KeyboardInterrupt:
    print("\nProgram terminated by user")
    
finally:
    # Clean up resources
    print("Cleaning up...")
    bh1745.set_leds(0)
    device.cleanup()
    print("Cleanup complete")
