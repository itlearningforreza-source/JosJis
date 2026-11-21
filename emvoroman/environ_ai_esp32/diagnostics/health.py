"""
ENVIRON AI ESP32 - Diagnostics (Lightweight)
"""

import gc
import time
import machine
from config import WDT_TIMEOUT_MS, WDT_FEED_INTERVAL_MS, HEAP_WARN_THRESHOLD, MAX_BOOT_FAILURES, SAFE_MODE_PIN

class Watchdog:
    def __init__(self, timeout_ms=WDT_TIMEOUT_MS):
        self._wdt = None
        self._feed_iv = WDT_FEED_INTERVAL_MS
        self._last = 0
        try:
            self._wdt = machine.WDT(timeout=timeout_ms)
            print("[WDT] Enabled " + str(timeout_ms) + "ms")
        except Exception as e:
            print("[WDT] Failed: " + str(e))
    
    def feed(self):
        if self._wdt:
            try: self._wdt.feed(); self._last = time.ticks_ms()
            except: pass
    
    def need_feed(self):
        if not self._wdt: return False
        return time.ticks_diff(time.ticks_ms(), self._last) >= self._feed_iv

class Diagnostics:
    def __init__(self):
        self._start = time.ticks_ms()
        self._errors = []
        self._warns = []
        self._boot_fails = 0
        try:
            self._reset = machine.reset_cause()
        except: self._reset = None
    
    def boot_ok(self, ok=True):
        self._boot_fails = 0 if ok else self._boot_fails + 1
    
    def safe_mode(self):
        return self._boot_fails >= 3
    
    def error(self, src, msg):
        self._errors.append({'s': src, 'm': msg, 't': time.ticks_ms()})
        if len(self._errors) > 20: self._errors.pop(0)
    
    def warn(self, src, msg):
        self._warns.append({'s': src, 'm': msg, 't': time.ticks_ms()})
        if len(self._warns) > 20: self._warns.pop(0)
    
    def run(self):
        gc.collect()
        free = gc.mem_free()
        if free < 15000:
            self.warn('mem', 'Low heap: ' + str(free))
        return {
            'up_ms': time.ticks_diff(time.ticks_ms(), self._start),
            'free': free,
            'used': gc.mem_alloc(),
            'reset': self._reset,
            'boots': self._boot_fails,
            'errs': len(self._errors),
            'warns': len(self._warns),
            'health': 'OK' if free >= 15000 else 'LOW_MEM'
        }

class SafeMode:
    def __init__(self, diag):
        self._diag = diag
        self._on = False
    
    def check(self):
        if self._diag.safe_mode():
            self.enter()
            return True
        return False
    
    def enter(self):
        if not self._on:
            print("[SAFE] Entering...")
            self._on = True
    
    def loop(self, led_pin=2):
        led = machine.Pin(led_pin, machine.Pin.OUT)
        while self._on:
            led.on(); time.sleep(0.2)
            led.off(); time.sleep(0.2)

if __name__ == '__main__':
    d = Diagnostics()
    print(d.run())
