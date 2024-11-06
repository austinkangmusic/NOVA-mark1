import chat_utils

# Initialize LLM models
chat_utils.initialize()

chat_llm = chat_utils.use_chat_llm()



def stream_response(model, system_prompt, conversation_history):
    """Stream the response using the provided model."""
    # Combine system prompt and conversation history
    full_conversation = [{"role": "system", "content": system_prompt}] + conversation_history
    
    chunks = []
    
    # Stream response from the model
    response_generator = model.stream(full_conversation)
    
    # Iterate through the streamed response
    for chunk in response_generator:
        if chunk is None:
            continue  # Skip if chunk is None

        # Check if chunk is an object and contains content
        if hasattr(chunk, 'content'):  # Check if chunk has a 'content' attribute
            delta_content = chunk.content
            if delta_content is not None:
                chunks.append(delta_content)
                print(delta_content, end="", flush=True)
        elif isinstance(chunk, str):  # If chunk is a string, append directly
            chunks.append(chunk)
            print(chunk, end="", flush=True)

    print('\n')
    return ''.join(chunks)


conversation_history = []

system_prompt = ''

while True:
        user_input = input('User:\n')

        conversation_history.append({"role": "user", "content": user_input})
    
        # Stream the response with the system prompt, user input, and conversation history
        chatbot_response = stream_response(chat_llm, system_prompt, conversation_history)

        conversation_history.append({"role": "ai", "content": chatbot_response})