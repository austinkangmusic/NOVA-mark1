# import numpy as np
# import librosa
# import soundfile as sf

# # robotic_voice.py
# if_robotic = False
# def apply_full_vocoder(input_file, output_file, carrier_file, frame_size=2048):
#     # Load input speech
#     speech, sr = librosa.load(input_file, sr=None)

#     # Load carrier signal
#     carrier, _ = librosa.load(carrier_file, sr=sr)

#     # Make sure the carrier is at least as long as the speech
#     if len(carrier) < len(speech):
#         carrier = np.tile(carrier, int(np.ceil(len(speech) / len(carrier))))[:len(speech)]
#     else:
#         carrier = carrier[:len(speech)]

#     # Process with a vocoder
#     speech_stft = librosa.stft(speech, n_fft=frame_size)
#     carrier_stft = librosa.stft(carrier, n_fft=frame_size)

#     # Use the magnitude of the speech and phase of the carrier
#     magnitude = np.abs(speech_stft)
#     phase = np.angle(carrier_stft)

#     # Combine magnitude and phase
#     vocoded_stft = magnitude * np.exp(1j * phase)

#     # Inverse STFT to get back to time domain
#     vocoded_audio = librosa.istft(vocoded_stft)

#     # Save the new sound
#     sf.write(output_file, vocoded_audio, sr)




# apply_vocoder("audios/output.wav", "audios/full_vocoder_output.wav", "audios/carrier.wav")









import numpy as np
import librosa
import soundfile as sf

# robotic_voice.py
if_robotic = True

def apply_vocoder(input_file, output_file, carrier_file, frame_size=2048, speech_volume=1.0, vocoder_volume=1.0):
    # Load input speech
    speech, sr = librosa.load(input_file, sr=None)

    # Load carrier signal
    carrier, _ = librosa.load(carrier_file, sr=sr)

    # Make sure the carrier is at least as long as the speech
    if len(carrier) < len(speech):
        carrier = np.tile(carrier, int(np.ceil(len(speech) / len(carrier))))[:len(speech)]
    else:
        carrier = carrier[:len(speech)]

    # Process with a vocoder
    speech_stft = librosa.stft(speech, n_fft=frame_size)
    carrier_stft = librosa.stft(carrier, n_fft=frame_size)

    # Use the magnitude of the speech and phase of the carrier
    magnitude = np.abs(speech_stft)
    phase = np.angle(carrier_stft)

    # Combine magnitude and phase
    vocoded_stft = magnitude * np.exp(1j * phase)

    # Inverse STFT to get back to time domain
    vocoded_audio = librosa.istft(vocoded_stft)

    # Apply volume scaling
    speech_scaled = speech_volume * speech
    vocoded_audio_scaled = vocoder_volume * vocoded_audio

    # Ensure both arrays are the same length by trimming or padding the shorter one
    min_length = min(len(speech_scaled), len(vocoded_audio_scaled))
    speech_scaled = speech_scaled[:min_length]
    vocoded_audio_scaled = vocoded_audio_scaled[:min_length]

    # Combine original and vocoded audio
    combined_audio = speech_scaled + vocoded_audio_scaled

    # Save the new sound
    sf.write(output_file, combined_audio, sr)

# Example usage with adjustable volumes
# apply_vocoder("audios/output_c3po_effect.wav", "audios/vocoder_output.wav", "audios/carrier.wav", speech_volume=1, vocoder_volume=1)