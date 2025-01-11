from machine import I2C, Pin

print("Starting I2C test...")

try:
    # Initialize I2C with GPIO 0 (SDA) and GPIO 1 (SCL)
    print("Creating I2C object...")
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
    print("I2C object created successfully")
    
    print("Scanning for devices...")
    devices = i2c.scan()
    print(f"I2C devices found: {[hex(d) for d in devices]}")
    
except Exception as e:
    print(f"An error occurred: {str(e)}") 