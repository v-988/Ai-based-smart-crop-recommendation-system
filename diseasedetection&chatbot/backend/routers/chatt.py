# 3. Run the chatbot
print("Chatbot (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    reply = chat_with_openrouter(user_input)
    print("Bot:", reply)