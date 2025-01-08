from flask import Flask, render_template_string
import threading
import json

app = Flask(__name__)

# Shared data storage
current_data = {
    'color_hex': '#000000',
    'color_name': 'Unknown',
    'lrv': 0,
    'rgb': {'r': 0, 'g': 0, 'b': 0},
    'raw': {'r': 0, 'g': 0, 'b': 0, 'c': 0}
}

# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>LRV Sensor Data</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 0 20px;
            background-color: #f0f0f0;
        }
        .color-chip {
            width: 200px;
            height: 200px;
            border: 2px solid #333;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        .data-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .value-display {
            font-size: 1.2em;
            margin: 10px 0;
        }
        .lrv-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <h1>LRV Sensor Data</h1>
    
    <div class="data-container">
        <div class="color-chip" id="colorChip"></div>
        
        <div class="value-display">
            <strong>Color:</strong> <span id="colorHex"></span>
        </div>
        <div class="value-display">
            <strong>Name:</strong> <span id="colorName"></span>
        </div>
        <div class="value-display">
            <strong>LRV:</strong> <span id="lrvValue" class="lrv-value"></span>%
        </div>
        
        <h3>RGB Values:</h3>
        <div class="value-display">
            <strong>R:</strong> <span id="rgbR"></span>
            <strong>G:</strong> <span id="rgbG"></span>
            <strong>B:</strong> <span id="rgbB"></span>
        </div>
        
        <h3>Raw Sensor Values:</h3>
        <div class="value-display">
            <strong>R:</strong> <span id="rawR"></span>
            <strong>G:</strong> <span id="rawG"></span>
            <strong>B:</strong> <span id="rawB"></span>
            <strong>C:</strong> <span id="rawC"></span>
        </div>
    </div>

    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('colorChip').style.backgroundColor = data.color_hex;
                    document.getElementById('colorHex').textContent = data.color_hex;
                    document.getElementById('colorName').textContent = data.color_name;
                    document.getElementById('lrvValue').textContent = data.lrv.toFixed(1);
                    
                    document.getElementById('rgbR').textContent = data.rgb.r;
                    document.getElementById('rgbG').textContent = data.rgb.g;
                    document.getElementById('rgbB').textContent = data.rgb.b;
                    
                    document.getElementById('rawR').textContent = data.raw.r;
                    document.getElementById('rawG').textContent = data.raw.g;
                    document.getElementById('rawB').textContent = data.raw.b;
                    document.getElementById('rawC').textContent = data.raw.c;
                });
        }

        // Update every second
        setInterval(updateData, 1000);
        updateData();  // Initial update
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def get_data():
    return json.dumps(current_data)

def update_data(hex_color, color_name, lrv, rgb_values, raw_values):
    current_data['color_hex'] = hex_color
    current_data['color_name'] = color_name if color_name else 'Unknown'
    current_data['lrv'] = lrv
    current_data['rgb'] = rgb_values
    current_data['raw'] = raw_values

def start_server():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    start_server() 