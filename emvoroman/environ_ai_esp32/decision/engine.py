"""
ENVIRON AI ESP32 - Decision Engine (Lightweight)
"""

import time
from config import TEMP_ALARM_HIGH, TEMP_ALARM_LOW, HUMIDITY_ALARM_HIGH, MQ135_ADC_ALARM

class DecisionEngine:
    def __init__(self):
        self._alarms = {'temp': False, 'hum': False, 'aq': False, 'fault': False}
        self._active = False
        self._count = 0
        self._thresholds = {
            'th': TEMP_ALARM_HIGH, 'tl': TEMP_ALARM_LOW,
            'hh': HUMIDITY_ALARM_HIGH, 'aq': MQ135_ADC_ALARM
        }
    
    def evaluate(self, r):
        alarms = {}
        actions = {}
        sev = 'NORMAL'
        
        t = r.get('temp')
        h = r.get('hum')
        a = r.get('adc')
        dh = r.get('dht_ok', False)
        mh = r.get('mq_ok', False)
        mc = r.get('mq_cal', False)
        
        # Temp
        ta = False
        if t is not None:
            if t >= self._thresholds['th']:
                alarms['th'] = True; ta = True; sev = 'CRITICAL'
            elif t <= self._thresholds['tl']:
                alarms['tl'] = True; ta = True; sev = 'WARNING' if sev == 'NORMAL' else sev
        else:
            alarms['tmiss'] = True; sev = 'WARNING'
        
        # Humidity
        ha = False
        if h is not None:
            if h >= self._thresholds['hh']:
                alarms['hh'] = True; ha = True; sev = 'WARNING' if sev == 'NORMAL' else sev
        else:
            alarms['hmiss'] = True; sev = 'WARNING'
        
        # Air quality
        aa = False
        if a is not None:
            if a >= self._thresholds['aq']:
                alarms['aq'] = True; aa = True; sev = 'WARNING' if sev == 'NORMAL' else sev
        else:
            alarms['amiss'] = True; sev = 'WARNING'
        
        # Sensor faults
        fault = False
        if not dh:
            alarms['df'] = True; fault = True; sev = 'WARNING' if sev == 'NORMAL' else sev
        if not mh:
            alarms['mf'] = True; fault = True; sev = 'WARNING' if sev == 'NORMAL' else sev
        if not mc:
            alarms['uncal'] = True
        
        any_alarm = ta or ha or aa
        actions = {'buzzer': any_alarm, 'fan': ta or ha or aa, 'log': any_alarm}
        
        if any_alarm:
            self._active = True
            self._count += 1
        else:
            self._active = False
        
        return {'alarms': alarms, 'actions': actions, 'severity': sev, 'active': self._active, 'count': self._count}
    
    def is_alarm_active(self):
        return self._active
    
    def get_status(self):
        return {'active': self._active, 'count': self._count}

if __name__ == '__main__':
    d = DecisionEngine()
    print(d.evaluate({'temp': 25, 'hum': 50, 'adc': 1500, 'dht_ok': True, 'mq_ok': True, 'mq_cal': True}))
    print(d.evaluate({'temp': 36, 'hum': 50, 'adc': 1500, 'dht_ok': True, 'mq_ok': True, 'mq_cal': True}))
