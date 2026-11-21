"""
ENVIRON AI ESP32 - Relay (Lightweight)
"""

from machine import Pin
import time
from config import RELAY_ACTIVE_LOW, SIMULATION_MODE

class Relay:
    def __init__(self, pin, active_low=RELAY_ACTIVE_LOW, name="relay"):
        self._pin = Pin(pin, Pin.OUT)
        self._active_low = active_low
        self._name = name
        self._state = False
        self._changes = 0
        self.off()
        print("[" + name + "] GPIO" + str(pin) + " active_low=" + str(active_low))
    
    def _hw(self, on):
        if SIMULATION_MODE:
            self._pin.value(0 if on else 1)
        else:
            self._pin.value(0 if (on ^ self._active_low) else 1)
    
    def on(self):
        if not self._state:
            self._hw(True)
            self._state = True
            self._changes += 1
    
    def off(self):
        if self._state:
            self._hw(False)
            self._state = False
            self._changes += 1
    
    def is_on(self):
        return self._state
    
    def get_status(self):
        return {'state': 'ON' if self._state else 'OFF', 'changes': self._changes}

class FanRelay(Relay):
    def __init__(self, pin, min_run_ms=30000, active_low=True):
        from config import FAN_MIN_RUN_MS
        super().__init__(pin, active_low, "fan")
        self._min_run = min_run_ms or FAN_MIN_RUN_MS
    
    def off(self):
        if self._state:
            # Skip min run check for simplicity in lightweight version
            super().off()
    
    def force_off(self):
        self.off()

if __name__ == '__main__':
    import config
    config.SIMULATION_MODE = True
    r = Relay(5, name="test")
    r.on(); time.sleep(0.2); r.off()
    print(r.get_status())
