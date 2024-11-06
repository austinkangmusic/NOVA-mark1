from generate_pyttsx3_voice import generate_pyttsx3_voice

# Specify the input text file and output audio file
input_text_file = "transcription/output.txt"
output_audio_file = "audios/output.wav"

# Generate speech from text and save the audio file
generate_pyttsx3_voice(input_text_file, output_audio_file)


