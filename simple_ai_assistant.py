from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

while True:

    user_input = input("Vikal: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    if not user_input:
        continue

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role":"user",
                "content":user_input
            }
        ]
    )

    print("LLM Response:")
    print("Assistant: " + response.choices[0].message.content)