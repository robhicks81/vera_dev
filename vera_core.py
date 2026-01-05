import ollama
import os
import sys
import datetime
from vera_db import log_interaction  # <--- This now correctly pulls from the other file

# --- CONFIGURATION ---
VOICE_NAME = "en_GB-jenny_dioco-medium"

def generate_voice(text, output_file="vera_response.wav"):
    parts = VOICE_NAME.split('-')
    model_filename = f"{VOICE_NAME}.onnx"
    # Silence the output
    cmd = f'echo "{text}" | piper --model {model_filename} --output_file {output_file} > /dev/null 2>&1'
    os.system(cmd)

def get_telemetry():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""
    [SYSTEM TELEMETRY]
    CURRENT TIME: {now}
    GPS STATUS: OFFLINE
    USER: Rob
    """

def chat_loop():
    print("🔹 V.E.R.A. CORE ONLINE (DB LOGGING ACTIVE) 🔹")
    print("---------------------------------------------------")
    
    system_prompt = """
    You are V.E.R.A. (Virtual Electronic Road Assistant).
    You manage a tactical camper van.
    RULES:
    1. Be concise (under 2 sentences).
    2. Use [SYSTEM TELEMETRY] for time/status.
    3. Tone: Helpful, British, slightly militaristic.
    """
    
    messages = [{'role': 'system', 'content': system_prompt}]

    while True:
        try:
            # 1. INPUT
            user_input = input("\n👤 YOU: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
            
            # LOG INPUT
            log_interaction("Rob", user_input)
            
            # Context
            telemetry = get_telemetry()
            full_prompt = f"{telemetry}\nUSER COMMAND: {user_input}"
            messages.append({'role': 'user', 'content': full_prompt})

            # 2. THINK
            print("🧠 Thinking...", end="", flush=True)
            response = ollama.chat(model='llama3.2', messages=messages)
            ai_text = response['message']['content']
            print(f"\r🤖 VERA: {ai_text}") 
            
            # LOG OUTPUT
            log_interaction("VERA", ai_text)
            
            # 3. SPEAK
            print(f"🗣️  (Synthesizing...)")
            generate_voice(ai_text)
            messages.append({'role': 'assistant', 'content': ai_text})

        except KeyboardInterrupt:
            print("\n🛑 Force Quit.")
            break

if __name__ == "__main__":
    chat_loop()