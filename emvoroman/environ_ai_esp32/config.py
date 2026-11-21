"""
ENVIRON AI ESP32 - Configuration (Lightweight v0.2.0)
All configurable parameters - optimized for ESP32 DevKit V1 standard (no PSRAM)
"""

# ============================================================
# HARDWARE PIN MAPPING (ESP32 DevKit V1)
# ============================================================
PIN_MQ135_ADC = 34      # GPIO34 - ADC1_CH6 (input only, no pull-up)
PIN_DHT22 = 4           # GPIO4 - DHT22 data
PIN_RELAY = 5           # GPIO5 - Relay control (active LOW typical)
PIN_BUZZER = 18         # GPIO18 - Buzzer PWM
PIN_LED_STATUS = 2      # GPIO2 - Built-in LED (active LOW)

# ============================================================
# ADC CONFIG (Lightweight: single sample, no moving avg buffer)
# ============================================================
ADC_ATTEN = 3           # ADC.ATTN_11DB = 3.3V range
ADC_WIDTH = 12          # 12-bit resolution (0-4095)
ADC_SAMPLES = 3         # Reduced from 10 to 3 (save CPU/RAM)
ADC_SETTLE_MS = 1       # Reduced from 2 to 1 ms

# MQ-135 CALIBRATION (MANDATORY - calibrate in fresh air!)
MQ135_R0 = 76000        # Ohms - placeholder, MUST calibrate
MQ135_CO2_M = -0.337    # Slope for CO2 estimation
MQ135_CO2_B = 0.717     # Intercept

# ============================================================
# DHT22 CONFIG (Lightweight)
# ============================================================
DHT22_RETRIES = 2       # Reduced from 3 to 2
DHT22_RETRY_DELAY_MS = 300
DHT22_MIN_INTERVAL_MS = 2000

# ============================================================
# TIMING (Lightweight intervals)
# ============================================================
SENSOR_READ_INTERVAL_MS = 3000      # Increased from 2000 to 3000 (save CPU)
STORAGE_INTERVAL_MS = 300000        # 5 minutes (unchanged)

# ============================================================
# THRESHOLDS (Use ADC raw for reliability - no false ppm claims)
# ============================================================
TEMP_FAN_ON = 28.0
TEMP_FAN_OFF = 26.0
HUMIDITY_FAN_ON = 75.0
HUMIDITY_FAN_OFF = 70.0
MQ135_ADC_FAN_ON = 2500
MQ135_ADC_FAN_OFF = 2000

# Alarm thresholds
TEMP_ALARM_HIGH = 35.0
TEMP_ALARM_LOW = 15.0
HUMIDITY_ALARM_HIGH = 90.0
MQ135_ADC_ALARM = 3200

# ============================================================
# ACTUATOR (Lightweight timing)
# ============================================================
RELAY_ACTIVE_LOW = True
FAN_MIN_RUN_MS = 30000      # Reduced from 60s to 30s
FAN_COOLDOWN_MS = 60000     # Reduced from 120s to 60s

BUZZER_FREQ = 2000
BUZZER_DUTY = 512           # 50% duty (10-bit PWM: 0-1023)

# ============================================================
# STORAGE (Lightweight)
# ============================================================
STORAGE_FILE = '/data/environ_log.csv'
STORAGE_MAX_FILES = 3       # Reduced from 7 to 3 days
STORAGE_MAX_SIZE_KB = 256   # Reduced from 512 to 256 KB
STORAGE_FLUSH_EVERY = 5     # Reduced from 10 to 5 records

CSV_HEADER = "timestamp,temp_c,humidity_pct,mq135_adc,mq135_est_ppm,fan_state,alarm_state,error_flags
"

# ============================================================
# WATCHDOG & RELIABILITY (Lightweight)
# ============================================================
WDT_TIMEOUT_MS = 20000      # Reduced from 30s to 20s
WDT_FEED_INTERVAL_MS = 5000

MAX_BOOT_FAILURES = 3
SAFE_MODE_PIN = 0           # GPIO0 (boot button)

# ============================================================
# DIAGNOSTICS
# ============================================================
DIAG_INTERVAL_MS = 60000    # 60 seconds
HEAP_WARN_THRESHOLD = 15000 # Warn if free heap < 15KB

# ============================================================
# SIMULATION MODE
# ============================================================
SIMULATION_MODE = True      # Set False when hardware connected
SIM_TEMP_BASE = 27.0
SIM_HUMIDITY_BASE = 60.0
SIM_MQ135_BASE = 1500

# ============================================================
# VERSION
# ============================================================
FIRMWARE_VERSION = "0.2.0-light"
DEVICE_ID = "ENVIRON-AI-001"
