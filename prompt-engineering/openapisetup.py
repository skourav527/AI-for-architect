import openai
import os
import json
import os
os.environ["OPENAI_API_BASE"] = "https://api.openai.com/v1"
os.environ["PYTHONHTTPSVERIFY"] = "0"

# Read API key from appsettings.json
with open(os.path.join(os.path.dirname(__file__), "appsettings.json"), "r") as f:
    config = json.load(f)
api_key_value = config.get("OPENAI_API_KEY")

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key = api_key_value

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
