import os
import requests

# 1. Set your OpenRouter API key
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 2. Function to send a message to the chatbot
def chat_with_openrouter(message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",  # You can use gpt-4o-mini, gpt-3.5-turbo, etc.
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Get chatbot reply
        reply = data["choices"][0]["message"]["content"]
        return reply
    else:
        return f"Error: {response.status_code}, {response.text}"

# 3. Run the chatbot
print("Chatbot (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    reply = chat_with_openrouter(user_input)
    print("Bot:", reply)
