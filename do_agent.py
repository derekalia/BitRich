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
                "You are an assistant specialized in automating tasks on web pages. Analyze the JSON data containing the elements of a web page and extract relevant components to perform the specified task. "
                "Respond only with a JSON object that includes the coordinates of relevant elements (e.g., {\"Element Name\": ..., \"Coordinates\": ..., \"Description\": ...}). "
                "Ensure the response is focused on providing coordinates only and avoid using functions like 'getActiveWindowTitle' or other window-handling code."
            )
            initial_user_prompt = f"Here is the JSON data of the web page:\n{current_page_dict}\n"

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
            initial_response = requests.post(self.base_url, headers=headers, json=initial_payload, timeout=10)
            initial_response.raise_for_status()
            element_info = initial_response.json()['choices'][0]['message']['content']

            # Final prompt to generate Python code
            system_prompt_code = (
                "You are an AI agent that generates Python code using the `pyautogui` library to automate interactions with a web page. "
                "Generate Python code that uses only the coordinates provided in the JSON data to move the mouse, click, and type as necessary. "
                "Do not include any functions for window handling like 'getActiveWindowTitle' or anything that interacts with the operating system's windowing system. "
                "Ensure the code runs independently, using only the given coordinates and `pyautogui` functions. Respond with raw Python code only."
            )

            final_user_prompt = (
                "Here is the JSON data for the web page elements and relevant coordinates:\n"
                f"{element_info}\n"
                f"Perform the following task: {action}"
            )

            final_payload = {
                "model": "meta-llama/llama-3.2-90b-vision-instruct",
                "messages": [
                    {"role": "system", "content": system_prompt_code},
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

            venv_python_path = '/Users/mob/Desktop/BitRich/venv/bin/python'  

            #pyautogui.FAILSAFE = False

            code = final_response.json()['choices'][0]['message']['content']
            code = code.strip('```python').strip('```').strip()  # Remove any formatting indicators

            # Remove non-Python explanations or appended text outside of the code
            if '```' in code:
                code = code.split('```')[0]  # Retain only the code portion before any markdown remnants

            venv_python_path = '/Users/mob/Desktop/BitRich/venv/bin/python'

            print("Executing the following code:")
            print(code)  # Display the cleaned Python code for verification

            try:
                subprocess.run([venv_python_path, '-c', code], check=True)
            except subprocess.CalledProcessError as sub_err:
                logging.error(f"Subprocess execution error: {sub_err}")
                print(f"Subprocess execution error: {sub_err}")
                raise

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