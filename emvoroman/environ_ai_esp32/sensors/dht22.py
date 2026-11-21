"""
ENVIRON AI ESP32 - DHT22 Sensor (Lightweight)
"""

import dht
from machine import Pin
import time
from config import PIN_DHT22, DHT22_RETRIES, DHT22_RETRY_DELAY_MS, DHT22_MIN_INTERVAL_MS, SIMULATION_MODE, SIM_TEMP_BASE, SIM_HUMIDITY_BASE

class DHT22Sensor:
    def __init__(self):
        self._pin = Pin(PIN_DHT22, Pin.IN, Pin.PULL_UP)
        self._sensor = dht.DHT22(self._pin)
        self._last_temp = None
        self._last_hum = None
        self._last_read = 0
        self._errors = 0
        self._fails = 0
    
    def read(self):
        if SIMULATION_MODE:
            import random
            self._last_temp = SIM_TEMP_BASE + random.uniform(-1, 1)
            self._last_hum = max(0, min(100, SIM_HUMIDITY_BASE + random.uniform(-3, 3)))
            self._last_read = time.ticks_ms()
            self._fails = 0
            return True
        
        elapsed = time.ticks_diff(time.ticks_ms(), self._last_read)
        if elapsed < DHT22_MIN_INTERVAL_MS:
            time.sleep_ms(DHT22_MIN_INTERVAL_MS - elapsed)
        
        for _ in range(DHT22_RETRIES):
            try:
                self._sensor.measure()
                t = self._sensor.temperature()
                h = self._sensor.humidity()
                if t is None or h is None:
                    raise ValueError("None")
                if not (-40 <= t <= 80) or not (0 <= h <= 100):
                    raise ValueError("Range")
                self._last_temp = t
                self._last_hum = h
                self._last_read = time.ticks_ms()
                self._fails = 0
                return True
            except:
                self._errors += 1
                self._fails += 1
                time.sleep_ms(DHT22_RETRY_DELAY_MS)
        
        return False
    
    def get_temperature(self):
        return self._last_temp
    
    def get_humidity(self):
        return self._last_hum
    
    def health_check(self):
        if self._fails >= 3:
            return 'FAILED'
        if self._fails > 0:
            return 'DEGRADED'
        if self._last_temp is None:
            return 'NO_READ'
        return 'OK'
    
    def get_status(self):
        return {
            'temp': self._last_temp,
            'hum': self._last_hum,
            'errors': self._errors,
            'fails': self._fails,
            'healthy': self._fails == 0
        }

def test_dht22():
    import config
    config.SIMULATION_MODE = True
    s = DHT22Sensor()
    for _ in range(3):
        s.read()
        print("T:", s.get_temperature(), "H:", s.get_humidity())
        time.sleep(1)

if __name__ == '__main__':
    test_dht22()
