import os
import torch
import codecs
import torchaudio
from initialize_tts import initialize_tts_model, speaker_name
xtts_model, gpt_cond_latent, speaker_embedding = initialize_tts_model(speaker_name)

def generate_voice_audio(text, output_path):
    
    # Perform inference to get audio output
    out = xtts_model.inference(
        text,
        "en",
        gpt_cond_latent,
        speaker_embedding,
        temperature=0.7  # Add custom parameters here
    )
    
    # Extract waveform and sample rate from the output
    waveform = torch.tensor(out["wav"]).unsqueeze(0)
    sample_rate = 24000  # Ensure this matches the sample rate used in inference

    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the audio file in PCM format
    torchaudio.save(output_path, waveform, sample_rate, encoding="PCM_S", bits_per_sample=16)
    # print(f"Saved synthesized speech to {output_path}")

def run():
    # Read the AI response from the file
    with codecs.open("transcription/output.txt", "r", encoding="utf-8", errors="surrogateescape") as file:
        ai_response = file.read()

    # Path to save the output audio
    output_path = "audios/output.wav"
    
    # Generate voice audio
    generate_voice_audio(ai_response, output_path)
