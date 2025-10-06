import pvporcupine
import pyaudio
import struct
import os
from transformers import pipeline
import sounddevice as sd
from scipy.io.wavfile import write

# --- WAKE WORD CONFIGURATION ---
PICOVOICE_ACCESS_KEY = "183fLGAfh9eEQuMMic086r7ard40c1xICVLCYJs7v3hnqpl1mXOZmw==" 
KEYWORD_FILE_PATH = "Hey-Mitra_en_windows_v3_0_0.ppn" 

# --- SPEECH-TO-TEXT CONFIGURATION ---
MODEL_NAME = "openai/whisper-tiny.en"
RECORDING_PATH = "command.wav"
SAMPLE_RATE = 16000
DURATION = 4

# --- 1. INITIALIZE MODELS (Happens only once at the start) ---

# Initialize Speech-to-Text Model
try:
    print("Loading speech-to-text model...")
    stt_pipeline = pipeline("automatic-speech-recognition", model=MODEL_NAME)
    print("Speech-to-text model loaded successfully.")
except Exception as e:
    print(f"Error loading STT model: {e}")
    stt_pipeline = None

# Initialize Wake Word Model
try:
    print("Initializing wake word detector...")
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_ACCESS_KEY,
        keyword_paths=[KEYWORD_FILE_PATH]
    )
    print("Wake word detector initialized successfully.")
except Exception as e:
    print(f"Error initializing Porcupine: {e}")
    porcupine = None

# --- 2. DEFINE FUNCTIONS ---

def transcribe_command():
    """Records audio and transcribes it into text."""
    if stt_pipeline is None:
        print("STT pipeline not available.")
        return None

    print(f"\nListening for command...")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    write(RECORDING_PATH, SAMPLE_RATE, recording)
    print("Recording complete.")

    print("Transcribing audio...")
    transcribed_text = None
    try:
        result = stt_pipeline(RECORDING_PATH)
        transcribed_text = result["text"].strip()
    except Exception as e:
        print(f"Error during transcription: {e}")
    finally:
        if os.path.exists(RECORDING_PATH):
            os.remove(RECORDING_PATH)
        
    return transcribed_text

def run_voice_assistant():
    """Listens for the wake word and then transcribes the following command."""
    if porcupine is None:
        print("Could not start. Wake word detector failed to initialize.")
        return

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("\n---------------------------------")
    print("Listening for 'Hey Mitra'...")
    print("Press Ctrl+C to stop the assistant.")
    print("---------------------------------")

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected!")
                
                # --- THIS IS THE INTEGRATION ---
                command = transcribe_command()
                if command:
                    print(f"\nCommand received: '{command}'")
                    # Later, we will send this command to the "brain"
                else:
                    print("\nCould not understand the command.")
                
                print("\n---------------------------------")
                print("Listening for 'Hey Mitra'...") # Go back to listening
                print("---------------------------------")


    except KeyboardInterrupt:
        print("Stopping assistant...")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()

# --- 3. RUN THE ASSISTANT ---
if __name__ == '__main__':
    run_voice_assistant()