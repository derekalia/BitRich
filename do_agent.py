import pyautogui
import os
import tempfile
import subprocess
import requests
import json
import logging
import base64
from dotenv import load_dotenv
from gradio import GradioAPI, handle_file  # Ensure the import path is correct

# Configure logging for PageDoAgent
logging.basicConfig(filename='page_do_agent.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PageDoAgent:
    def __init__(self):
        try:
            load_dotenv()
            self.api_key = os.getenv("OPENROUTERAPIKEY")
            self.gradio_api = GradioAPI()  # Use the singleton instance of GradioAPI
            self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        except Exception as e:
            logging.error(f"Error during PageDoAgent initialization: {e}")
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

    def retrieve_json(self):
        try:
            # Take a screenshot and save it to a temporary file
            screenshot = pyautogui.screenshot()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                screenshot.save(temp_file.name)
                temp_file_path = temp_file.name

            # Use Gradio client to make a prediction call
            result = self.gradio_api.call_gradio_api(
                temp_file_path # Directly pass the image path
            )

            return result, temp_file_path
        except Exception as e:
            logging.error(f"Error retrieving JSON data: {e}")
            print(f"Error retrieving JSON data: {e}")
            raise

    def run_do_agent(self, action, current_page_dict, image_path):
        try:
            # Encode the image for payloads if necessary
            encoded_image = self.encode_image_to_base64(image_path)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Initial prompt for element identification
            system_prompt = (
                "You are a helpful assistant. I'll provide you with the JSON file containing the elements of the website, "
                "and please reply with the possible element to open the notification with the format in JSON only like "
                "Element:{\"Icon Box ID\": 175, \"Coordinates\": [3122, 257, 101, 106], \"Description\": \"a notification or alert.\"}"
            )
            initial_user_prompt = f"The JSON of the website elements is as follows:\n{current_page_dict}\n"

            initial_payload = {
                "model": "meta-llama/llama-3.2-90b-vision-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": initial_user_prompt}
                ],
                "image": encoded_image,
                "temperature": 0.0
            }

            # Make the initial API call to OpenRouter for LLaMA
            initial_response = requests.post(self.base_url, headers=headers, json=initial_payload)
            initial_response.raise_for_status()
            element_info = initial_response.json()['choices'][0]['message']['content']

            # Final prompt to generate Python code
            final_user_prompt = (
                "The JSON of the website elements is as follows:\n"
                f"{element_info}\n"
                f"Do: {action}"
            )

            final_payload = {
                "model": "meta-llama/llama-3.2-90b-vision-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant. I'll provide you with the JSON containing the elements of the website, "
                            "and please create the Python code using pyautogui to achieve the function requested by the user. "
                            "Answer only with the Python code, without anything else, in double quotes only. Make sure to wrap it in double quotes."
                        )
                    },
                    {"role": "user", "content": final_user_prompt}
                ],
                "image": encoded_image,
                "temperature": 0.0
            }

            
            # Make the final API call to OpenRouter for LLaMA
            final_response = requests.post(self.base_url, headers=headers, json=final_payload)
            final_response.raise_for_status()
            code = final_response.json()['choices'][0]['message']['content']
            code = code.strip('```python').strip('```').strip()

            conda_env_name = 'myenv'
            conda_env_path = os.path.join('/Users/mob/anaconda3/envs', conda_env_name, 'bin', 'python')

            print(code)
            # Run the generated Python code using the Conda environment's Python
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