from faster_whisper import WhisperModel
import os
import time

# Configuration
MODEL_SIZE = "tiny.en"  # Smallest, fastest model. Accurate enough for commands.
# Options: tiny.en, base.en, small.en, medium.en (Larger = Slower but smarter)

def test_hearing(audio_file="vera_output.wav"):
    print(f"👂 Loading Ear Model ({MODEL_SIZE}) on CPU...")
    start_load = time.time()
    
    # We force CPU usage to avoid fighting the RX 580 drivers for this specific library
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    
    print(f"✅ Model Loaded in {time.time() - start_load:.2f}s")
    print(f"🎧 Listening to file: {audio_file}...")

    # Transcribe
    segments, info = model.transcribe(audio_file, beam_size=5)

    print("-" * 30)
    print(f"Detected Language: {info.language} (Probability: {info.language_probability:.2f})")
    print("-" * 30)

    # Print the text
    for segment in segments:
        print(f"📝 TRANSCRIPT: {segment.text}")
        
    print("-" * 30)
    print("✅ Hearing Test Complete.")

if __name__ == "__main__":
    if not os.path.exists("vera_output.wav"):
        print("❌ Error: 'vera_output.wav' not found. Run vera_speak.py first!")
    else:
        test_hearing()