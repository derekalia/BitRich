import pyautogui
import json
import os
from gradio_client import Client, handle_file
import tempfile
import re
import requests
from dotenv import load_dotenv
import base64
import subprocess

class PageDoAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENROUTERAPIKEY")
        self.client = Client("derekalia/OmniParser2")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def retrieve_json(self):
        screenshot = pyautogui.screenshot()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            screenshot.save(temp_file.name)
            temp_file_path = temp_file.name
        
        result = self.client.predict(
            image_input=handle_file(temp_file_path),
            box_threshold=0.05,
            iou_threshold=0.1,
            api_name="/process"
        )

        return result, temp_file_path
    
    def encode_image_to_base64(self, image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    
    def run_do_agent(self, action, current_page_dict, image_path):
        
        # Encode the image to Base64
        encoded_image = self.encode_image_to_base64(image_path)

        # Set headers for the API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Initial user prompt with JSON of website elements
        initial_user_prompt = (
            "The JSON of the website elements is as follows:\n"
            f"{current_page_dict}\n"
        )

        # Define the initial payload to identify the notification element
        initial_payload = {
            "model": "meta-llama/llama-3.2-90b-vision-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. I'll provide you with the JSON file containing the elements of the website, "
                        "and please reply with the possible element to open the notification with the format in JSON only like "
                        "Element:{\"Icon Box ID\": 175, \"Coordinates\": [3122, 257, 101, 106], \"Description\": \"a notification or alert.\"}"
                    ),
                },
                {
                    "role": "user",
                    "content": initial_user_prompt,
                },
            ],
            "image": encoded_image,
            "temperature": 0.0
        }

        # Send the initial request and parse the response
        initial_response = requests.post(self.base_url, headers=headers, json=initial_payload)
        initial_result = initial_response.json()
        element_info = initial_result['choices'][0]['message']['content']

        # Updated user prompt with action and element information
        final_user_prompt = (
            "The JSON of the website elements is as follows:\n"
            f"{element_info}\n"
            f"Do: {action}"
        )

        # Define the final payload to generate Python code for the action
        final_payload = {
            "model": "meta-llama/llama-3.2-90b-vision-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. I'll provide you with the JSON containing the elements of the website, "
                        "and please create the Python code using pyautogui to achieve the function requested by the user. "
                        "Answer only with the Python code, without anything else, in double quotes."
                    ),
                },
                {
                    "role": "user",
                    "content": final_user_prompt,
                },
            ],
            "image": encoded_image,
            "temperature": 0.0
        }


        # Send the final request and parse the response
        final_response = requests.post(self.base_url, headers=headers, json=final_payload)
        final_result = final_response.json()
        code = final_result['choices'][0]['message']['content']

        conda_env_name = 'myenv'

        # Construct the path to the Python executable in that environment
        conda_env_path = os.path.join('/root/miniconda/envs', conda_env_name, 'bin', 'python')

        # Run the script using the Conda environment's Python
        subprocess.run([conda_env_path, '-c' ,code])

    def runDoAgent(self, action):
        result, temp_file_path = self.retrieve_json()

        self.run_do_agent(action, result, temp_file_path)