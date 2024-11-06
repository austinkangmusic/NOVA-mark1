import pyaudio
import wave
import numpy as np
import torch
import time
from silero_vad import load_silero_vad
from scipy.signal import resample

# Constants
SAMPLING_RATE = 16000
RECORDING_RATE = 44100
CHUNK_SIZE = 1024
VAD_CHUNK_SIZE = 512  # Size of each chunk processed by VAD
MIN_VAD_CHUNK_SIZE = 1600  # Minimum chunk size (in samples) for VAD to process (depends on model)
SILENCE_DURATION = 0.5
MAX_NO_VOICE_DURATION = 10
# Load VAD model
USE_ONNX = False  # Change to True if you want to test onnx model
torch.set_num_threads(1)

if USE_ONNX:
    import onnxruntime as ort
    model = ort.InferenceSession('path_to_your_model.onnx')
else:
    model = load_silero_vad(onnx=USE_ONNX)

# Function to process audio chunks with VAD
def process_chunk(chunk):
    tensor_chunk = torch.from_numpy(chunk).float()
    speech_prob = model(tensor_chunk, SAMPLING_RATE).item()
    return speech_prob

def record_audio(filename='audios/input.wav', channels=1, rate=RECORDING_RATE, chunk=CHUNK_SIZE, silence_duration=SILENCE_DURATION, max_no_voice_duration=MAX_NO_VOICE_DURATION):
    """
    Records audio in real-time and saves it to a WAV file, maintaining a maximum of specified duration,
    while processing VAD in a separate chunk size.
    """
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    file_name = "statuses/voice_detected.txt"
    with open(file_name, 'w') as file:
        file.write('False')
    voice_detected = False

    # Open the stream for recording
    stream = audio.open(format=pyaudio.paInt16, channels=channels,
                        rate=rate, input=True,
                        frames_per_buffer=chunk)
    
    silence_threshold = rate / chunk * silence_duration
    start_time = time.time()

    # Open the wave file once for writing
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)

        # Initialize an empty list to hold audio frames
        vad_buffer = np.array([], dtype=np.int16)  # Buffer for VAD processing

        print("Monitoring Voice...")
        try:
            while True:
                data = stream.read(chunk)
                audio_data = np.frombuffer(data, dtype=np.int16)  # Convert to numpy array
                wf.writeframes(data)  # Write the current audio data directly to the file

                # Accumulate audio data for VAD processing
                vad_buffer = np.concatenate((vad_buffer, audio_data))

                # Check if we have enough data for VAD processing
                if len(vad_buffer) >= MIN_VAD_CHUNK_SIZE:
                    # Downsample to 16 kHz
                    downsampled_length = int(len(vad_buffer) * (SAMPLING_RATE / RECORDING_RATE))
                    vad_chunk = resample(vad_buffer, downsampled_length)

                    # Ensure vad_chunk is a multiple of 512
                    num_samples = len(vad_chunk)
                    if num_samples >= VAD_CHUNK_SIZE:
                        vad_chunk = vad_chunk[:(num_samples // VAD_CHUNK_SIZE) * VAD_CHUNK_SIZE]

                        # Normalize to float32
                        vad_chunk_float = vad_chunk.astype(np.float32) / np.iinfo(np.int16).max
                        speech_prob = process_chunk(vad_chunk_float)
                        if speech_prob > 0.5:
                            print(f"Speech Probability: {speech_prob:.2f}")
                            silence_counter = 0
                            start_time = time.time()  # Reset timer

                            voice_detected = True 
                            # Open the file in write mode and write the message
                            with open("statuses/voice_detected.txt", 'w') as file:
                                file.write('True')

                            with open("statuses/pause_detected.txt", "w") as file:
                                file.write('false')  
                        else:
                            if voice_detected:
                                silence_counter += 1
                            if voice_detected and silence_counter >= silence_threshold:
                                print("Silence detected after voice.")

                                voice_detected = False
                                # Open the file in write mode and write the message
                                with open("statuses/voice_detected.txt", 'w') as file:
                                    file.write('False')

                                with open("statuses/pause_detected.txt", "w") as file:
                                    file.write('true')    

                    # Clear the VAD buffer after processing
                    vad_buffer = vad_buffer[len(audio_data):]  # Keep only unprocessed data
                elapsed_time = time.time() - start_time
                if elapsed_time >= max_no_voice_duration and not voice_detected:
                    print(f'No voice detected for the last {max_no_voice_duration} seconds. Restarting.')
                    silence_counter = 0
                    voice_detected = False  # Reset voice detected flag    
                    with open("audios/input.wav", "wb") as file:
                        file.write(b'')
                    with open("statuses/restarted.txt", "w") as file:
                        file.write('true')

                        # Initialize PyAudio
                    audio = pyaudio.PyAudio()

                    stream = audio.open(format=pyaudio.paInt16, channels=channels,
                                        rate=rate, input=True,
                                        frames_per_buffer=chunk)
                    

                    # Open the WAV file for writing
                    try:
                        wf = wave.open(filename, 'wb')
                    except Exception as e:
                        print(f"Failed to open file: {e}")

                    wf.setnchannels(channels)
                    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(rate)

                    start_time = time.time()  # Reset timer
                with open('transcription/input.txt', 'r') as file:
                    user_input = file.read()
                with open('statuses/speak_status.txt', 'r') as file:
                    speak_status = file.read()
                with open('statuses/chatbot_replied.txt', 'r') as file:
                    chatbot_replied = file.read()
                if speak_status == 'false' and chatbot_replied == 'true' and '[Not Speaking]' in user_input:

                    with open("transcription/input.txt", "w") as file:
                        file.write('')  


                    with open("audios/input.wav", "wb") as file:
                        file.write(b'')

                        # Initialize PyAudio
                    audio = pyaudio.PyAudio()

                    stream = audio.open(format=pyaudio.paInt16, channels=channels,
                                        rate=rate, input=True,
                                        frames_per_buffer=chunk)
                    

                    # Open the WAV file for writing
                    try:
                        wf = wave.open(filename, 'wb')
                    except Exception as e:
                        print(f"Failed to open file: {e}")

                    wf.setnchannels(channels)
                    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(rate)

        except KeyboardInterrupt:
            print("Recording stopped.")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        print(f"Audio recorded and saved as {filename}")

# record_audio()
# print('record_live.py')

