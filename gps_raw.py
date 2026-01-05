import serial
import time

# Configure the serial connection
# Most USB GPS dongles run at 9600 baud. If this fails, we try 4800.
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

print("📡 CONNECTING TO SATELLITES...")
print("--------------------------------")

try:
    while True:
        line = ser.readline().decode('utf-8', errors='replace').strip()
        if line:
            print(f"RAW DATA: {line}")
            
            # Simple check to see if we have a lock
            if line.startswith("$GPGGA"):
                parts = line.split(',')
                # If parts[2] (Latitude) is empty, we don't have a fix yet
                if not parts[2]:
                    print("   ⚠️  Satellites visible, but NO FIX yet (Keep antenna near window!)")
                else:
                    print(f"   ✅ LOCK ACQUIRED: {parts[2]} N, {parts[4]} W")

except KeyboardInterrupt:
    print("\n🛑 Scanning stopped.")
finally:
    ser.close()