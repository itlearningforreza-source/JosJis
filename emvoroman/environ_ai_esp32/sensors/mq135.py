"""
ENVIRON AI ESP32 - MQ-135 Gas Sensor (Lightweight)
ADC raw reading with minimal filtering. No false ppm claims.
"""

from machine import ADC, Pin
import time
import math
from config import PIN_MQ135_ADC, ADC_ATTEN, ADC_WIDTH, ADC_SAMPLES, ADC_SETTLE_MS, MQ135_R0, MQ135_CO2_M, MQ135_CO2_B, SIMULATION_MODE, SIM_MQ135_BASE

class MQ135:
    def __init__(self):
        self._adc = ADC(Pin(PIN_MQ135_ADC))
        self._adc.atten(ADC_ATTEN)
        self._adc.width(ADC_WIDTH)
        self._last_adc = 0
        self._error_count = 0
        self._r0 = MQ135_R0
        self._calibrated = False
    
    def read_adc(self):
        if SIMULATION_MODE:
            import random
            val = SIM_MQ135_BASE + random.randint(-50, 50)
            self._last_adc = max(0, min(4095, val))
            return self._last_adc
        
        total = 0
        valid = 0
        for _ in range(ADC_SAMPLES):
            try:
                val = self._adc.read()
                if 0 <= val <= 4095:
                    total += val
                    valid += 1
            except:
                self._error_count += 1
            time.sleep_ms(ADC_SETTLE_MS)
        
        if valid == 0:
            self._error_count += 1
            return self._last_adc
        
        avg = total // valid
        self._last_adc = avg
        return avg
    
    def estimate_rs(self, adc_val=None):
        if adc_val is None:
            adc_val = self._last_adc
        if adc_val <= 0:
            return None
        vout = (adc_val / 4095.0) * 3.3
        if vout <= 0:
            return None
        return ((3.3 - vout) / vout) * 10000.0
    
    def estimate_ppm(self, adc_val=None):
        rs = self.estimate_rs(adc_val)
        if rs is None or self._r0 <= 0:
            return None
        try:
            ratio = rs / self._r0
            if ratio <= 0:
                return None
            log_ratio = math.log10(ratio)
            ppm = 10 ** ((log_ratio - MQ135_CO2_B) / MQ135_CO2_M)
            return max(0, int(ppm))
        except:
            return None
    
    def calibrate_r0(self, samples=20, delay_ms=50):
        print("[MQ135] Calibrating R0 in fresh air...")
        readings = []
        for i in range(samples):
            adc = self.read_adc()
            rs = self.estimate_rs(adc)
            if rs:
                readings.append(rs)
            time.sleep_ms(delay_ms)
        
        if len(readings) < 5:
            print("[MQ135] Calibration failed")
            return False
        
        readings.sort()
        self._r0 = readings[len(readings) // 2]
        self._calibrated = True
        print("[MQ135] R0 = " + str(int(self._r0)) + " ohms")
        return True
    
    def set_r0(self, r0):
        self._r0 = r0
        self._calibrated = True
    
    def health_check(self):
        if self._error_count > 10:
            return 'DEGRADED'
        if not self._calibrated:
            return 'UNCALIBRATED'
        return 'OK'
    
    def get_status(self):
        return {
            'adc': self._last_adc,
            'rs': self.estimate_rs(),
            'ppm': self.estimate_ppm(),
            'r0': self._r0,
            'calibrated': self._calibrated,
            'errors': self._error_count
        }

def test_mq135():
    import config
    config.SIMULATION_MODE = True
    s = MQ135()
    for _ in range(3):
        print("ADC:", s.read_adc(), "Status:", s.get_status())
        time.sleep(1)

if __name__ == '__main__':
    test_mq135()
