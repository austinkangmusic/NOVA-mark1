import codecs
from initialize_pyttsx3 import Pyttsx3Initializer

def generate_pyttsx3(input_text_file, output_audio_file):
    """
    Function to generate speech from text and save it to an audio file.

    Args:
    input_text_file (str): Path to the input text file.
    output_audio_file (str): Path to the output audio file (e.g., 'audios/output.wav').
    """
    try:
        # Read the content from the transcription file
        with codecs.open(input_text_file, "r", encoding="utf-8", errors="surrogateescape") as file:
            ai_response = file.read()

        # Get the TTS engine instance
        tts_initializer = Pyttsx3Initializer.get_instance()
        engine = tts_initializer.get_engine()

        # Save the speech to a file
        engine.save_to_file(ai_response, output_audio_file)

        # Run the speech engine
        engine.runAndWait()

        print(f"Audio saved to {output_audio_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

def running():
    # Specify the input text file and output audio file
    input_text_file = "transcription/output.txt"
    output_audio_file = "audios/output.wav"

    # Generate speech from text and save the audio file
    generate_pyttsx3(input_text_file, output_audio_file)
