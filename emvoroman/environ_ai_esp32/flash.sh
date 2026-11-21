#!/bin/bash
# ENVIRON AI ESP32 - Flash Script
# Flashes MicroPython firmware and uploads application files

set -e

# Configuration
ESP32_PORT="/dev/ttyUSB0"
BAUD_RATE=115200

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ENVIRON AI ESP32 - Flash Tool${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if port exists
if [ ! -e "$ESP32_PORT" ]; then
    echo -e "${RED}Error: Port $ESP32_PORT not found${NC}"
    echo "Available ports:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "  None found"
    exit 1
fi

echo -e "${GREEN}Found ESP32 at $ESP32_PORT${NC}"
echo ""

# Step 1: Check for firmware file
FIRMWARE_FILE="esp32-firmware.bin"
if [ ! -f "$FIRMWARE_FILE" ]; then
    echo -e "${YELLOW}Firmware file not found: $FIRMWARE_FILE${NC}"
    echo ""
    echo "Please download MicroPython firmware for ESP32:"
    echo "  1. Open browser: https://micropython.org/download/esp32/"
    echo "  2. Download the latest 'ESP32 Generic' .bin file"
    echo "  3. Save as: $PWD/$FIRMWARE_FILE"
    echo "  4. Re-run this script"
    echo ""
    echo "Or use wget/curl with a direct link (check the page for current URL):"
    echo "  wget -O $FIRMWARE_FILE 'https://micropython.org/resources/firmware/esp32-YYYYMMDD-vX.XX.X.bin'"
    echo ""
    exit 1
fi

# Verify firmware file size (should be ~1.5-2MB)
FIRMWARE_SIZE=$(stat -c%s "$FIRMWARE_FILE")
if [ "$FIRMWARE_SIZE" -lt 1000000 ]; then
    echo -e "${RED}Error: Firmware file too small ($FIRMWARE_SIZE bytes)${NC}"
    echo "This appears to be an error page, not firmware."
    echo "Please download the correct firmware from https://micropython.org/download/esp32/"
    exit 1
fi

echo -e "${GREEN}Firmware file OK: $FIRMWARE_FILE ($FIRMWARE_SIZE bytes)${NC}"
echo ""

# Step 1: Erase flash
echo -e "${YELLOW}Step 1: Erasing flash...${NC}"
esptool.py --port "$ESP32_PORT" --baud "$BAUD_RATE" --before default_reset --after hard_reset erase_flash

# Step 2: Flash MicroPython firmware
echo -e "${YELLOW}Step 2: Flashing MicroPython firmware...${NC}"
esptool.py --port "$ESP32_PORT" --baud "$BAUD_RATE" --before default_reset --after hard_reset write_flash -z 0x1000 "$FIRMWARE_FILE"

# Step 3: Wait for reboot
echo -e "${YELLOW}Step 3: Waiting for reboot...${NC}"
sleep 3

# Step 4: Upload application files
echo -e "${YELLOW}Step 4: Uploading application files...${NC}"

FILES=(
    "boot.py"
    "main.py"
    "config.py"
    "sensors/__init__.py"
    "sensors/mq135.py"
    "sensors/dht22.py"
    "actuators/__init__.py"
    "actuators/relay.py"
    "actuators/fan.py"
    "actuators/buzzer.py"
    "decision/__init__.py"
    "decision/engine.py"
    "storage/__init__.py"
    "storage/logger.py"
    "diagnostics/__init__.py"
    "diagnostics/health.py"
    "lib/__init__.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  Uploading $file..."
        mpremote connect "$ESP32_PORT" fs cp "$file" :"$file"
    else
        echo -e "${RED}  Warning: $file not found${NC}"
    fi
done

# Step 5: Verify upload
echo -e "${YELLOW}Step 5: Verifying upload...${NC}"
mpremote connect "$ESP32_PORT" fs ls

# Step 6: Soft reset
echo -e "${YELLOW}Step 6: Soft reset...${NC}"
mpremote connect "$ESP32_PORT" exec "import machine; machine.soft_reset()"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Flash Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The ESP32 should now be running ENVIRON AI."
echo "Connect to serial console to monitor:"
echo "  mpremote connect $ESP32_PORT console"
echo ""
echo "Or use screen:"
echo "  screen $ESP32_PORT 115200"
echo ""
