from groq import Groq
import os
import json
os.environ["GROQ_API_KEY"] = "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"
# Initialize Groq client with API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# Define the user prompt content using string formatting
user_prompt = (
    "You are an orchestrator and you are given the following tools to achieve the ultimate goal the current state of the website is like the following Json containing the web page element:\n"
    "Name:double_check_agent"
    "Usage:To double check the state of website fit the yes no question for example: is the website login?"
    "Input:qestion in the string format"
    "Output: boolen"
    "Name:execution_agent"
    "Usage:To perfom a simple task on the webpage for example click on the notification button try break the task down"
    "Input:"
    "Output: boolen"
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