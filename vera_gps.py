import serial
import threading
import pynmea2
import reverse_geocoder as rg
import time

class GPSHandler:
    def __init__(self, port='/dev/ttyACM0'):
        self.port = port
        self.current_data = {
            'lat': 30.7900,         # Default: Kingsland
            'lon': -81.6800,        # Default: Kingsland
            'speed': 0,
            'location_name': "Kingsland, Georgia (SIMULATION)",
            'status': "LOCKED (SIM)" # Start in SIM mode by default
        }
        self.running = True
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.daemon = True 
        
    def start(self):
        self.thread.start()
        
    def stop(self):
        self.running = False

    def _update_loop(self):
        while self.running:
            try:
                # Try to connect to hardware
                with serial.Serial(self.port, 9600, timeout=1) as ser:
                    print(f"🛰️  GPS Hardware Connected on {self.port}")
                    while self.running:
                        try:
                            line = ser.readline().decode('utf-8', errors='replace').strip()
                            
                            # Valid Data Check
                            if line.startswith('$GPRMC'): 
                                msg = pynmea2.parse(line)
                                if msg.status == "A": # A = Active (Real Lock)
                                    self._update_location(msg.latitude, msg.longitude, msg.spd_over_grnd_kmph, "LOCKED")
                                else:
                                    # Connected, but NO SATELLITES? -> Keep SIM coordinates
                                    self.current_data['status'] = "LOCKED (SIM - NO SAT)"
                        except Exception:
                            continue 
                            
            except Exception as e:
                # Hardware disconnected or crashed? -> Stay in SIM mode
                # We wait 5 seconds before trying to reconnect so we don't spam logs
                print(f"⚠️  GPS Hardware Error: {e}. Using Simulation.")
                self.current_data['status'] = "LOCKED (SIM - HARDWARE FAIL)"
                time.sleep(5)

    def _update_location(self, lat, lon, speed, status):
        # Reverse Geocode
        try:
            coordinates = (lat, lon)
            results = rg.search(coordinates) 
            city = results[0]['name']
            state = results[0]['admin1']
            location_name = f"{city}, {state}"
        except:
            location_name = "Unknown Territory"
        
        self.current_data['lat'] = lat
        self.current_data['lon'] = lon
        self.current_data['location_name'] = location_name
        self.current_data['speed'] = speed
        self.current_data['status'] = status

    def get_stats(self):
        return self.current_data