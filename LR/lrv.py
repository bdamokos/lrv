from breakout_bh1745 import BreakoutBH1745
from pimoroni_i2c import PimoroniI2C
import time
import math

VERSION = "1.2.3"
print(f"LRV Sensor Script v{VERSION}")

# Sensitivity corrections from the original code
SENSITIVITY_CORRECTIONS = {
    'red': 0.7,    # Peak around 615nm with ~0.7 relative sensitivity
    'green': 1.0,  # Peak around 540nm with ~1.0 relative sensitivity
    'blue': 0.55   # Peak around 465nm with ~0.55 relative sensitivity
}

HTML_COLORS = [
    {"name": "AliceBlue", "code": "#F0F8FF"},
    {"name": "AntiqueWhite", "code": "#FAEBD7"},
    {"name": "Aqua", "code": "#00FFFF"},
    {"name": "Aquamarine", "code": "#7FFFD4"},
    {"name": "Azure", "code": "#F0FFFF"},
    {"name": "Beige", "code": "#F5F5DC"},
    {"name": "Bisque", "code": "#FFE4C4"},
    {"name": "Black", "code": "#000000"},
    {"name": "BlanchedAlmond", "code": "#FFEBCD"},
    {"name": "Blue", "code": "#0000FF"},
    {"name": "BlueViolet", "code": "#8A2BE2"},
    {"name": "Brown", "code": "#A52A2A"},
    {"name": "BurlyWood", "code": "#DEB887"},
    {"name": "CadetBlue", "code": "#5F9EA0"},
    {"name": "Chartreuse", "code": "#7FFF00"},
    {"name": "Chocolate", "code": "#D2691E"},
    {"name": "Coral", "code": "#FF7F50"},
    {"name": "CornflowerBlue", "code": "#6495ED"},
    {"name": "Cornsilk", "code": "#FFF8DC"},
    {"name": "Crimson", "code": "#DC143C"},
    {"name": "Cyan", "code": "#00FFFF"},
    {"name": "DarkBlue", "code": "#00008B"},
    {"name": "DarkCyan", "code": "#008B8B"},
    {"name": "DarkGoldenRod", "code": "#B8860B"},
    {"name": "DarkGray", "code": "#A9A9A9"},
    {"name": "DarkGreen", "code": "#006400"},
    {"name": "DarkKhaki", "code": "#BDB76B"},
    {"name": "DarkMagenta", "code": "#8B008B"},
    {"name": "DarkOliveGreen", "code": "#556B2F"},
    {"name": "DarkOrange", "code": "#FF8C00"},
    {"name": "DarkOrchid", "code": "#9932CC"},
    {"name": "DarkRed", "code": "#8B0000"},
    {"name": "DarkSalmon", "code": "#E9967A"},
    {"name": "DarkSeaGreen", "code": "#8FBC8F"},
    {"name": "DarkSlateBlue", "code": "#483D8B"},
    {"name": "DarkSlateGray", "code": "#2F4F4F"},
    {"name": "DarkTurquoise", "code": "#00CED1"},
    {"name": "DarkViolet", "code": "#9400D3"},
    {"name": "DeepPink", "code": "#FF1493"},
    {"name": "DeepSkyBlue", "code": "#00BFFF"},
    {"name": "DimGray", "code": "#696969"},
    {"name": "DodgerBlue", "code": "#1E90FF"},
    {"name": "FireBrick", "code": "#B22222"},
    {"name": "FloralWhite", "code": "#FFFAF0"},
    {"name": "ForestGreen", "code": "#228B22"},
    {"name": "Fuchsia", "code": "#FF00FF"},
    {"name": "Gainsboro", "code": "#DCDCDC"},
    {"name": "GhostWhite", "code": "#F8F8FF"},
    {"name": "Gold", "code": "#FFD700"},
    {"name": "GoldenRod", "code": "#DAA520"},
    {"name": "Gray", "code": "#808080"},
    {"name": "Green", "code": "#008000"},
    {"name": "GreenYellow", "code": "#ADFF2F"},
    {"name": "HoneyDew", "code": "#F0FFF0"},
    {"name": "HotPink", "code": "#FF69B4"},
    {"name": "IndianRed", "code": "#CD5C5C"},
    {"name": "Indigo", "code": "#4B0082"},
    {"name": "Ivory", "code": "#FFFFF0"},
    {"name": "Khaki", "code": "#F0E68C"},
    {"name": "Lavender", "code": "#E6E6FA"},
    {"name": "LavenderBlush", "code": "#FFF0F5"},
    {"name": "LawnGreen", "code": "#7CFC00"},
    {"name": "LemonChiffon", "code": "#FFFACD"},
    {"name": "LightBlue", "code": "#ADD8E6"},
    {"name": "LightCoral", "code": "#F08080"},
    {"name": "LightCyan", "code": "#E0FFFF"},
    {"name": "LightGoldenRodYellow", "code": "#FAFAD2"},
    {"name": "LightGray", "code": "#D3D3D3"},
    {"name": "LightGreen", "code": "#90EE90"},
    {"name": "LightPink", "code": "#FFB6C1"},
    {"name": "LightSalmon", "code": "#FFA07A"},
    {"name": "LightSeaGreen", "code": "#20B2AA"},
    {"name": "LightSkyBlue", "code": "#87CEFA"},
    {"name": "LightSlateGray", "code": "#778899"},
    {"name": "LightSteelBlue", "code": "#B0C4DE"},
    {"name": "LightYellow", "code": "#FFFFE0"},
    {"name": "Lime", "code": "#00FF00"},
    {"name": "LimeGreen", "code": "#32CD32"},
    {"name": "Linen", "code": "#FAF0E6"},
    {"name": "Magenta", "code": "#FF00FF"},
    {"name": "Maroon", "code": "#800000"},
    {"name": "MediumAquaMarine", "code": "#66CDAA"},
    {"name": "MediumBlue", "code": "#0000CD"},
    {"name": "MediumOrchid", "code": "#BA55D3"},
    {"name": "MediumPurple", "code": "#9370DB"},
    {"name": "MediumSeaGreen", "code": "#3CB371"},
    {"name": "MediumSlateBlue", "code": "#7B68EE"},
    {"name": "MediumSpringGreen", "code": "#00FA9A"},
    {"name": "MediumTurquoise", "code": "#48D1CC"},
    {"name": "MediumVioletRed", "code": "#C71585"},
    {"name": "MidnightBlue", "code": "#191970"},
    {"name": "MintCream", "code": "#F5FFFA"},
    {"name": "MistyRose", "code": "#FFE4E1"},
    {"name": "Moccasin", "code": "#FFE4B5"},
    {"name": "NavajoWhite", "code": "#FFDEAD"},
    {"name": "Navy", "code": "#000080"},
    {"name": "OldLace", "code": "#FDF5E6"},
    {"name": "Olive", "code": "#808000"},
    {"name": "OliveDrab", "code": "#6B8E23"},
    {"name": "Orange", "code": "#FFA500"},
    {"name": "OrangeRed", "code": "#FF4500"},
    {"name": "Orchid", "code": "#DA70D6"},
    {"name": "PaleGoldenRod", "code": "#EEE8AA"},
    {"name": "PaleGreen", "code": "#98FB98"},
    {"name": "PaleTurquoise", "code": "#AFEEEE"},
    {"name": "PaleVioletRed", "code": "#DB7093"},
    {"name": "PapayaWhip", "code": "#FFEFD5"},
    {"name": "PeachPuff", "code": "#FFDAB9"},
    {"name": "Peru", "code": "#CD853F"},
    {"name": "Pink", "code": "#FFC0CB"},
    {"name": "Plum", "code": "#DDA0DD"},
    {"name": "PowderBlue", "code": "#B0E0E6"},
    {"name": "Purple", "code": "#800080"},
    {"name": "RebeccaPurple", "code": "#663399"},
    {"name": "Red", "code": "#FF0000"},
    {"name": "RosyBrown", "code": "#BC8F8F"},
    {"name": "RoyalBlue", "code": "#4169E1"},
    {"name": "SaddleBrown", "code": "#8B4513"},
    {"name": "Salmon", "code": "#FA8072"},
    {"name": "SandyBrown", "code": "#F4A460"},
    {"name": "SeaGreen", "code": "#2E8B57"},
    {"name": "SeaShell", "code": "#FFF5EE"},
    {"name": "Sienna", "code": "#A0522D"},
    {"name": "Silver", "code": "#C0C0C0"},
    {"name": "SkyBlue", "code": "#87CEEB"},
    {"name": "SlateBlue", "code": "#6A5ACD"},
    {"name": "SlateGray", "code": "#708090"},
    {"name": "Snow", "code": "#FFFAFA"},
    {"name": "SpringGreen", "code": "#00FF7F"},
    {"name": "SteelBlue", "code": "#4682B4"},
    {"name": "Tan", "code": "#D2B48C"},
    {"name": "Teal", "code": "#008080"},
    {"name": "Thistle", "code": "#D8BFD8"},
    {"name": "Tomato", "code": "#FF6347"},
    {"name": "Turquoise", "code": "#40E0D0"},
    {"name": "Violet", "code": "#EE82EE"},
    {"name": "Wheat", "code": "#F5DEB3"},
    {"name": "White", "code": "#FFFFFF"},
    {"name": "WhiteSmoke", "code": "#F5F5F5"},
    {"name": "Yellow", "code": "#FFFF00"},
    {"name": "YellowGreen", "code": "#9ACD32"}
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

def main():
    # Initialize I2C like in demo.py
    i2c = PimoroniI2C(sda=0, scl=1)
    sensor = BreakoutBH1745(i2c)
    
    # Turn on LEDs
    sensor.leds(True)
    print("LEDs turned on")
    
    try:
        while True:
            # Get all readings like in demo.py
            rgbc_raw = sensor.rgbc_raw()
            rgb_clamped = sensor.rgbc_clamped()
            rgb_scaled = sensor.rgbc_scaled()
            
            # Calculate LRV using raw values
            r, g, b, c = rgbc_raw
            lrv = calculate_lrv(r, g, b, c)
            
            # Find nearest HTML color using rgb_scaled directly
            color_name = find_nearest_color(*rgb_scaled)
            
            # Print all values
            print("Raw: {}, {}, {}, {}".format(*rgbc_raw))
            print("Clamped: {}, {}, {}, {}".format(*rgb_clamped))
            print("Scaled: #{:02x}{:02x}{:02x}".format(*rgb_scaled))
            print(f"Nearest Color: {color_name}")
            print(f"LRV: {lrv:.1f}%")
            print("---")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        sensor.leds(False)
        print("\nLEDs turned off")
        print("Program terminated.")

if __name__ == "__main__":
    main() 