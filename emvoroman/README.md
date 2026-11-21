# ENVIRON AI - Indoor Environmental Monitoring System

> **Complete indoor environmental monitoring & control system**  
> Dual architecture: **Python backend (Fedora)** + **MicroPython firmware (ESP32 DevKit V1)**

---

## Project Structure

```
emvoroman/
├── environ_ai/                 # Python Backend (Fedora Linux)
│   ├── __main__.py            # CLI entry point
│   ├── config/settings.py     # Central configuration
│   ├── core/orchestrator.py   # Main loop (5-min updates)
│   ├── data/
│   │   ├── database.py        # SQLite + WAL mode
│   │   └── fetcher.py         # OpenWeatherMap API client
│   ├── models/estimator.py    # Physics-based + ML models
│   ├── dashboard/app.py       # Streamlit web dashboard
│   └── tests/                 # Unit tests (24 passing)
│
├── environ_ai_esp32/          # MicroPython Firmware (ESP32 DevKit V1)
│   ├── boot.py                # Auto-start + safe mode
│   ├── main.py                # Ultra-light main loop (3s cycle)
│   ├── config.py              # All hardware/config params
│   ├── flash_simple.sh        # Manual bootloader flasher
│   ├── esp32-firmware.bin     # MicroPython v1.23.0 GENERIC
│   ├── sensors/
│   │   ├── mq135.py           # ADC + R0 calibration
│   │   └── dht22.py           # Temp/humidity + retry
│   ├── actuators/
│   │   ├── relay.py           # Active LOW relay driver
│   │   ├── fan.py             # Hysteresis + cooldown
│   │   └── buzzer.py          # 4 patterns (CRIT/WARN/INFO/FAULT)
│   ├── decision/engine.py     # Thresholds + sensor faults
│   ├── storage/logger.py      # CSV + rotation (256KB/3 files)
│   ├── diagnostics/health.py  # Watchdog + heap + safe mode
│   └── README.md              # ESP32-specific docs
│
├── data/                      # SQLite database (auto-created)
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── start.sh                   # Backend startup script
└── README.md                  # This file
```

---

## System Overview

### Python Backend (environ_ai)
- **Purpose**: Cloud-connected monitoring with historical data & web dashboard
- **OS**: Fedora Linux (Intel i3, 8GB RAM)
- **Data Source**: OpenWeatherMap API (weather + air quality)
- **Model**: Physics-based indoor estimation (no indoor sensors)
- **Storage**: SQLite with WAL mode, 30-day retention
- **Dashboard**: Streamlit + Plotly (real-time charts + confidence intervals)
- **Interval**: 5-minute updates, 6-hour predictions

### ESP32 Firmware (environ_ai_esp32)
- **Purpose**: Standalone offline monitoring & local control
- **Hardware**: ESP32 DevKit V1 (no PSRAM)
- **Sensors**: MQ-135 (ADC), DHT22 (temp/humidity)
- **Actuators**: Relay (fan), Buzzer (alarms)
- **Storage**: CSV on flash with rotation
- **Firmware**: MicroPython v1.23.0 GENERIC (non-SPIRAM, 1.7MB)
- **Interval**: 3-second sensor cycle, 5-min logging

---

## Hardware Requirements

### ESP32 DevKit V1 Connections

| Component | GPIO | Notes |
|-----------|------|-------|
| MQ-135 AOUT | 34 | ADC1_CH6 (input only) |
| DHT22 DATA | 4 | 4.7k pull-up required |
| Relay IN | 5 | Active LOW module |
| Buzzer + | 18 | PWM capable |
| Status LED | 2 | Built-in (active LOW) |
| BOOT button | 0 | Safe mode trigger |

### Missing Hardware (Simulation Mode Enabled)
- Relay 1-channel module
- DC Fan 12V + driver
- Active Buzzer 5V
- 12V Power Adapter

---

## Quick Start

### 1. Python Backend (Fedora)

```bash
cd /home/rezaahmadkhairuddin/emvoroman

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set API key (get from openweathermap.org)
export OPENWEATHER_API_KEY="your_key_here"

# Initialize database
python -m environ_ai --init-db

# Test single update
python -m environ_ai --once

# Run daemon (5-min updates)
python -m environ_ai &

# Or launch dashboard
python -m environ_ai --dashboard
# Open http://localhost:8501
```

### 2. ESP32 Firmware

```bash
cd environ_ai_esp32

# 1. Download stable firmware (non-SPIRAM, ~1.7MB)
curl -L -o esp32-firmware.bin \
  'https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin'

# 2. Verify size (~1.7 MB)
ls -la esp32-firmware.bin

# 3. Flash with MANUAL BOOTLOADER (most reliable)
./flash_simple.sh

# Follow on-screen:
# 1. Hold BOOT button (GPIO0)
# 2. Press & release EN/RST
# 3. Release BOOT
# 4. Press ENTER in terminal

# 4. Monitor
mpremote connect /dev/ttyUSB0 console
# Or: screen /dev/ttyUSB0 115200
```

---

## Configuration

### Python Backend (environ_ai/config/settings.py)

