# ENVIRON AI ESP32 Firmware

MicroPython firmware for ESP32 DevKit V1 environmental monitoring and control system.

## Hardware Requirements

### Required (Available)
- **ESP32 DevKit V1** (ESP32-WROOM-32)
- **MQ-135** Gas Sensor (ADC output)
- **DHT22** Temperature & Humidity Sensor

### Required (Not Yet Available - Simulation Mode)
- **Relay 1 Channel** (5V/3.3V compatible, active LOW)
- **DC Fan 12V** (with appropriate driver/relay)
- **Active Buzzer** (5V)
- **12V Power Adapter** (for fan)

## Pin Mapping (ESP32 DevKit V1)

| Component | GPIO | Notes |
|-----------|------|-------|
| MQ-135 ADC | 34 | ADC1_CH6 (input only) |
| DHT22 Data | 4 | With pull-up |
| Relay Control | 5 | Active LOW typical |
| Buzzer PWM | 18 | PWM capable |
| Status LED | 2 | Built-in (active LOW) |
| Safe Mode | 0 | Boot button (pull-up) |

## Quick Start

### 1. Prerequisites (Fedora Linux)

```bash
# Install required tools
sudo dnf install python3-pip esptool

# Install mpremote
pip3 install --user mpremote esptool

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### 2. Flash Firmware

```bash
cd environ_ai_esp32

# Make flash script executable
chmod +x flash.sh

# Connect ESP32 via USB
# Run flash script (will download MicroPython firmware, flash it, and upload app)
./flash.sh
```

### 3. Monitor Serial Console

```bash
# Using mpremote
mpremote connect /dev/ttyUSB0 console

# Or using screen
screen /dev/ttyUSB0 115200

# Or using minicom
minicom -D /dev/ttyUSB0 -b 115200
```

## Configuration

Edit `config.py` to adjust:

- **Pin assignments** (if using different GPIOs)
- **Thresholds** for fan/alarm triggers
- **Calibration values** for MQ-135
- **Simulation mode** (set False when hardware connected)

### Key Settings

```python
# Fan control thresholds
TEMP_FAN_ON = 28.0      # °C
TEMP_FAN_OFF = 26.0     # °C (hysteresis)
HUMIDITY_FAN_ON = 75.0  # %
HUMIDITY_FAN_OFF = 70.0 # %

# Alarm thresholds
TEMP_ALARM_HIGH = 35.0  # °C
TEMP_ALARM_LOW = 15.0   # °C
HUMIDITY_ALARM_HIGH = 90.0 # %
MQ135_ADC_ALARM = 3200  # Raw ADC value

# MQ-135 Calibration (MUST calibrate in clean air!)
MQ135_R0 = 76000        # Ohms - calibrate in fresh air
```

## Architecture

```
environ_ai_esp32/
├── boot.py              # Auto-start on boot
├── main.py              # Main application loop
├── config.py            # All configuration
├── flash.sh             # Flash script
├── sensors/
│   ├── __init__.py
│   ├── mq135.py         # MQ-135 ADC driver
│   └── dht22.py         # DHT22 driver
├── actuators/
│   ├── __init__.py
│   ├── relay.py         # Relay driver
│   ├── fan.py           # Fan controller with hysteresis
│   └── buzzer.py        # Buzzer with patterns
├── decision/
│   ├── __init__.py
│   └── engine.py        # Decision engine
├── storage/
│   ├── __init__.py
│   └── logger.py        # CSV logger with rotation
├── decision/
│   ├── __init__.py
│   └── engine.py
├── diagnostics/
│   ├── __init__.py
│   └── health.py        # Watchdog, health monitoring
└── lib/
    └── __init__.py
