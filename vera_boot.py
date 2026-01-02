import platform
import psutil
import datetime
import os
import sys

def clear_screen():
    #Clears the terminal for a dashboard effect
    os.system('clear')

def check_system():
    clear_screen()
    print(f"🔹 V.E.R.A. SYSTEM DIAGNOSIC")
    print(f"📍 Host: {platform.node()} | User: {os.getlogin()}")
    print(f"🕒 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 48)
    
    #OS Info
    print(f"🖥️ OS: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    #CPU Check
    cpu_freq = psutil.cpu_freq()
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"🧠 CPU: {cpu_usage}% Load | Speed: {cpu_freq.current:.0f}MHz")
    
    # RAM Check
    ram = psutil.virtual_memory()
    gb_used = ram.used / (1024**3)
    gb_total = ram.total / (1024**3)
    print(f"💾 RAM: {ram.percent}% Used ({gb_used:.1f}GB / {gb_total:.1f}GB)")
    
    # Disk Check (Root Partition)
    disk = psutil.disk_usage('/')
    gb_free = disk.free / (1024**3)
    print(f"💽 SSD: {disk.percent}% Full ({gb_free:.1f}GB Free)")
    
    print("=" * 40)
    
    # Logic Test
    if ram.percent > 90:
        print("⚠️  WARNING: High Memory Usage!")
    else:
        print("✅ System Status: NOMINAL")

if __name__ == "__main__":
    check_system()