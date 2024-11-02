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
import logging

# Configure logging for PageDoAgent
logging.basicConfig(filename='page_do_agent.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PageDoAgent:
    def __init__(self):
        try:
            load_dotenv()
            self.api_key = os.getenv("OPENROUTERAPIKEY")
            self.client = Client("derekalia/OmniParser2")
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        except Exception as e:
            logging.error(f"Error during PageDoAgent initialization: {e}")
            raise

    def retrieve_json(self):
        try:
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
        except Exception as e:
            logging.error(f"Error retrieving JSON data: {e}")
            print(f"Error retrieving JSON data: {e}")
            raise

    def encode_image_to_base64(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            logging.error(f"Error encoding image to Base64: {e}")
            print(f"Error encoding image to Base64: {e}")
            raise

    def run_do_agent(self, action, current_page_dict, image_path):
        try:
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
            initial_response.raise_for_status()
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
            final_response.raise_for_status()
            final_result = final_response.json()
            code = final_result['choices'][0]['message']['content']

            conda_env_name = 'myenv'

            # Construct the path to the Python executable in that environment
            conda_env_path = os.path.join('/root/miniconda/envs', conda_env_name, 'bin', 'python')

            # Run the script using the Conda environment's Python
            subprocess.run([conda_env_path, '-c', code], check=True)

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error in run_do_agent: {http_err}")
            print(f"HTTP error in run_do_agent: {http_err}")
            raise
        except subprocess.CalledProcessError as sub_err:
            logging.error(f"Subprocess execution error: {sub_err}")
            print(f"Subprocess execution error: {sub_err}")
            raise
        except json.JSONDecodeError as json_err:
            logging.error(f"JSON decoding error in run_do_agent: {json_err}")
            print(f"JSON decoding error in run_do_agent: {json_err}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in run_do_agent: {e}")
            print(f"Unexpected error in run_do_agent: {e}")
            raise

    def runDoAgent(self, action):
        try:
            result, temp_file_path = self.retrieve_json()
            self.run_do_agent(action, result, temp_file_path)
        except Exception as e:
            logging.error(f"Error in runDoAgent: {e}")
            print(f"Error in runDoAgent: {e}")
            raise