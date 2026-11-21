#!/bin/bash
# ENVIRON AI ESP32 - Ultra Simple & Robust Flash
set -e

PORT="/dev/ttyUSB0"
BAUD="115200"
FIRMWARE="esp32-firmware.bin"

echo "=== ENVIRON AI ESP32 Simple Flash ==="
echo "Port: $PORT | Baud: $BAUD | Firmware: $FIRMWARE"

[ ! -f "$FIRMWARE" ] && { echo "ERROR: $FIRMWARE tidak ditemukan"; exit 1; }
SIZE=$(stat -c%s "$FIRMWARE")
[ "$SIZE" -lt 1000000 ] && { echo "ERROR: Firmware terlalu kecil ($SIZE bytes)"; exit 1; }
echo "Firmware OK: $SIZE bytes"

[ ! -e "$PORT" ] && { echo "ERROR: $PORT tidak ada. Recolok USB."; exit 1; }

echo ""
echo "⚠️  MANUAL BOOTLOADER MODE:"
echo "   1. Tekan tahan BOOT (GPIO0)"
echo "   2. Tekan & lepas EN/RST"
echo "   3. Lepas BOOT"
echo "   4. Tekan ENTER di sini..."
read -p "Tekan ENTER saat siap..."

echo ""
echo "=== ERASE FLASH ==="
esptool.py --port "$PORT" --baud 115200 --before default-reset --after no-reset erase-flash

echo ""
echo "=== FLASH FIRMWARE ==="
esptool.py --port "$PORT" --baud 115200 --before default-reset --after hard-reset write-flash -z 0x1000 "$FIRMWARE"

echo ""
echo "=== UPLOAD APP FILES ==="
for f in boot.py main.py config.py \
         sensors/__init__.py sensors/mq135.py sensors/dht22.py \
         actuators/__init__.py actuators/relay.py actuators/fan.py actuators/buzzer.py \
         decision/__init__.py decision/engine.py \
         storage/__init__.py storage/logger.py \
         diagnostics/__init__.py diagnostics/health.py \
         lib/__init__.py; do
  [ -f "$f" ] && mpremote connect "$PORT" fs cp "$f" :"$f" && echo "  ✓ $f"
done

echo ""
echo "=== VERIFY & RESET ==="
mpremote connect "$PORT" fs ls
mpremote connect "$PORT" exec "import machine; machine.soft_reset()"
echo "=== DONE ==="