```

## Main Loop Timing

| Task | Interval |
|------|----------|
| Sensor Reading | 2 seconds |
| Data Logging | 5 minutes |
| Diagnostics | 1 minute |
| Status Print | 30 seconds |
| Watchdog Feed | 5 seconds |

## MQ-135 Calibration (IMPORTANT)

The MQ-135 **MUST** be calibrated in clean air before use:

1. Power on ESP32 in fresh, well-ventilated air
2. Wait 5+ minutes for sensor warm-up
3. Run calibration via REPL:
   ```python
   from sensors.mq135 import MQ135
   sensor = MQ135()
   sensor.calibrate_r0()  # Takes ~5 seconds
   print(f"R0 = {sensor._r0}")
   ```
4. Update `MQ135_R0` in config.py with the calibrated value

**Without calibration, ppm values are meaningless!** Use ADC raw values for reliable threshold-based control.

## Simulation Mode

When hardware is not fully connected, set `SIMULATION_MODE = True` in config.py:

- Simulates sensor readings
- Logs simulated data
- Tests logic without hardware

## Data Logging

- **Format**: CSV with timestamp, temp, humidity, MQ135 ADC, estimated ppm, fan state, alarm state, error flags
- **Location**: `/data/environ_log.csv`
- **Rotation**: 7 files, 512KB max each
- **Flush**: Every 10 records

## Safety Features

- **Watchdog**: 30s timeout, fed every 5s
- **Hysteresis**: Fan on/off thresholds prevent rapid cycling
- **Minimum Run Time**: Fan runs at least 1 minute
- **Cooldown**: 2 minutes between fan cycles
- **Safe Mode**: Entered after 3 consecutive boot failures
- **Error Flags**: Bitmask for tracking issues

## Alarm Patterns

| Condition | Pattern |
|-----------|---------|
| Critical (high temp) | 3 fast beeps, repeat |
| Warning (high humidity/AQ) | 2 beeps, long pause |
| Sensor Fault | Long-short-long |
| Info | Single short beep |

## Troubleshooting

### ESP32 not detected
```bash
# Check USB devices
lsusb
ls /dev/ttyUSB* /dev/ttyACM*
```

### Permission denied on serial port
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### MQ-135 readings unstable
- Ensure stable 3.3V power
- Add 10uF + 0.1uF capacitors near sensor VCC/GND
- Keep sensor away from WiFi antenna
- Allow 24-48h burn-in for new sensors

### DHT22 read failures
- Check pull-up resistor (4.7k-10k on data line)
- Ensure 2+ second intervals between reads
- Check wiring length (< 20m)

### Watchdog resets
- Check for blocking code in main loop
- Ensure `feed_watchdog()` called regularly
- Increase `WDT_TIMEOUT_MS` if needed

## File System on ESP32

```
/
├── boot.py
├── main.py
├── config.py
├── sensors/
├── actuators/
├── decision/
├── storage/
├── diagnostics/
├── lib/
└── data/
    └── environ_log.csv
```

## Updating Firmware

```bash
cd environ_ai_esp32
./flash.sh
```

Or upload individual files:
```bash
mpremote connect /dev/ttyUSB0 fs cp main.py :main.py
mpremote connect /dev/ttyUSB0 exec "import machine; machine.soft_reset()"
```

## Monitoring via REPL

```bash
mpremote connect /dev/ttyUSB0 repl
```

Useful commands:
```python
# Check sensor status
from sensors.mq135 import MQ135
from sensors.dht22 import DHT22Sensor
mq = MQ135()
dht = DHT22Sensor()
print(mq.get_status())
print(dht.get_status())

# Check fan
from actuators.fan import FanController
fan = FanController()
print(fan.get_status())

# Check storage
from storage.logger import DataLogger
log = DataLogger()
print(log.get_stats())

# Calibrate MQ135
mq.calibrate_r0()

# Manual fan control
fan.force_on()
fan.force_off()
fan.resume_auto()
```

## License

MIT License - Free for personal and commercial use.

## Support

For issues, check:
1. Serial console output
2. Error flags in status output
3. Log files in `/data/`
4. Diagnostics output every minute

---

**ENVIRON AI ESP32** - Offline-first environmental monitoring for ESP32
