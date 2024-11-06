import os
import subprocess
import ollama
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings, AzureChatOpenAI, AzureOpenAIEmbeddings, AzureOpenAI
from langchain_ollama import OllamaLLM
from langchain_community.embeddings import OllamaEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from pydantic.v1.types import SecretStr


# Load environment variables
load_dotenv()

# Configuration
DEFAULT_TEMPERATURE = 0.0

# Utility function to get API keys from environment variables
def get_api_key(service):
    return os.getenv(f"API_KEY_{service.upper()}") or os.getenv(f"{service.upper()}_API_KEY")


import os
import subprocess

def find_drive_path():
    # Look for either "Utilities" or "Private Server" on any drive
    for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        base_path = f"{drive_letter}:\\"
        utilities_path = os.path.join(base_path, "Utilities", "LLMS", "Ollama")
        private_server_path = os.path.join(base_path, "Private Server", "LLMS", "Ollama")
        
        if os.path.exists(utilities_path):
            return utilities_path
        elif os.path.exists(private_server_path):
            return private_server_path
    return None

# Get paths based on the existing location
ollama_base_path = find_drive_path()
if ollama_base_path:
    ollama_path = os.path.join(ollama_base_path, "ollama.exe")
    models_directory = os.path.join(ollama_base_path, "models")
else:
    raise FileNotFoundError("Neither 'Utilities' nor 'Private Server' directories found on any drive.")

def check_model_exists(model_name):
    # Run ollama list command to get the list of models
    command = f'"{ollama_path}" list'  # Quotes added to handle spaces in the path
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return model_name in result.stdout
    except subprocess.CalledProcessError as e:
        print("Failed to run command:", e)
        return False  # Return False if the command fails

def pull_model(model_name):
    # Pull the model if it does not exist
    print(f"Model '{model_name}' not found. Downloading model...")
    command = f'"{ollama_path}" pull {model_name}'  # Construct the pull command
    try:
        subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"Model '{model_name}' downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to pull model:", e)
        
def ensure_model_exists(model_name):
    model_path = os.path.join(models_directory, model_name)
    if not os.path.exists(model_path) and not check_model_exists(model_name):
        pull_model(model_name)


# Ollama models https://tidy-exotic-serval.ngrok-free.app
# http://localhost:11434
def get_ollama_chat(model_name: str, temperature=DEFAULT_TEMPERATURE, base_url="https://tidy-exotic-serval.ngrok-free.app"):
    ensure_model_exists(model_name)
    return OllamaLLM(model=model_name, temperature=temperature, base_url=base_url)

def get_ollama_embedding(model_name: str, temperature=DEFAULT_TEMPERATURE):
    ensure_model_exists(model_name)
    return OllamaEmbeddings(model=model_name, temperature=temperature)

    
# HuggingFace models
def get_huggingface_embedding(model_name:str):
    return HuggingFaceEmbeddings(model_name=model_name)

# LM Studio and other OpenAI compatible interfaces
def get_lmstudio_chat(model_name:str, base_url="http://localhost:1234/v1", temperature=DEFAULT_TEMPERATURE):
    return ChatOpenAI(model_name=model_name, base_url=base_url, temperature=temperature, api_key="none") # type: ignore

def get_lmstudio_embedding(model_name:str, base_url="http://localhost:1234/v1"):
    return OpenAIEmbeddings(model_name=model_name, base_url=base_url) # type: ignore

# Anthropic models
def get_anthropic_chat(model_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE):
    api_key = api_key or get_api_key("anthropic")
    return ChatAnthropic(model_name=model_name, temperature=temperature, api_key=api_key) # type: ignore


# llms.py
import requests
import json

# Retrieve the API key from environment variables
ARLIAI_API_KEY = os.getenv("ARLIAI_API_KEY")
API_URL = "https://api.arliai.com/v1/chat/completions"

def get_arli_ai_chat(model_name: str, api_key=None, temperature=0.7):
    """Get an instance of the ArliAI chat model."""
    api_key = api_key or ARLIAI_API_KEY
    return ArliAIChat(model_name=model_name, api_key=api_key, temperature=temperature)

class ArliAIChat:
    def __init__(self, model_name, api_key, temperature):
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature

    def stream(self, full_conversation):
        payload = json.dumps({
            "model": self.model_name,
            "messages": full_conversation,
            "temperature": self.temperature,
            "stream": True
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }

        response = requests.post(API_URL, headers=headers, data=payload, stream=True)
        return self.process_stream_response(response)

    def process_stream_response(self, response):
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('data: '):
                    line_str = line_str[6:]
                if line_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(line_str)
                    yield chunk.get('choices', [{}])[0].get('delta', {}).get('content')
                except json.JSONDecodeError:
                    print("Error decoding JSON:", line_str)





# OpenAI models
def get_openai_chat(model_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE):
    api_key = api_key or get_api_key("openai")
    return ChatOpenAI(model_name=model_name, temperature=temperature, api_key=api_key) # type: ignore

def get_openai_instruct(model_name:str,api_key=None, temperature=DEFAULT_TEMPERATURE):
    api_key = api_key or get_api_key("openai")
    return OpenAI(model=model_name, temperature=temperature, api_key=api_key) # type: ignore

def get_openai_embedding(model_name:str, api_key=None):
    api_key = api_key or get_api_key("openai")
    return OpenAIEmbeddings(model=model_name, api_key=api_key) # type: ignore

def get_azure_openai_chat(deployment_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE, azure_endpoint=None):
    api_key = api_key or get_api_key("openai_azure")
    azure_endpoint = azure_endpoint or os.getenv("OPENAI_AZURE_ENDPOINT")
    return AzureChatOpenAI(deployment_name=deployment_name, temperature=temperature, api_key=api_key, azure_endpoint=azure_endpoint) # type: ignore

def get_azure_openai_instruct(deployment_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE, azure_endpoint=None):
    api_key = api_key or get_api_key("openai_azure")
    azure_endpoint = azure_endpoint or os.getenv("OPENAI_AZURE_ENDPOINT")
    return AzureOpenAI(deployment_name=deployment_name, temperature=temperature, api_key=api_key, azure_endpoint=azure_endpoint) # type: ignore

def get_azure_openai_embedding(deployment_name:str, api_key=None, azure_endpoint=None):
    api_key = api_key or get_api_key("openai_azure")
    azure_endpoint = azure_endpoint or os.getenv("OPENAI_AZURE_ENDPOINT")
    return AzureOpenAIEmbeddings(deployment_name=deployment_name, api_key=api_key, azure_endpoint=azure_endpoint) # type: ignore

# Google models
def get_google_chat(model_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE):
    return ChatGoogleGenerativeAI(model=model_name, temperature=temperature, google_api_key=api_key, safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE }) # type: ignore

# Groq models
def get_groq_chat(model_name:str, api_key=None, temperature=DEFAULT_TEMPERATURE):
    api_key = api_key or get_api_key("groq")
    return ChatGroq(model_name=model_name, temperature=temperature, api_key=api_key) # type: ignore
   
# OpenRouter models
def get_openrouter(model_name: str="meta-llama/llama-3.1-8b-instruct:free", api_key=None, temperature=DEFAULT_TEMPERATURE):
    api_key = api_key or get_api_key("openrouter")
    return ChatOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1", model=model_name, temperature=temperature) # type: ignore
        
def get_embedding_hf(model_name="sentence-transformers/all-MiniLM-L6-v2"):
    return HuggingFaceEmbeddings(model_name=model_name)

def get_embedding_openai(api_key=None):
    api_key = api_key or get_api_key("openai")
    return OpenAIEmbeddings(api_key=api_key) #type: ignore

