import os
starting_seq = "\033[90m"
ending_seq = "\033[0m"

def log(text):
    if os.getenv("DEBUG") == "True":
        print(f"  {starting_seq}{text}{ending_seq}")