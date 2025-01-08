#!/usr/bin/env python
import time
import niquests as requests
from bh1745 import BH1745
from luma.core import cmdline
from PIL import Image, ImageDraw, ImageFont
import json
import os
import argparse
import threading
from web_interface import start_server, update_data

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

# Add these constants near the top of the file, after the imports
CALIBRATION_SAMPLES = {
    "White Reference (96%)": 96.0,  # Example: Pure white paper/card
    "Mid Gray (50%)": 50.0,        # Example: Mid gray card
    "Black Reference (4%)": 4.0     # Example: Dark black card/surface
}

CALIBRATION_FILE = "lrv_calibration.json"

def save_calibration(scaling_factor):
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump({'scaling_factor': scaling_factor}, f)

def load_calibration():
    try:
        with open(CALIBRATION_FILE, 'r') as f:
            data = json.load(f)
            return data.get('scaling_factor', None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

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

def calibrate_lrv():
    """
    Calibrate the LRV calculation using known reference samples.
    Returns the calibrated scaling factor.
    """
    scaling_factors = []
    print("\nLRV Calibration Process")
    print("=======================")
    
    for sample_name, known_lrv in CALIBRATION_SAMPLES.items():
        input(f"\nPlace the {sample_name} sample under the sensor and press Enter...")
        
        # Take multiple readings and average them for stability
        readings = []
        for _ in range(5):
            raw_r, raw_g, raw_b, raw_c = bh1745.get_rgbc_raw()
            if raw_c == 0:
                continue
                
            r_norm = raw_r / raw_c
            g_norm = raw_g / raw_c
            b_norm = raw_b / raw_c
            
            # Calculate relative luminance
            luminance = (0.2126 * r_norm) + (0.7152 * g_norm) + (0.0722 * b_norm)
            readings.append(luminance)
            time.sleep(0.2)
        
        if not readings:
            print(f"Failed to get valid readings for {sample_name}")
            continue
            
        avg_luminance = sum(readings) / len(readings)
        
        # Calculate scaling factor needed to match known LRV
        if avg_luminance > 0:
            scaling_factor = known_lrv / avg_luminance
            scaling_factors.append(scaling_factor)
            print(f"Sample: {sample_name}")
            print(f"Measured luminance: {avg_luminance:.4f}")
            print(f"Calculated scaling factor: {scaling_factor:.2f}")
    
    if not scaling_factors:
        return 100.0  # Default scaling factor
        
    # Use median scaling factor to avoid outliers
    final_scaling = sum(scaling_factors) / len(scaling_factors)
    print(f"\nFinal calibrated scaling factor: {final_scaling:.2f}")
    return final_scaling

# Modify the calculate_lrv function to use the calibrated scaling factor
def calculate_lrv(r, g, b, c, scaling_factor):
    """
    Calculate calibrated Light Reflectance Value (LRV)
    
    Using CIE luminance coefficients (Y from CIE XYZ):
    - Red contribution: 0.2126
    - Green contribution: 0.7152
    - Blue contribution: 0.0722
    """
    if c == 0:
        return 0
        
    r_norm = r / c
    g_norm = g / c
    b_norm = b / c
    
    # Calculate relative luminance using CIE coefficients
    luminance = (0.2126 * r_norm) + (0.7152 * g_norm) + (0.0722 * b_norm)
    
    # Scale to 0-100 range using calibrated scaling factor
    lrv = min(100, luminance * scaling_factor)
    
    return round(lrv, 1)

def parse_args():
    parser = argparse.ArgumentParser(description='LRV Measurement Tool')
    parser.add_argument('--calibrate', '-c', action='store_true',
                       help='Force calibration even if existing calibration exists')
    parser.add_argument('--skip-calibration', '-s', action='store_true',
                       help='Skip calibration and use default scaling factor (100.0)')
    parser.add_argument('--no-web', action='store_true',
                       help='Disable web interface')
    return parser.parse_args()

args = parse_args()

# Start web server if not disabled
if not args.no_web:
    print("Starting web interface on port 8080...")
    web_thread = threading.Thread(target=start_server, daemon=True)
    web_thread.start()

if args.skip_calibration:
    print("Skipping calibration, using default scaling factor (100.0)")
    scaling_factor = 100.0
else:
    print("Checking for existing calibration...")
    scaling_factor = load_calibration()
    if scaling_factor is None or args.calibrate:
        if args.calibrate:
            print("Forced calibration requested...")
        else:
            print("No calibration found. Starting calibration process...")
        scaling_factor = calibrate_lrv()
        save_calibration(scaling_factor)
        print("Calibration saved.")
    else:
        print(f"Using existing calibration (scaling factor: {scaling_factor:.2f})")
        if not args.calibrate:  # Only ask if not forcing calibration
            recalibrate = input("Would you like to recalibrate? (y/n): ").lower().strip() == 'y'
            if recalibrate:
                scaling_factor = calibrate_lrv()
                save_calibration(scaling_factor)
                print("New calibration saved.")

time.sleep(1.0)  # Skip the reading that happened before the LEDs were enabled

try:
    while True:
        # Create a new image with mode '1' for 1-bit color
        image = Image.new('1', (device.width, device.height))
        draw = ImageDraw.Draw(image)
        
        # Get both raw and scaled readings
        r, g, b = bh1745.get_rgb_scaled()  # Normalized using C internally
        raw_r, raw_g, raw_b, raw_c = bh1745.get_rgbc_raw()  # Raw values including Clear
        
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
        print("\nNormalized values:")
        print(f"Red:   {r}")
        print(f"Green: {g}")
        print(f"Blue:  {b}")
        print("\nRaw values:")
        print(f"Red:   {raw_r}")
        print(f"Green: {raw_g}")
        print(f"Blue:  {raw_b}")
        print(f"Clear: {raw_c}")
        
        raw_r, raw_g, raw_b, raw_c = bh1745.get_rgbc_raw()
        lrv = calculate_lrv(raw_r, raw_g, raw_b, raw_c, scaling_factor)
        
        # Add LRV to display and console output
        draw.text((0, 85), f"LRV: {lrv}%", font=font, fill="white")
        
        print(f"\nEstimated LRV: {lrv}%")
        
        time.sleep(1.0)  # Changed to 1 second update frequency

        if not args.no_web:
            update_data(
                color_hex,
                color_name,
                lrv,
                {'r': r, 'g': g, 'b': b},
                {'r': raw_r, 'g': raw_g, 'b': raw_b, 'c': raw_c}
            )

except KeyboardInterrupt:
    print("\nProgram terminated by user")
    
finally:
    # Clean up resources
    print("Cleaning up...")
    bh1745.set_leds(0)
    device.cleanup()
    print("Cleanup complete")
