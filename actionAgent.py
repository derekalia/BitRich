from groq import Groq
import os
import json
os.environ["GROQ_API_KEY"] = "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"
# Initialize Groq client with API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Read website elements from a text file
with open("/root/message.txt", "r") as file:
    website_elements = file.read()

# Define the user prompt content using string formatting
user_prompt = (
    "The JSON of the website elements is as follows:\n"
    f"{website_elements}\n"
)

# Create a chat completion to retrieve the necessary pyautogui code
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. I'll provide you with the JSON file containing the elements of the website, and please reply with the possible element to open the notification with with format in json only like Element:{\"Icon Box ID\": 175, \"Coordinates\": [3122, 257, 101, 106], \"Description\": \"a notification or alert.\"}"
            ),
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    model="llama3-70b-8192"
)
ans=chat_completion.choices[0].message.content
print(ans)
# Initialize Groq client with API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# Define the user prompt content using string formatting
user_prompt = (
    "The JSON of the website elements is as follows:\n"
    f"{ans}"
    "click on the notification tab"
)

# Create a chat completion to retrieve the necessary pyautogui code
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. I'll provide you with the JSON containing the elements of the website, and please create the python code using pyautogui to achieve the function ask by the user."
            ),
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    model="llama3-70b-8192"
)

chat_completion.choices[0].message.content