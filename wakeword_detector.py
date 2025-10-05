import pvporcupine
import pyaudio
import struct
import os

# --- CONFIGURATION ---
PICOVOICE_ACCESS_KEY = "183fLGAfh9eEQuMMic086r7ard40c1xICVLCYJs7v3hnqpl1mXOZmw==" 
KEYWORD_FILE_PATH = "Hey-Mitra_en_windows_v3_0_0.ppn" 

def listen_for_wake_word():
    """
    Initializes Porcupine and listens for the custom wake word.
    This function will run forever until you stop it (Ctrl+C).
    """
    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=[KEYWORD_FILE_PATH]
        )
    except pvporcupine.PorcupineInvalidArgumentError as e:
        print(f"Error initializing Porcupine: {e}")
        print("Please make sure your Access Key and Keyword File Path are correct.")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for 'Hey Mitra'...")
    print("---------------------------------")
    print("Press Ctrl+C to stop listening.")

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm)
            if result >= 0:
                print("Wake word 'Hey Mitra' detected!")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()

if __name__ == '__main__':
    listen_for_wake_word()