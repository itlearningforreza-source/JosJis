"""
ENVIRON AI ESP32 - Boot Script
Runs automatically on MicroPython startup.
"""

import gc
import machine
import sys

# Disable debug output for cleaner boot
try:
    import os
    os.dupterm(None, 1)  # Disable REPL on UART0
except:
    pass

# Enable garbage collection
gc.collect()
gc.threshold(10000)  # Collect when 10KB allocated

# Print boot info
print("=" * 40)
print("ENVIRON AI ESP32 Booting...")
print(f"CPU Freq: {machine.freq() // 1000000} MHz")
print(f"Free Heap: {gc.mem_free()} bytes")
print(f"Reset Cause: {machine.reset_cause()}")
print("=" * 40)

# Check for safe mode trigger (GPIO0 held low)
try:
    import config
    safe_mode_pin = machine.Pin(config.SAFE_MODE_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    if safe_mode_pin.value() == 0:
        print("SAFE MODE TRIGGERED (GPIO0 held low)")
        # Enter minimal safe mode
        while True:
            import time
            led = machine.Pin(2, machine.Pin.OUT)
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.2)
except:
    pass

# Start main application
try:
    import main
except Exception as e:
    print(f"Failed to start main: {e}")
    # Blink LED rapidly to indicate error
    led = machine.Pin(2, machine.Pin.OUT)
    while True:
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)
