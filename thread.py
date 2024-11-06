import pyaudio
import os
import wave
import numpy as np
from pprint import pprint

import torch
from initialize_whisper import initialize_whisper_model
from silero_vad import (load_silero_vad, read_audio, get_speech_timestamps, save_audio, VADIterator, collect_chunks)
from record_live import record_audio
# from chatbot import run
import threading
import queue

# Initialize Whisper model

whisper_model = initialize_whisper_model()


# Load VAD model
print("Loading VAD model...")
model = load_silero_vad(onnx=False)
sampling_rate = 16000
chunk_size = 512
voice_detected = False
speech_threshold = 0.2
print("VAD model loaded.")


from datetime import datetime
import time
import pytz

# Set timezone to Singapore Time (SGT)
sgt_tz = pytz.timezone('Asia/Singapore')

# Function to get formatted current time in Singapore Time (SGT)
def get_sgt_time():
    # Set timezone to Singapore Time (SGT)
    sgt_tz = pytz.timezone('Asia/Singapore')
    # Get current time in SGT
    current_time = datetime.now(sgt_tz)
    # Format time in HH:MM:SS and extended microseconds
    formatted_time = current_time.strftime('%H:%M:%S.') + f'{current_time.microsecond}'
    return formatted_time

#user_start_time = get_sgt_time()
#user_end_time = get_sgt_time()
#ai_start_time = get_sgt_time()
#ai_end_time = get_sgt_time()






# Function to transcribe audio using Whisper model
def transcribe_with_whisper(audio_file, whisper_model):
    # print(f"Transcribing audio file: {audio_file}")
    try:
        segments, info = whisper_model.transcribe(audio_file, beam_size=5)
        transcription = ""
        for segment in segments:
            transcription += segment.text + " "
        # print("Transcription completed.")
        return transcription.strip()
    except Exception as e:
        # print(f"Exception during transcription: {e}")
        return ""
import sys
# Threaded function to process the audio and transcribe it
def process_and_transcribe(audio_file, whisper_model):
    while True:
            # Define the file name
        file_name = "statuses/voice_detected.txt"

        # Read the content of the file and store it in the voice_detected variable
        try:
            with open(file_name, 'r') as file:
                voice_detected = file.read()
            
        except FileNotFoundError:
            voice_detected = ""

        # You can now use the voice_detected variable in your program

        if voice_detected.lower() == 'true':                
            user_start_time = get_sgt_time()

            while True:
                # Read the content of the file and store it in the voice_detected variable
                try:
                    with open(file_name, 'r') as file:
                        voice_detected = file.read()
                    
                except FileNotFoundError:
                    voice_detected = ""
                # Read the content of the file and store it in the voice_detected variable
                try:
                    with open('statuses/pause_detected.txt', 'r') as file:
                        pause_detected = file.read()
                    
                except FileNotFoundError:
                    pause_detected = ""


                # print('process_full_audio completed...')
                user_latest_word_time = get_sgt_time()

                # Transcribe the recorded audio
                user_input = transcribe_with_whisper(audio_file, whisper_model)
                if voice_detected.lower() == 'true' and pause_detected.lower() == 'false':
                    if user_input:
                        user_input = f'(start time: {user_start_time}) {user_input}... [Speaking] (latest word time: {user_latest_word_time})'
                        with open("statuses/chatbot_replied.txt", "w") as file:
                            file.write('false')
                        # Save transcription to a file
                        with open("statuses/seconds.txt", "w") as file:
                            file.write(user_latest_word_time)
                        try:
                            with open("transcription/input.txt", "w") as file:
                                file.write(user_input)
                                # print("Transcription saved to 'transcription/input.txt'.")
                        except Exception as e:
                            pass

                if voice_detected.lower() == 'false':
                    if user_input:
                        user_input = transcribe_with_whisper(audio_file, whisper_model)

                        user_input = f'(start time: {user_start_time}) {user_input} [Not Speaking] (latest word time: {user_latest_word_time})'
                        # Save transcription to a file
                        with open("statuses/seconds.txt", "w") as file:
                            file.write(user_latest_word_time)
                        with open("transcription/input.txt", "w") as file:
                            file.write(user_input)
                    break
                

# Queue for audio files
audio_queue = queue.Queue()

def audio_worker():
    while True:
        audio_file = audio_queue.get()
        if audio_file is None:  # Exit condition
            # print("Audio worker exiting...")
            break
        # print(f"Processing audio file from queue: {audio_file}")
        process_and_transcribe(audio_file, whisper_model)
        audio_queue.task_done()

def execute():
    # Specify the path to the file
    file_path = 'audios/input.wav'
    
    # Check if the file exists before attempting to delete it
    if os.path.exists(file_path):
        os.remove(file_path)  # Delete the file
        # print(f"{file_path} has been deleted.")
    else:
        pass
    
    with open("transcription/input.txt", "w") as file:
        file.write('')

    # Start worker thread
    worker_thread = threading.Thread(target=audio_worker)
    worker_thread.start()
    # print("Worker thread started.")

    # llm_thread = threading.Thread(target=run)
    # llm_thread.start()

    # Add audio file to the queue
    audio_file = "audios/input.wav"
    audio_queue.put(audio_file)
    # print(f"Audio file added to the queue: {audio_file}")

    try:
        # Start processing
        record_audio()

        # Optionally, wait for all processing to complete
        audio_queue.join()
        # print("All tasks in the audio queue have been processed.")

    except KeyboardInterrupt:
        pass
        # print("KeyboardInterrupt received. Stopping processing...")

    finally:
        # Stop the worker thread
        audio_queue.put(None)
        worker_thread.join()
        # llm_thread.join()
        # print("Worker thread has been stopped.")

# execute()


