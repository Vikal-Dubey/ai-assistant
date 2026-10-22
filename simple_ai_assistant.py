from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = []

messages.append(
    {
        "role": "system",
        "content": "Act like a humorous assistant. The response length should be within 100 words."
    }
)

while True:

    user_input = input("Vikal: ").strip()

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    if not user_input:
        continue

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )

    assistant_reply = response.choices[0].message.content
    messages.append(
        {
            "role": "assistant",
            "content": assistant_reply
        }
    )

    print("LLM Response:")
    print("Assistant: " + assistant_reply)