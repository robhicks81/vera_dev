from flask import Flask, render_template, request, jsonify
import ollama
import datetime
import os
import time
import psutil
from vera_db import log_interaction
from vera_gps import GPSHandler # Import the new GPS module

app = Flask(__name__)

# --- HARDWARE INIT ---
print("🛰️  Initializing GPS System...")
gps = GPSHandler('/dev/ttyACM0')
gps.start()

# --- CONFIGURATION ---
SYSTEM_PROMPT = """
You are V.E.R.A. (Virtual Electronic Road Assistant).
You manage a tactical camper van.
RULES:
1. Be concise (under 2 sentences).
2. Tone: Helpful, British, slightly militaristic.
3. USE THE TELEMETRY.
   - If GPS is LOCKED, report the [LOCATION] provided (e.g., "We are currently near Kingsland, Georgia").
   - Do NOT give raw coordinates unless asked.
   - If GPS is OFFLINE, say "Unable to determine sector."
"""
chat_history = [{'role': 'system', 'content': SYSTEM_PROMPT}]

def get_telemetry():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = gps.get_stats()
    
    # FIX: Check if the string STARTS with LOCKED (handling SIM mode)
    if data['status'].startswith("LOCKED"):
        # We pass the City Name to the AI
        loc_str = f"{data['status']} | LOCATION: {data['location_name']} | COORDS: {data['lat']:.4f}, {data['lon']:.4f}"
    else:
        loc_str = "OFFLINE"

    return f"TIME: {now} | GPS: {loc_str} | USER: Rob"

def generate_voice_web(text):
    timestamp = int(time.time())
    filename = f"vera_{timestamp}.wav"
    filepath = os.path.join("static", filename)
    
    parts = "en_GB-jenny_dioco-medium".split('-')
    model = f"en_GB-jenny_dioco-medium.onnx"
    
    cmd = f'echo "{text}" | piper --model {model} --output_file {filepath} > /dev/null 2>&1'
    os.system(cmd)
    
    return filename

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    log_interaction("Rob", user_input)
    
    telemetry = get_telemetry()
    # Feed telemetry into the prompt so she sees it immediately
    full_prompt = f"[{telemetry}] COMMAND: {user_input}"
    
    chat_history.append({'role': 'user', 'content': full_prompt})
    
    print("🧠 Thinking...")
    response = ollama.chat(model='llama3.2', messages=chat_history)
    ai_text = response['message']['content']
    
    log_interaction("VERA", ai_text)
    chat_history.append({'role': 'assistant', 'content': ai_text})
    
    audio_file = generate_voice_web(ai_text)
    
    return jsonify({'response': ai_text, 'audio_url': audio_file})

@app.route('/telemetry')
def telemetry_endpoint():
    # 1. GPS DATA
    gps_data = gps.get_stats()
    status_text = gps_data['status']
    is_locked = status_text.startswith("LOCKED")
    
    # 2. SERVER VITALS (The Upgrade)
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    temp = "N/A" 
    
    # Try to get temperature (Linux specific, might fail on some VMs/Windows)
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            temp = f"{temps['coretemp'][0].current}°C"
        elif 'cpu_thermal' in temps: # Raspberry Pi specific name
            temp = f"{temps['cpu_thermal'][0].current}°C"
    except:
        pass

    engine_status = f"CPU: {cpu}% | RAM: {ram}% | TEMP: {temp}"

    return jsonify({
        'status': status_text,
        'color': '#00ff00' if is_locked else 'red',
        'location': gps_data.get('location_name', 'Unknown'),
        'engine': engine_status # New Data Field
    })

@app.route('/system/shutdown', methods=['POST'])
def system_shutdown():
    log_interaction("System", "Manual Shutdown Initiated via Dashboard.")
    # Execute Linux shutdown command
    # 'sudo' is required, but we configured NOPASSWD so it won't block
    os.system("sudo shutdown now")
    return jsonify({'status': 'Shutting down...'})

@app.route('/system/reboot', methods=['POST'])
def system_reboot():
    log_interaction("System", "Manual Reboot Initiated via Dashboard.")
    os.system("sudo reboot")
    return jsonify({'status': 'Rebooting...'})

if __name__ == '__main__':
    print("🔹 V.E.R.A. WEB INTERFACE ONLINE 🔹")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        gps.stop() # Clean shutdown