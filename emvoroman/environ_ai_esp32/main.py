"""
ENVIRON AI ESP32 - Main Application (Ultra-Lightweight v0.2.0)
Standalone environmental monitoring - optimized for ESP32 DevKit V1
"""

import gc
import time
import machine
import sys

from config import *
from sensors.mq135 import MQ135
from sensors.dht22 import DHT22Sensor
from actuators.fan import FanController
from actuators.buzzer import Buzzer
from decision.engine import DecisionEngine
from storage.logger import DataLogger
from diagnostics.health import Diagnostics, Watchdog, SafeMode

# Global state - single dict (saves RAM vs class)
S = {'run': True, 'boot': time.ticks_ms(), 'err': 0}

def setup():
    print("\n=== ENVIRON AI v" + FIRMWARE_VERSION + " ===")
    print("Device: " + DEVICE_ID + " | Sim: " + str(SIMULATION_MODE))
    print("Free heap: " + str(gc.mem_free()) + " bytes\n")
    
    H = {}
    H['wdt'] = Watchdog()
    H['diag'] = Diagnostics()
    H['diag'].record_boot(True)
    H['safe'] = SafeMode(H['diag'])
    
    print("[Init] Sensors...")
    H['mq'] = MQ135()
    H['dht'] = DHT22Sensor()
    
    print("[Init] Actuators...")
    H['fan'] = FanController()
    H['buz'] = Buzzer()
    
    print("[Init] Logic & Storage...")
    H['dec'] = DecisionEngine()
    H['log'] = DataLogger()
    
    if H['safe'].check_and_enter():
        H['safe'].run_safe_loop()
        return False
    
    read_sensors(H)
    H['buz'].alarm_info()
    gc.collect()
    print("[Init] Done. Heap: " + str(gc.mem_free()) + " bytes\n")
    return H

def read_sensors(H):
    r = {'t': time.ticks_ms()}
    H['dht'].read()
    r['temp'] = H['dht']._last_temp
    r['hum'] = H['dht']._last_humidity
    r['dht_ok'] = H['dht'].health_check() == 'OK'
    
    r['adc'] = H['mq'].read_adc()
    r['ppm'] = H['mq'].estimate_ppm()
    r['mq_ok'] = H['mq'].health_check() == 'OK'
    r['mq_cal'] = H['mq']._calibrated
    
    r['fan'] = H['fan']._relay.is_on()
    return r

def update_fan(H, r):
    try:
        H['fan'].update(r.get('temp'), r.get('hum'), r.get('adc'))
    except:
        S['err'] |= 4

def decide(H, r):
    try:
        d = H['dec'].evaluate({
            'temp_c': r.get('temp'), 'humidity_pct': r.get('hum'),
            'mq135_adc': r.get('adc'),
            'dht_health': 'OK' if r.get('dht_ok') else 'FAILED',
            'mq135_health': 'OK' if r.get('mq_ok') else 'FAILED',
            'mq135_calibrated': r.get('mq_cal', False)
        })
        if d['actions'].get('alarm_buzzer'):
            sev = d.get('severity', 'NORMAL')
            if sev == 'CRITICAL':
                H['buz'].alarm_critical()
            else:
                H['buz'].alarm_warning()
        else:
            H['buz'].stop()
        return d
    except:
        S['err'] |= 8
        H['buz'].alarm_sensor_fault()
        return None

def log_data(H, r, d):
    try:
        H['log'].log_reading(r, r.get('fan', False), H['dec'].is_alarm_active(), S['err'])
    except:
        S['err'] |= 4

def loop(H):
    S['run'] = True
    last_s = last_log = last_diag = 0
    
    while S['run']:
        now = time.ticks_ms()
        
        if H['wdt'].should_feed():
            H['wdt'].feed()
        
        if time.ticks_diff(now, last_s) >= SENSOR_READ_INTERVAL_MS:
            r = read_sensors(H)
            update_fan(H, r)
            d = decide(H, r)
            last_s = now
            
            if time.ticks_diff(now, S['boot']) % 30000 < 100:
                uptime = time.ticks_diff(now, S['boot']) // 1000
                fan_str = 'ON' if r.get('fan') else 'OFF'
                print("[" + str(uptime) + "s] T:" + str(r.get('temp')) + "C H:" + str(r.get('hum')) + "% ADC:" + str(r.get('adc')) + " Fan:" + fan_str + " Err:0x" + format(S['err'], '02X') + " Heap:" + str(gc.mem_free()))
        
        if time.ticks_diff(now, last_log) >= STORAGE_INTERVAL_MS:
            r = read_sensors(H)
            d = decide(H, r)
            log_data(H, r, d)
            last_log = now
            gc.collect()
        
        if time.ticks_diff(now, last_diag) >= 60000:
            gc.collect()
            if gc.mem_free() < 15000:
                H['diag'].add_warning('mem', 'Low heap: ' + str(gc.mem_free()))
            last_diag = now
        
        H['safe'].check_and_enter()
        time.sleep_ms(50)
    
    print("[Main] Loop exited")

if __name__ == '__main__':
    try:
        H = setup()
        if H:
            loop(H)
    except KeyboardInterrupt:
        print("\n[Stop] User interrupt")
    except Exception as e:
        print("[FATAL] " + str(e))
        S['err'] |= 128
        try:
            if 'buz' in locals() or 'buz' in globals():
                pass
        except:
            pass
    finally:
        try:
            if 'H' in locals() and 'fan' in H:
                H['fan'].force_off()
            if 'H' in locals() and 'buz' in H:
                H['buz'].stop()
            if 'H' in locals() and 'log' in H:
                H['log'].close()
        except:
            pass
        print("[Stop] Done")
