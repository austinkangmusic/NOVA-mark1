import llms
import json
import re
import subprocess
import os
def initialize():
    global chat_llm, utility_llm, embedding_llm

    # main chat model used by agents (smarter, more accurate)
    # chat_llm = llms.get_arli_ai_chat(model_name="Meta-Llama-3.1-70B-Instruct", temperature=0)

    # chat_llm = llms.get_openai_chat(model_name="gpt-4o-mini", temperature=0)
##

    # https://colab.research.google.com/drive/131bKCMT-K1nD6AdMe7NF6-Yzxull1Q9G#scrollTo=V7MbuLui56vL
    # Set the environment variable
    os.environ["OLLAMA_HOST"] = "https://tidy-exotic-serval.ngrok-free.app"

    # Define the model name
    model_name = "llama3.1:8b"

    # Get the chat model
    chat_llm = llms.get_ollama_chat(model_name=model_name, temperature=0)

    # Ensure the model exists
    llms.ensure_model_exists(model_name=model_name)

    # # Command to run ollama serve
    # ollama_path = "D:\\Utilities\\LLMS\\Ollama\\ollama.exe"  # Path to the Ollama executable
    # command = f'"{ollama_path}" serve'  # Ensure the command is formatted correctly

    # try:
    #     subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    # except subprocess.CalledProcessError as e:
    #     print("Failed to run command:", e)
##

    # chat_llm = llms.get_lmstudio_chat(model_name="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", temperature=0)
    # chat_llm = llms.get_openrouter(model_name="meta-llama/llama-3.1-70b-instruct")
    # chat_llm = llms.get_azure_openai_chat(deployment_name="gpt-4o-mini", temperature=0)
    # chat_llm = llms.get_anthropic_chat(model_name="claude-3-5-sonnet-20240620", temperature=0)
    # chat_llm = llms.get_google_chat(model_name="gemini-1.5-flash", temperature=0)
    # chat_llm = llms.get_groq_chat(model_name="llama-3.1-70b-versatile", temperature=0)
    
    # utility model used for helper functions (cheaper, faster)
    utility_llm = chat_llm # change if you want to use a different utility model

    # embedding model used for memory
    # embedding_llm = llms.get_openai_embedding(model_name="text-embedding-3-small")
    # embedding_llm = llms.get_ollama_embedding(model_name="nomic-embed-text")
    embedding_llm = llms.get_huggingface_embedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    return chat_llm, utility_llm, embedding_llm

def use_chat_llm():
    return chat_llm

def use_utility_llm():
    return utility_llm

def use_embedding_llm():
    return embedding_llm


def remove_trailing_commas(json_string):
    # Remove trailing commas before closing brackets or braces
    json_string = re.sub(r',\s*(\]|\})', r'\1', json_string)
    return json_string

def extract_tool_info(response_json):
    # Remove the JSON formatting markers from the input string
    # Use regex to trim leading spaces and then remove the markers
    response_json = re.sub(r'^\s*```json', '', response_json).rstrip('```').strip()
    
    # Clean the JSON string by removing invalid elements
    cleaned_response = re.sub(r'\.\.\.|//.*', '', response_json).strip()
    
    # Remove trailing commas
    cleaned_response = remove_trailing_commas(cleaned_response)

    try:
        response = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON after cleanup: {e}")
        print("Cleaned response content:", cleaned_response)
        return None, None  # Return None if JSON parsing fails

    tool_name = response.get("tool_name", "")
    tool_args = response.get("tool_args", {})

    return tool_name, tool_args

def extract_response(response_text):
    # Try to find JSON within ```json ... ``` if delimiters are present
    json_match = re.search(r'```json\s*({.*?})\s*```', response_text, re.DOTALL)
    
    # If delimiters are found, use the matched JSON content; otherwise, use the full response
    json_string = json_match.group(1) if json_match else response_text.strip()

    try:
        # Parse the JSON string
        response = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("Extracted JSON content:", json_string)
        return None, None  # Return None if JSON parsing fails

    # Extract "thoughts" and "text" fields, returning as separate variables
    thoughts = response.get("thoughts", "")
    text = response.get("text", None)

    return thoughts, text

