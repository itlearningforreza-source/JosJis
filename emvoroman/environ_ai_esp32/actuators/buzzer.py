"""
ENVIRON AI ESP32 - Buzzer (Lightweight)
"""

from machine import Pin, PWM
import time
from config import PIN_BUZZER, BUZZER_FREQ, BUZZER_DUTY, SIMULATION_MODE

class Buzzer:
    def __init__(self, pin=PIN_BUZZER):
        self._pin = Pin(pin, Pin.OUT)
        self._pwm = PWM(self._pin, freq=BUZZER_FREQ, duty=0) if not SIMULATION_MODE else None
        self._pin.value(0)
    
    def _set(self, duty):
        if SIMULATION_MODE:
            self._pin.value(1 if duty else 0)
        else:
            self._pwm.duty(duty)
    
    def beep(self, ms=100):
        self._set(512)
        time.sleep_ms(ms)
        self._set(0)
    
    def alarm_critical(self):
        for _ in range(3):
            self._set(512)
            time.sleep_ms(100)
            self._set(0)
            time.sleep_ms(100)
        time.sleep_ms(500)
    
    def alarm_warning(self):
        for _ in range(2):
            self._set(512)
            time.sleep_ms(200)
            self._set(0)
            time.sleep_ms(200)
        time.sleep_ms(500)
    
    def alarm_info(self):
        self.beep(50)
    
    def alarm_fault(self):
        self._set(512)
        time.sleep_ms(300)
        self._set(0)
        time.sleep_ms(100)
        self._set(512)
        time.sleep_ms(100)
        self._set(0)
        time.sleep_ms(100)
        self._set(512)
        time.sleep_ms(300)
        self._set(0)
    
    def stop(self):
        self._set(0)
    
    def get_status(self):
        return {'active': False}

if __name__ == '__main__':
    import config
    config.SIMULATION_MODE = True
    b = Buzzer()
    b.alarm_info()
    time.sleep(0.5)
    b.alarm_warning()
    time.sleep(1)
    b.alarm_critical()
    time.sleep(1)
