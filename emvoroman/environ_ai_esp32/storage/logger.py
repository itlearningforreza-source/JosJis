"""
ENVIRON AI ESP32 - Data Logger (Lightweight)
"""

import os
import time
from config import STORAGE_FILE, STORAGE_MAX_FILES, STORAGE_MAX_SIZE_KB, STORAGE_FLUSH_EVERY, CSV_HEADER

class DataLogger:
    def __init__(self, filepath=STORAGE_FILE):
        self._fp = filepath
        self._max_files = 3
        self._max_kb = 256
        self._flush_n = 5
        self._buf = []
        self._count = 0
        self._fh = None
        self._size = 0
        self._errors = 0
        
        try:
            d = self._fp.rsplit('/', 1)[0]
            if d: os.mkdir(d)
        except: pass
        
        self._open()
        print("[Log] " + filepath)
    
    def _open(self):
        try:
            exists = False
            try:
                os.stat(self._fp); exists = True
            except: pass
            self._fh = open(self._fp, 'a')
            if not exists:
                self._fh.write(CSV_HEADER)
                self._fh.flush()
            self._size = os.stat(self._fp)[6]
        except Exception as e:
            print("[Log] Open error: " + str(e))
            self._errors += 1
    
    def log(self, ts, temp, hum, adc, ppm, fan, alarm, err):
        fan_s = 'ON' if fan else 'OFF'
        al_s = 'ON' if alarm else 'OFF'
        ts_s = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*time.localtime()[:6])
        t_s = "{:.1f}".format(temp) if temp is not None else ""
        h_s = "{:.1f}".format(hum) if hum is not None else ""
        a_s = str(adc) if adc is not None else ""
        p_s = str(ppm) if ppm is not None else ""
        line = ts_s + "," + t_s + "," + h_s + "," + a_s + "," + p_s + "," + fan_s + "," + al_s + "," + str(err) + "\n"
        
        self._buf.append(line)
        self._count += 1
        
        if len(self._buf) >= self._flush_n:
            self.flush()
        
        if self._size > self._max_kb * 1024:
            self.rotate()
    
    def flush(self):
        if not self._buf or not self._fh:
            return
        try:
            for l in self._buf:
                self._fh.write(l)
            self._fh.flush()
            self._buf.clear()
            self._size = os.stat(self._fp)[6]
        except Exception as e:
            print("[Log] Flush error: " + str(e))
            self._errors += 1
    
    def rotate(self):
        print("[Log] Rotate")
        self.flush()
        if self._fh:
            try: self._fh.close()
            except: pass
        
        for i in range(self._max_files - 1, 0, -1):
            try: os.rename(self._fp + "." + str(i), self._fp + "." + str(i + 1))
            except: pass
        try: os.rename(self._fp, self._fp + ".1")
        except: pass
        self._open()
    
    def log_reading(self, r, fan, alarm, err):
        self.log(time.ticks_ms(), r.get('temp'), r.get('hum'), r.get('adc'), r.get('ppm'), fan, alarm, err)
    
    def get_stats(self):
        return {'file': self._fp, 'records': self._count, 'buf': len(self._buf), 'kb': self._size / 1024, 'errors': self._errors}
    
    def close(self):
        self.flush()
        if self._fh:
            try: self._fh.close()
            except: pass
    
    def health_check(self):
        if self._errors > 3:
            return 'DEGRADED'
        try:
            f = self._fp + '.test'
            with open(f, 'w') as fp: fp.write('t')
            os.remove(f)
            return 'OK'
        except:
            return 'FAILED'

if __name__ == '__main__':
    import config
    config.SIMULATION_MODE = True
    l = DataLogger('/tmp/test.csv')
    for i in range(3):
        l.log_reading({'temp': 25+i, 'hum': 50, 'adc': 1500, 'ppm': 400}, i%2==0, i==2, 0)
        time.sleep(0.1)
    l.flush()
    print(l.get_stats())
    l.close()
