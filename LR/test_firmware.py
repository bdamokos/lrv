print("Testing imports...")
try:
    from breakout_bh1745 import BreakoutBH1745
    print("✓ breakout_bh1745 available")
except ImportError as e:
    print(f"✗ Failed to import breakout_bh1745: {e}")

try:
    from pimoroni_i2c import PimoroniI2C
    print("✓ pimoroni_i2c available")
except ImportError as e:
    print(f"✗ Failed to import pimoroni_i2c: {e}") 