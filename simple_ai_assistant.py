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

MAX_STEPS = 5
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

#Chat loop starts from here
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
    
    # Chained Tool calling
    for step in range(MAX_STEPS):

        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )
        
        assistant_reply = response.choices[0].message

        if not assistant_reply.tool_calls:
            break

        messages.append(assistant_reply)

        for tool_call in assistant_reply.tool_calls:
            func_name = tool_call.function.name

            try:
                func_args = json.loads(tool_call.function.arguments or "{}")

                fn = FUNCTION_NAME_TO_FUNCTION[func_name]
                result = fn(**func_args)

            except Exception as e:
                result = f"Error occurred while executing {func_name}: {e}"

            messages.append({
                "role" : "tool",
                "tool_call_id" : tool_call.id,
                "content" : str(result)
            })

    else:
        # Ran out of steps, The model never gave the final answer
        fallback = "Sorry, I couldn't complete the request within the allowed steps."
        messages.append({
            "role": "assistant",
            "content": fallback
        })
        print("Assistant: " + fallback)
        continue

    final_reply = assistant_reply.content or "I couldn't generate a response."
    messages.append(
        {
            "role": "assistant",
            "content": final_reply
        }
    )

    print("Assistant: " + final_reply)