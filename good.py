import requests
import json

ARLIAI_API_KEY = "05d2906a-01cb-41ed-8dd8-0a3e9d13e87e"
API_URL = "https://api.arliai.com/v1/chat/completions"

def create_payload(full_conversation):
    """Create the payload for the API request."""
    return json.dumps({
        "model": "Meta-Llama-3.1-8B-Instruct",
        "messages": full_conversation,
        "repetition_penalty": 1.1,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1024,
        "stream": True
    })

def get_headers():
    """Return headers for the API request."""
    return {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {ARLIAI_API_KEY}"
    }

def process_stream_response(response):
    """Process the streamed response and return the full response text."""
    chunks = []

    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8').strip()
            if line_str.startswith('data: '):
                line_str = line_str[6:]

            if line_str == '[DONE]':
                break

            try:
                chunk = json.loads(line_str)
                delta_content = chunk.get('choices', [{}])[0].get('delta', {}).get('content')
                if delta_content:
                    chunks.append(delta_content)
                    print(delta_content, end="", flush=True)
            except json.JSONDecodeError:
                print("Error decoding JSON:", line_str)

    return ''.join(chunks)

def stream_response(model, system_prompt, conversation_history):
    """Stream the response using the provided model."""
    # Combine system prompt and conversation history
    full_conversation = [{"role": "system", "content": system_prompt}] + conversation_history
    
    chunks = []
    response_generator = model.stream(full_conversation)
    for chunk in response_generator:
        delta_content = chunk.content
        if delta_content is not None:
            chunks.append(delta_content)
            print(delta_content, end="", flush=True)
    
    print('\n')
    return ''.join(chunks)


conversation_history = []

system_prompt = ''

while True:
        user_input = input('User:\n')

        conversation_history.append({"role": "user", "content": user_input})
    
        # Stream the response with the system prompt, user input, and conversation history
        chatbot_response = stream_response(system_prompt, conversation_history)

        conversation_history.append({"role": "ai", "content": chatbot_response})
