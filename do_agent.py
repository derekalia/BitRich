import pyautogui
import os
import tempfile
import subprocess
import requests
import json
import logging
from dotenv import load_dotenv
from gradio import GradioAPI  # Ensure the import path is correct

# Configure logging for PageDoAgent
logging.basicConfig(filename='page_do_agent.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PageDoAgent:
    def __init__(self):
        try:
            load_dotenv()
            self.api_key = os.getenv("OPENROUTERAPIKEY")
            self.gradio_api = GradioAPI()  # Use the singleton instance of GradioAPI
        except Exception as e:
            logging.error(f"Error during PageDoAgent initialization: {e}")
            raise

    def retrieve_json(self):
        try:
            # Take a screenshot and save it to a temporary file
            screenshot = pyautogui.screenshot()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                screenshot.save(temp_file.name)
                temp_file_path = temp_file.name

            # Use Gradio client to make a prediction call
            result = self.gradio_api.client.predict(
                image_input=temp_file_path,  # Directly pass the image path
                box_threshold=0.05,
                iou_threshold=0.1,
                api_name="/process"
            )

            return result, temp_file_path
        except Exception as e:
            logging.error(f"Error retrieving JSON data: {e}")
            print(f"Error retrieving JSON data: {e}")
            raise

    def run_do_agent(self, action, current_page_dict, image_path):
        try:
            # Create and send payloads for processing
            system_prompt = (
                "You are a helpful assistant. I'll provide you with the JSON file containing the elements of the website, "
                "and please reply with the possible element to open the notification with the format in JSON only like "
                "Element:{\"Icon Box ID\": 175, \"Coordinates\": [3122, 257, 101, 106], \"Description\": \"a notification or alert.\"}"
            )
            initial_user_prompt = f"The JSON of the website elements is as follows:\n{current_page_dict}\n"

            # Generate the initial response
            element_info = self.gradio_api.call_gradio_api(
                self.gradio_api.construct_payload(
                    model="meta-llama/llama-3.2-90b-vision-instruct",
                    system_prompt=system_prompt,
                    user_prompt=initial_user_prompt,
                    temperature=0.0
                ),
                image_path
            )

            # Create and send the final payload with the action and element info
            final_user_prompt = (
                "The JSON of the website elements is as follows:\n"
                f"{element_info}\n"
                f"Do: {action}"
            )

            code = self.gradio_api.call_gradio_api(
                self.gradio_api.construct_payload(
                    model="meta-llama/llama-3.2-90b-vision-instruct",
                    system_prompt=(
                        "You are a helpful assistant. I'll provide you with the JSON containing the elements of the website, "
                        "and please create the Python code using pyautogui to achieve the function requested by the user. "
                        "Answer only with the Python code, without anything else, in double quotes."
                    ),
                    user_prompt=final_user_prompt,
                    temperature=0.0
                ),
                image_path
            )

            conda_env_name = 'myenv'
            conda_env_path = os.path.join('/root/miniconda/envs', conda_env_name, 'bin', 'python')

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