```python
# Key settings
update_interval_minutes: 5          # Update frequency
indoor_temp_offset_c: 2.0           # Indoor = outdoor + 2C
indoor_humidity_factor: 0.85        # Indoor RH = outdoor x 0.85
infiltration_factor: 0.3            # PM2.5 indoor = outdoor x 0.3
history_retention_days: 30          # Data retention
```

### ESP32 Firmware (environ_ai_esp32/config.py)

```python
# Sensor timing
SENSOR_READ_INTERVAL_MS = 3000      # 3-second cycle
STORAGE_INTERVAL_MS = 300000        # 5-min logging

# Fan thresholds (hysteresis)
TEMP_FAN_ON = 28.0      # C
TEMP_FAN_OFF = 26.0     # C
HUMIDITY_FAN_ON = 75.0  # %
HUMIDITY_FAN_OFF = 70.0 # %

# MQ-135 (ADC raw - no false ppm)
MQ135_ADC_FAN_ON = 2500
MQ135_ADC_FAN_OFF = 2000
MQ135_ADC_ALARM = 3200

# MQ-135 CALIBRATION (MANDATORY!)
MQ135_R0 = 76000        # Calibrate in fresh air after 5min warmup
```

---

## Data & Accuracy

### Python Backend
- **Estimation Method**: Physics-based (no indoor sensors)
- **Confidence Intervals**: 95% CI on all estimates
- **Accuracy Claim**: 85%+ for temperature/humidity (vs outdoor reference)
- **PM2.5 Indoor**: Estimation only (infiltration model)

### ESP32 Firmware
- **MQ-135**: ADC raw thresholds (no ppm claims without calibration)
- **DHT22**: 0.5C, 2% RH (sensor spec)
- **Accuracy Target**: 85%+ for threshold detection
- **Calibration Required**: MQ-135 R0 in fresh air (5min warmup)

---

## Safety & Reliability

| Feature | Python Backend | ESP32 Firmware |
|---------|----------------|----------------|
| Watchdog | N/A | Hardware WDT (20s) |
| Safe Mode | N/A | 3 boot failures blink LED |
| Error Flags | Bitmask logging | Bitmask + CSV |
| Data Rotation | 30-day SQLite | 3 files x 256KB CSV |
| Recovery | Auto-restart | Auto-reset + safe mode |

---

## Testing

```bash
# Python backend tests
cd /home/rezaahmadkhairuddin/emvoroman
source venv/bin/activate
pytest environ_ai/tests/ -v
# 24 tests passing

# ESP32 simulation test
cd environ_ai_esp32
python3 -c "
import config; config.SIMULATION_MODE = True
from sensors.mq135 import MQ135
from sensors.dht22 import DHT22Sensor
mq = MQ135(); dht = DHT22Sensor()
print('MQ135:', mq.get_status())
print('DHT22:', dht.get_status())
"
```

---

## Monitoring & Debugging

### Python Dashboard
- **URL**: http://localhost:8501
- **Features**: Real-time charts, confidence intervals, predictions, sensor quality

### ESP32 Serial Console
```bash
mpremote connect /dev/ttyUSB0 console
# Or: screen /dev/ttyUSB0 115200
```

**Useful REPL Commands:**
```python
# Sensor status
from sensors.mq135 import MQ135
from sensors.dht22 import DHT22Sensor
mq = MQ135(); dht = DHT22Sensor()
print(mq.get_status()); print(dht.get_status())

# Calibrate MQ-135 (REQUIRED)
mq.calibrate_r0()  # Run in fresh air after 5min warmup
print("R0 =", mq._r0)  # Update config.py MQ135_R0

# Manual fan control
from actuators.fan import FanController
fan = FanController()
fan.force_on(); fan.force_off(); fan.auto()

# Check storage
from storage.logger import DataLogger
log = DataLogger()
print(log.get_stats())

# System diagnostics
from diagnostics.health import Diagnostics
diag = Diagnostics()
print(diag.run())
```

---

## Important Notes

### Scientific Limitations
- **Python backend**: Indoor estimates are **physics-based approximations**, not measurements
- **ESP32 MQ-135**: Without calibration gas, **ppm values are estimates only**
- **No health decisions**: Do not use for medical/safety-critical purposes
- **Validation required**: Compare with actual indoor sensors when available

### Hardware Safety
- **Relay**: Active LOW, 5V logic, isolate from 12V fan circuit
- **MQ-135**: 5V heater, power from 5V pin (not 3.3V)
- **DHT22**: 3.3V logic, 4.7k pull-up on data line
- **Buzzer**: Active buzzer, 5V, PWM on GPIO18

### Flash Wear
- ESP32 flash: 10,000 write cycles
- Current config: 5-min logging = 100 writes/day = 2.7 years
- Rotation limits: 3 files x 256KB = 768KB max

---

## License

MIT License - Free for personal and commercial use.

---

## Contributing

1. Keep it simple - less code, fewer dependencies
2. Prioritize reliability over features
3. Document scientific assumptions
4. Add tests for new functionality
5. No hardcoded secrets

---

## Support

**Repository**: https://github.com/itlearningforreza-source/JosJis  
**Issues**: GitHub Issues tab  
**Documentation**: /environ_ai_esp32/README.md for ESP32-specific details

---

**ENVIRON AI** - *Simple, Reliable, Scientifically Honest Indoor Environmental Monitoring*
