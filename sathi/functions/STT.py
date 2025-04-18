import speech_recognition as sr
import os
import time
import uuid
import threading
import audioop
from queue import Queue

# Configuration
INPUT_AUDIO_DIR = r"C:\Users\Lenovo\OneDrive\Desktop\PadhaiMitra\Padhai_Sathi\Padhai-Sathi\Files\Students\Inputs"
OUTPUT_DIR = r"C:\Users\Lenovo\OneDrive\Desktop\PadhaiMitra\Padhai_Sathi\Padhai-Sathi\Files\Students\Notes"
DEFAULT_RECORD_DURATION = 30  # Fallback duration if needed (seconds)
SAMPLE_RATE = 16000  # Sample rate for audio capture
SAMPLE_WIDTH = 2  # 16-bit audio

# Create output directory if it doesn't exist
# os.makedirs(OUTPUT_DIR, exist_ok=True)


from pydub import AudioSegment
from tempfile import NamedTemporaryFile

def convert_to_wav(input_file):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1).set_frame_rate(16000)  # Mono, 16kHz
    temp_wav = NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(temp_wav.name, format="wav")
    return temp_wav.name

def validate_file_path(filename, default_dir=INPUT_AUDIO_DIR):
    """Validate and normalize file path."""
    try:
        if os.path.isabs(filename):
            file_path = os.path.normpath(filename)
        else:
            file_path = os.path.normpath(os.path.join(default_dir, filename))
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            return None
        return file_path
    except Exception as e:
        print(f"Error validating path: {e}")
        return None

def transcribe_audio_file(filepath):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filepath) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="en-US")
            print(f"Transcribed: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise Exception(f"API Error: {e}")

def transcribe_microphone():
    """Capture and transcribe real-time audio from microphone, controlled by space bar."""
    recognizer = sr.Recognizer()
    audio_queue = Queue()
    recording = False
    stop_event = threading.Event()
    
    def capture_audio():
        """Capture audio in a separate thread and store in queue."""
        try:
            with sr.Microphone(sample_rate=SAMPLE_RATE) as source:
                print(f"Adjusting for ambient noise... Please wait.")
                recognizer.adjust_for_ambient_noise(source, duration=2)
                
                while not stop_event.is_set():
                    try:
                        # Capture audio chunk (1-second buffer)
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=1)
                        if recording:
                            audio_queue.put(audio.get_raw_data(convert_rate=SAMPLE_RATE, convert_width=SAMPLE_WIDTH))
                    except sr.WaitTimeoutError:
                        continue  # No audio detected in this chunk
                    except Exception as e:
                        print(f"Error capturing audio chunk: {e}")
                        break
        except Exception as e:
            print(f"Error in audio capture thread: {e}")
    
    try:
        print("Press space bar to start recording...")
        # Start audio capture thread
        audio_thread = threading.Thread(target=capture_audio)
        audio_thread.daemon = True
        audio_thread.start()
        

        # # Wait for first space bar press to start

        # keyboard.wait('space')
        # print("Recording started. Press space bar again to stop.")
        # recording = True
        

        # # Wait for second space bar press to stop

        # keyboard.wait('space')
        # recording = False
        # stop_event.set()
        # print("Recording stopped.")
        
        # Collect all audio data from queue
        audio_data = b""
        while not audio_queue.empty():
            audio_data += audio_queue.get()
        
        if not audio_data:
            print("Error: No audio data captured.")
            return "", "unknown"
        
        # Convert raw audio to WAV format
        # wav_file = os.path.join(OUTPUT_DIR, f"mic_recording_{uuid.uuid4().hex}.wav")
        # with open(wav_file, "wb") as f:
        #     # Create WAV header
        #     wav = sr.AudioData(audio_data, SAMPLE_RATE, SAMPLE_WIDTH)
        #     f.write(wav.get_wav_data())
        # print(f"Saved microphone audio to {wav_file}")
        
        # Transcribe the WAV file
        text, language = transcribe_audio_file(wav_file)
        return text, language
    
    except KeyboardInterrupt:
        print("Recording interrupted.")
        stop_event.set()
        return "", "unknown"
    except Exception as e:
        print(f"Error in microphone transcription: {e}")
        stop_event.set()
        return "", "unknown"
    finally:
        stop_event.set()
        # Note: WAV file is retained as per original requirement

# def save_transcription(text, language, output_file):
#     """Save transcribed text to a file with timestamp and language."""
#     timestamp = time.strftime("%Y%m%d_%H%M%S")
#     try:
#         with open(output_file, "a", encoding="utf-8") as f:
#             f.write(f"{text}\n\n")
#         print(f"Transcription saved to {output_file}")
#     except Exception as e:
#         print(f"Error saving transcription: {e}")

