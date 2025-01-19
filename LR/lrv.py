from breakout_bh1745 import BreakoutBH1745
from pimoroni_i2c import PimoroniI2C
from machine import Pin, I2C
import time
import math
from ssd1306 import SSD1306_I2C

VERSION = "1.2.5"
print(f"LRV Sensor Script v{VERSION}")

# Initialize the OLED on second I2C bus
i2c_display = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
oled = SSD1306_I2C(128, 32, i2c_display)  # 128x32 pixels

# Sensitivity corrections from the original code
SENSITIVITY_CORRECTIONS = {
    'red': 0.7,    # Peak around 615nm with ~0.7 relative sensitivity
    'green': 1.0,  # Peak around 540nm with ~1.0 relative sensitivity
    'blue': 0.55   # Peak around 465nm with ~0.55 relative sensitivity
}

HTML_COLORS = [

    {"name": "Beige", "code": "#F5F5DC"},
    {"name": "Black", "code": "#000000"},

    {"name": "Blue", "code": "#0000FF"},

    {"name": "Brown", "code": "#A52A2A"},
    {"name": "Coral", "code": "#FF7F50"},
    {"name": "Crimson", "code": "#DC143C"},
    {"name": "Cyan", "code": "#00FFFF"},
    {"name": "DarkBlue", "code": "#00008B"},
    {"name": "DarkCyan", "code": "#008B8B"},
    {"name": "DarkGray", "code": "#A9A9A9"},
    {"name": "DarkGreen", "code": "#006400"},
    {"name": "DarkKhaki", "code": "#BDB76B"},
    {"name": "DarkMagenta", "code": "#8B008B"},
    {"name": "DarkOliveGreen", "code": "#556B2F"},
    {"name": "DarkOrange", "code": "#FF8C00"},
    {"name": "DarkRed", "code": "#8B0000"},
    {"name": "DarkViolet", "code": "#9400D3"},
    {"name": "Fuchsia", "code": "#FF00FF"},
    {"name": "Gold", "code": "#FFD700"},
    {"name": "Gray", "code": "#808080"},
    {"name": "Green", "code": "#008000"},
    {"name": "Indigo", "code": "#4B0082"},
    {"name": "Ivory", "code": "#FFFFF0"},
    {"name": "Khaki", "code": "#F0E68C"},
    {"name": "Lavender", "code": "#E6E6FA"},
    {"name": "LightBlue", "code": "#ADD8E6"},
    {"name": "LightCoral", "code": "#F08080"},
    {"name": "LightCyan", "code": "#E0FFFF"},
    {"name": "LightGray", "code": "#D3D3D3"},
    {"name": "LightGreen", "code": "#90EE90"},
    {"name": "LightSkyBlue", "code": "#87CEFA"},
    {"name": "LightYellow", "code": "#FFFFE0"},
    {"name": "Lime", "code": "#00FF00"},
    {"name": "Magenta", "code": "#FF00FF"},
    {"name": "Navy", "code": "#000080"},
    {"name": "Olive", "code": "#808000"},
    {"name": "Orange", "code": "#FFA500"},
    {"name": "Orchid", "code": "#DA70D6"},
    {"name": "Pink", "code": "#FFC0CB"},
    {"name": "Purple", "code": "#800080"},
    {"name": "Red", "code": "#FF0000"},
    {"name": "RoyalBlue", "code": "#4169E1"},
    {"name": "Salmon", "code": "#FA8072"},
    {"name": "Sienna", "code": "#A0522D"},
    {"name": "Silver", "code": "#C0C0C0"},
    {"name": "SlateGray", "code": "#708090"},
    {"name": "Turquoise", "code": "#40E0D0"},
    {"name": "Violet", "code": "#EE82EE"},

    {"name": "White", "code": "#FFFFFF"},

    {"name": "Yellow", "code": "#FFFF00"},
]

def calculate_lrv(r, g, b, c):
    """Calculate calibrated Light Reflectance Value (LRV)"""
    if c == 0:
        return 0
        
    # Apply sensitivity corrections to raw values
    r_corrected = r / SENSITIVITY_CORRECTIONS['red']
    g_corrected = g / SENSITIVITY_CORRECTIONS['green']
    b_corrected = b / SENSITIVITY_CORRECTIONS['blue']
    
    # Normalize using clear reading
    r_norm = r_corrected / c
    g_norm = g_corrected / c
    b_norm = b_corrected / c
    
    # Calculate relative luminance using CIE coefficients
    luminance = (0.2126 * r_norm) + (0.7152 * g_norm) + (0.0722 * b_norm)
    
    # Scale to 0-100 range
    lrv = min(100, luminance * 100)
    return round(lrv, 1)

def hex_to_rgb(hex_color):
    """Convert hex color (#RRGGBB) to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(r1, g1, b1, r2, g2, b2):
    """Calculate Euclidean distance between two RGB colors"""
    return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

def find_nearest_color(r, g, b, c):
    """Find the nearest HTML color name for given RGB values"""
    min_distance = float('inf')
    nearest_color = None
    
    for color in HTML_COLORS:
        rgb = hex_to_rgb(color['code'])
        distance = color_distance(r, g, b, *rgb)
        
        if distance < min_distance:
            min_distance = distance
            nearest_color = color['name']
    
    return nearest_color

def display_readings(rgb_scaled, color_name, lrv):
    """Display readings on the OLED"""
    oled.fill(0)  # Clear display
    
    # First line: RGB as hex
    hex_color = "#{:02x}{:02x}{:02x}".format(*rgb_scaled)
    oled.text(hex_color, 0, 0)
    
    # Second line: Color name (truncate if too long)
    if len(color_name) > 16:  # OLED can fit ~16 chars per line
        color_name = color_name[:16]
    oled.text(color_name, 0, 12)
    
    # Third line: LRV value
    oled.text(f"LRV: {lrv:.1f}%", 0, 24)
    
    # Update display
    oled.show()
    # pass
def main():
    # Initialize I2C for color sensor
    i2c = PimoroniI2C(sda=0, scl=1)
    sensor = BreakoutBH1745(i2c)
    
    # Turn on LEDs
    sensor.leds(True)
    print("LEDs turned on")
    
    try:
        while True:
            # Get all readings
            rgbc_raw = sensor.rgbc_raw()
            rgb_clamped = sensor.rgbc_clamped()
            rgb_scaled = sensor.rgbc_scaled()
            
            # Calculate LRV using raw values
            r, g, b, c = rgbc_raw
            lrv = calculate_lrv(r, g, b, c)
            
            # Find nearest HTML color using rgb_scaled directly
            color_name = find_nearest_color(*rgb_scaled)
            
            # Update OLED display
            display_readings(rgb_scaled, color_name, lrv)
            current_time = time.localtime()
            print(f"Time: {current_time[3]:02d}:{current_time[4]:02d}:{current_time[5]:02d}")
            # Print all values to console too
            print("Raw: {}, {}, {}, {}".format(*rgbc_raw))
            print("Clamped: {}, {}, {}, {}".format(*rgb_clamped))
            print("Scaled: #{:02x}{:02x}{:02x}".format(*rgb_scaled))
            print(f"Nearest Color: {color_name}")
            print(f"LRV: {lrv:.1f}%")
            print("---")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        sensor.leds(False)
        # oled.fill(0)  # Clear display
        # oled.text("Stopped", 0, 12)
        # oled.show()
        print("\nLEDs turned off")
        print("Program terminated.")

if __name__ == "__main__":
    main() 