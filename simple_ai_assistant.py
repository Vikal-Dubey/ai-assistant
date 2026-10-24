# standard library imports
import os

#Third-party imports
from openai import OpenAI
from dotenv import load_dotenv
from types import SimpleNamespace

#Local module imports
from tools import TOOLS, run_tool
from Utilities.utilities import log


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
            "Be a humble, helpful assistant. Keep answers short and clear. "
            "Answer general questions directly without using tools. "
            "Call web_search only when the user explicitly asks to search the web "
            "or requests latest, current, or recent information. "
            "Do not search for simple explanations or general knowledge. "
            "Use search results to answer and include relevant URLs. "
            "Never claim to have searched if you did not."
        )
    }
)

def stream_chat(history):
    stream = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools=TOOLS,
        stream=True
    )

    full_response = ""
    calls = {}
    label_printed = False

    #Streaming started
    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            #1. Content Streaming: Do we have message(content) from the LLM
            if delta.content:
                if not label_printed:
                    print("🤖 Assistant: ", end="")
                    label_printed = True
                
                print(delta.content, end="", flush=True)
                full_response += delta.content

            #2. Tool Calls
            for tc in (delta.tool_calls or []):
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments=""))
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments
    except KeyboardInterrupt:
        print("\n {Stopped By You}")
        calss = {}

    if label_printed:
        print() #Move to the next line after assistant's response

    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])

    return full_response, calls_list

def build_tool_calls_payload(tool_calls):

    """
    Converts our collected tool calls into dict format
    that the api expects inside an assistant message.
    """

    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id" : tool_call.id,
            "type" : "function",
            "function" : {
                "name" : tool_call.function.name,
                "arguments" : tool_call.function.arguments
            }
        }
        payload.append(tool_call_dict)

    return payload

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

        full_response, tool_calls = stream_chat(messages)
        

        if not tool_calls:
            final_response = full_response or "I couldn't generate a response."

            messages.append({
                "role": "assistant",
                "content": final_response
            })
            break

        log(f" Step {step + 1}: Assistant called {len(tool_calls)} tool(s).")
        messages.append({
            "role" : "assistant",
            "content" : full_response,
            "tool_calls" : build_tool_calls_payload(tool_calls)
        })

        for tool_call in tool_calls:
            result = run_tool(tool_call)
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
        print("🤖 Assistant: " + fallback)
        continue