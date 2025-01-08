#!/usr/bin/env python
import time
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

# Create a default font
font = ImageFont.load_default()

time.sleep(1.0)  # Skip the reading that happened before the LEDs were enabled

def create_bar(value, max_length=10):
    """Create a progress bar string based on a value (0-255)"""
    filled_length = int((value / 255.0) * max_length)
    bar = '[' + '=' * filled_length + ' ' * (max_length - filled_length) + ']'
    return bar

try:
    while True:
        # Create a new image with mode '1' for 1-bit color
        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        # Get the RGB reading
        r, g, b = bh1745.get_rgb_scaled()
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        
        # Create the bar graphs
        r_bar = create_bar(r)
        g_bar = create_bar(g)
        b_bar = create_bar(b)
        
        # Draw the text and bars on the image
        draw.text((0, 0), f"Color: {color_hex}", font=font, fill="white")
        draw.text((0, 15), f"R: {r_bar}", font=font, fill="white")
        draw.text((0, 25), f"G: {g_bar}", font=font, fill="white")
        draw.text((0, 35), f"B: {b_bar}", font=font, fill="white")
        
        # Display the image on the OLED
        device.display(image)
        
        # Also print to console for debugging
        print(f"\033[2J\033[H")  # Clear console
        print(f"Color: {color_hex}")
        print(f"Red:   {r_bar} ({r})")
        print(f"Green: {g_bar} ({g})")
        print(f"Blue:  {b_bar} ({b})")
        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram terminated by user")
    
finally:
    # Clean up resources
    print("Cleaning up...")
    bh1745.set_leds(0)
    device.cleanup()
    print("Cleanup complete")
