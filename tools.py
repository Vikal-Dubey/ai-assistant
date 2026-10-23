from datetime import datetime
from ddgs import DDGS
import requests

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    
    except requests.RequestException as e:
        return f"Error fetching weather data for{city}: {e}"

def get_user_city():
    return input("Please enter your city for weather information: ").strip()

def web_search(query):
    try:
        results = DDGS().text(
            query,
            max_results=5
        )

        if not results:
            return "No search results found."

        formatted_results = []

        for item in results:
            formatted_results.append(
                f"Title: {item.get('title', 'N/A')}\n"
                f"URL: {item.get('href', 'N/A')}\n"
                f"Snippet: {item.get('body', 'N/A')}"
            )

        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Web search failed: {e}"

TOOLS = [
    {
        "type": "function",
        "function" : {
            "name" : "get_current_time",
            "description" : "Return the current date and time in the format YYYY-MM-DD HH:MM:SS",
            "parameters" : {
                "type" : "object",
                "properties" : {}
            }
        }
    }, {
        "type" : "function",
        "function" : {
            "name" : "get_city_weather",
            "description" : "Return the current weather for a given city",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "city" : {
                        "type" : "string",
                        "description" : "The name of the city to get the weather for"
                    }
                },
                "required" : ["city"]
            }
        }
    }, {
        "type" : "function",
        "function" : {
            "name" : "web_search",
            "description" : "Perform a web search for a given query and return the top 5 results",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "query" : {
                        "type" : "string",
                        "description" : "The search query"
                    }
                },
                "required" : ["query"]
            }
        }
    }, {
        "type" : "function",
        "function" : {
            "name" : "get_user_city",
            "description" : "Ask the user to enter their city for weather information.",
            "parameters" : {
                "type" : "object",
                "parameters" : {}
            }
        }
    }
]

FUNCTION_NAME_TO_FUNCTION = {
    "get_current_time" : get_current_time,
    "get_city_weather" : get_city_weather,
    "get_user_city" : get_user_city,
    "web_search": web_search
}