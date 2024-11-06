import wave
import numpy as np
from scipy.io import wavfile

def apply_c3po_effect(input_file, output_file, delay_ms=25, delay_volume=0.6):
    """
    Applies a C3PO voice effect by creating a delayed copy of the original audio and blending them.
    
    Args:
    input_file (str): Path to the input .wav audio file.
    output_file (str): Path where the output .wav audio file will be saved.
    delay_ms (int, optional): The delay in milliseconds for the delayed signal (default is 10 ms).
    delay_volume (float, optional): Volume multiplier for the delayed signal (default is 0.6).
    """
    
    # Open the wave file
    with wave.open(input_file, 'rb') as wav_in:
        params = wav_in.getparams()
        num_channels = params.nchannels
        sample_width = params.sampwidth
        sample_rate = params.framerate
        num_frames = params.nframes
        audio_data = wav_in.readframes(num_frames)

    # Convert the byte data to numpy array
    audio_signal = np.frombuffer(audio_data, dtype=np.int16)

    # Calculate the number of samples for the delay
    delay_samples = int(sample_rate * (delay_ms / 1000))

    # Create a delayed version of the audio signal with volume reduction
    delayed_signal = np.zeros(len(audio_signal) + delay_samples, dtype=np.float32)
    delayed_signal[delay_samples:] = audio_signal * delay_volume  # Reduce delayed signal volume

    # Pad original signal to match length of delayed signal
    padded_original_signal = np.zeros(len(delayed_signal), dtype=np.float32)
    padded_original_signal[:len(audio_signal)] = audio_signal

    # Combine the original and delayed signals
    combined_signal = padded_original_signal + delayed_signal

    # Prevent clipping by normalizing the combined signal
    max_val = np.max(np.abs(combined_signal))
    if max_val > 32767:  # Clip protection for 16-bit PCM
        combined_signal = combined_signal * (32767 / max_val)

    # Convert back to int16 for saving
    combined_signal = combined_signal.astype(np.int16)

    # Save the modified signal as a new wave file
    wavfile.write(output_file, sample_rate, combined_signal)

# # Example usage:
# input_file = r"D:\Private Server\Projects\ultron\Emma-0.4v\audios\output.wav"
# output_file = r"D:\Private Server\Projects\ultron\Emma-0.4v\audios\output_c3po_effect.wav"

# apply_c3po_effect(input_file, output_file)
