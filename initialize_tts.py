import os
import glob
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from cuda_device import get_device  # Import the get_device function

with open("statuses/speaker_name.txt", "r") as file:
    speaker_name = file.read()

# Singleton-like behavior
_initialized = False
xtts_model = None
_gpt_cond_latent = None
_speaker_embedding = None

def initialize_tts_model(speaker_name):
    global _initialized, xtts_model, _gpt_cond_latent, _speaker_embedding
    if not _initialized:
        device = get_device()

        print(f"Loading '{speaker_name}' model...")
        config = XttsConfig()
        config.load_json(f"XTTS-v2_models\XTTS-v2_{speaker_name}\config.json")
        xtts_model = Xtts.init_from_config(config)
        xtts_model.load_checkpoint(config, checkpoint_dir=f"XTTS-v2_models\XTTS-v2_{speaker_name}", use_deepspeed=False)
        xtts_model.device

        print("Computing speaker latents...")
        
        # Collect all .wav files from the specified directory
        audio_files = glob.glob(rf"XTTS-v2_models\XTTS-v2_{speaker_name}\voice_{speaker_name}\*.wav")
        
        # Compute conditioning latents for all collected audio files
        _gpt_cond_latent, _speaker_embedding = xtts_model.get_conditioning_latents(audio_path=audio_files)

        _initialized = True
    
    return xtts_model, _gpt_cond_latent, _speaker_embedding


