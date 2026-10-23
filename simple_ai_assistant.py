from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION
import json
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
        "content": (
            "Act like a humble assistant. Keep responses short. "
            "When the user asks to search the web, find the latest information, "
            "or requests recent developments, you MUST call web_search. "
            "Base your answer on the returned results and include relevant URLs. "
            "Never pretend you searched if you did not."
        )
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
        messages=messages,
        tools=TOOLS
    )

    assistant_reply = response.choices[0].message

    if assistant_reply.tool_calls:
        messages.append(assistant_reply)

        for tool_call in assistant_reply.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments or "{}")

            fn = FUNCTION_NAME_TO_FUNCTION[func_name]
            result = fn(**func_args)

            messages.append({
                "role" : "tool",
                "tool_call_id" : tool_call.id,
                "content" : str(result)
            })

        #2nd LLM API call to get the final response after tool execution
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )

        assistant_reply = response.choices[0].message

    messages.append(
        {
            "role": "assistant",
            "content": assistant_reply.content
        }
    )

    print("Assistant: " + assistant_reply.content)