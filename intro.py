import os
import torch
import torchaudio
import pyaudio
import wave
from initialize_tts import initialize_tts_model
import numpy as np
import librosa
import soundfile as sf

def generate_voice_audio(text, output_path):
    model, gpt_cond_latent, speaker_embedding = initialize_tts_model()
        
    # Perform inference to get audio output
    out = model.inference(
        text,
        "en",
        gpt_cond_latent,
        speaker_embedding,
        temperature=0.1  # Add custom parameters here
    )
    
    # Extract waveform and sample rate from the output
    waveform = torch.tensor(out["wav"]).unsqueeze(0)
    sample_rate = 24000  # Ensure this matches the sample rate used in inference

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the audio file in PCM format
    torchaudio.save(output_path, waveform, sample_rate, encoding="PCM_S", bits_per_sample=16)
    print(f"Saved synthesized speech to {output_path}")

import os
import wave
import numpy as np
import pyaudio
from scipy.signal import butter, lfilter

# Band-stop filter design to remove 442 Hz
def bandstop_filter(data, fs, lowcut, highcut, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='bandstop')
    y = lfilter(b, a, data)
    return y

# Function to apply filter and play audio
def play_audio(file_path):
    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return

    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()

    try:
        # Audio stream setup
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        # Filter design
        sample_rate = wf.getframerate()
        lowcut = 440  # Lower bound for filter
        highcut = 444  # Upper bound for filter

        # Read audio data in chunks and process
        data = wf.readframes(512)
        while data:
            # Convert bytes to numpy array for processing
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Apply the band-stop filter
            filtered_data = bandstop_filter(audio_data, sample_rate, lowcut, highcut)
            
            # Convert the filtered data back to bytes
            filtered_data = filtered_data.astype(np.int16).tobytes()

            # Play the filtered data
            stream.write(filtered_data)
            data = wf.readframes(512)
        
        stream.stop_stream()
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        stream.close()
        wf.close()
        p.terminate()

def initialize():

    from robotic_voice import if_robotic, apply_vocoder


    ai_response = "I'm ready."
    
    # Path to save the output audio
    output_path = "audios/output_0.wav"
    
    # Generate voice audio
    generate_voice_audio(ai_response, output_path)

    if if_robotic:
        apply_vocoder("audios/output_0.wav", "audios/output_0.wav", "audios/carrier.wav")
    
    # Play the generated audio
    play_audio(output_path)

def initialize_loop():
    while True:


        ai_response = input('Input a text: ')

        from robotic_voice import if_robotic, apply_vocoder
        
        # Path to save the output audio
        output_path = "audios/output_0.wav"
        
        # Generate voice audio
        generate_voice_audio(ai_response, output_path)
        # Example usage

        if if_robotic:
            apply_vocoder("audios/output_0.wav", "audios/output_0.wav", "audios/carrier.wav")

        # Play the generated audio
        play_audio(output_path)

# initialize()
initialize_loop()