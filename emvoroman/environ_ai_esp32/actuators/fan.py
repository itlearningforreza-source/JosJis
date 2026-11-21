"""
ENVIRON AI ESP32 - Fan Controller (Lightweight)
"""

from actuators.relay import FanRelay
import time
from config import PIN_RELAY, TEMP_FAN_ON, TEMP_FAN_OFF, HUMIDITY_FAN_ON, HUMIDITY_FAN_OFF, MQ135_ADC_FAN_ON, MQ135_ADC_FAN_OFF, FAN_COOLDOWN_MS, SIMULATION_MODE

class FanController:
    def __init__(self, relay_pin=PIN_RELAY):
        self._relay = FanRelay(relay_pin, name="fan")
        self._last_off = 0
        self._auto = True
        self._manual = None
    
    def update(self, temp, hum, adc):
        if not self._auto or self._manual is not None:
            return False
        
        run = False
        
        if temp is not None:
            if self._relay.is_on():
                if temp <= TEMP_FAN_OFF:
                    run = False
                else:
                    run = True
            else:
                if temp >= TEMP_FAN_ON:
                    run = True
        
        if hum is not None and not run:
            if self._relay.is_on():
                if hum <= HUMIDITY_FAN_OFF:
                    run = False
                else:
                    run = True
            else:
                if hum >= HUMIDITY_FAN_ON:
                    run = True
        
        if adc is not None and not run:
            if self._relay.is_on():
                if adc <= MQ135_ADC_FAN_OFF:
                    run = False
                else:
                    run = True
            else:
                if adc >= MQ135_ADC_FAN_ON:
                    run = True
        
        if run and self._last_off > 0:
            if time.ticks_diff(time.ticks_ms(), self._last_off) < 60000:
                run = False
        
        changed = False
        if run and not self._relay.is_on():
            self._relay.on()
            changed = True
        elif not run and self._relay.is_on():
            self._relay.off()
            self._last_off = time.ticks_ms()
            changed = True
        
        return changed
    
    def force_on(self):
        self._manual = True
        self._relay.on()
    
    def force_off(self):
        self._manual = False
        self._relay.off()
    
    def auto(self):
        self._manual = None
    
    def is_on(self):
        return self._relay.is_on()
    
    def get_status(self):
        s = self._relay.get_status()
        s['auto'] = self._auto
        return s

if __name__ == '__main__':
    import config
    config.SIMULATION_MODE = True
    f = FanController()
    f.update(30, 50, 1500)
    print(f.get_status())
    f.update(25, 50, 1500)
    print(f.get_status())
