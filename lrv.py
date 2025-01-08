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

try:
    while True:
        # Create a new image with mode '1' for 1-bit color
        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        # Get the RGB reading
        r, g, b = bh1745.get_rgb_scaled()
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        
        # Draw the text on the image
        draw.text((0, 0), f"RGB Reading:", font=font, fill="white")
        draw.text((0, 15), color_hex, font=font, fill="white")
        
        # Display the image on the OLED
        device.display(image)
        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nProgram terminated by user")
    
finally:
    # Clean up resources
    print("Cleaning up...")
    bh1745.set_leds(0)
    device.cleanup()
    print("Cleanup complete")
