import pyautogui
import json
import os
import tempfile
import requests
from dotenv import load_dotenv
import base64
import logging
from gradio import GradioAPI  # Importing the GradioAPI class

# Configure logging for PageVerificationAgent
logging.basicConfig(filename='page_verification_agent.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PageVerificationAgent:
    def __init__(self):
        try:
            load_dotenv()
            self.api_key = os.getenv("OPENROUTERAPIKEY")
            self.gradio_api = GradioAPI()  # Using the shared GradioAPI instance
        except Exception as e:
            logging.error(f"Error during PageVerificationAgent initialization: {e}")
            raise

    def retrieve_json(self):
        try:
            screenshot = pyautogui.screenshot()
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                screenshot.save(temp_file.name)
                temp_file_path = temp_file.name

            # Directly use the client instance to predict
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

    def encode_image_to_base64(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            logging.error(f"Error encoding image to Base64: {e}")
            print(f"Error encoding image to Base64: {e}")
            raise

    def run_llama_double_check_agent(self, state_check_string, current_page_dict, image_path):
        try:
            encoded_image = self.encode_image_to_base64(image_path)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            llama_system_prompt = (
                f"You are an AI agent tasked with verifying if a web page, described by a JSON representation of its elements and content, matches the expected page. "
                f"Your task is to analyze the central page elements and key headings while giving less priority to the top navigation or peripheral content. "
                f"Use the provided JSON dictionary and the attached image to check if they align with the expected page description. "
                f"Ensure that the analysis focuses on the primary content and structure of the page. Output only ‘true’ or ‘false’ based on this analysis."
            )

            llama_user_prompt = (
                f"Review the JSON dictionary provided under ‘currentPageDict’, which contains all detected central elements and their attributes, as well as the attached image. "
                f"Do not pay as much attention to the top bar including browser navigation elements such as (e.g., 'File', 'Edit', 'View'), date, and time information. "
                f"Compare these with the expected page description: {state_check_string}. "
                f"Focus primarily on central elements and key headings that convey the main purpose of the page. Respond with ‘true’ if the central page content matches the expectation, or ‘false’ if it does not. Do not include anything else\n\n"
                f"currentPageDict= {current_page_dict}"
            )

            payload = self.gradio_api.construct_payload(
                model="meta-llama/llama-3.2-90b-vision-instruct",
                system_prompt=llama_system_prompt,
                user_prompt=llama_user_prompt,
                temperature=0.0
            )

            # Make the API call and return the response
            result = self.gradio_api.call_gradio_api(payload, image_path)
            return result
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error in run_llama_double_check_agent: {http_err}")
            print(f"HTTP error in run_llama_double_check_agent: {http_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error in run_llama_double_check_agent: {req_err}")
            print(f"Request error in run_llama_double_check_agent: {req_err}")
            raise
        except json.JSONDecodeError as json_err:
            logging.error(f"JSON decoding error in run_llama_double_check_agent: {json_err}")
            print(f"JSON decoding error in run_llama_double_check_agent: {json_err}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in run_llama_double_check_agent: {e}")
            print(f"Unexpected error in run_llama_double_check_agent: {e}")
            raise

    def read_json_to_dict(self, file_path):
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError as fnf_err:
            logging.error(f"File not found: {fnf_err}")
            print(f"File not found: {fnf_err}")
            raise
        except json.JSONDecodeError as json_err:
            logging.error(f"JSON decoding error in read_json_to_dict: {json_err}")
            print(f"JSON decoding error in read_json_to_dict: {json_err}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in read_json_to_dict: {e}")
            print(f"Unexpected error in read_json_to_dict: {e}")
            raise

    def double_check_agent(self, desired_state):
        try:
            current_page_dict, temp_file_path = self.retrieve_json()
            result = self.run_llama_double_check_agent(desired_state, current_page_dict, temp_file_path)
            print(result)
            return result
        except Exception as e:
            logging.error(f"Error in double_check_agent: {e}")
            print(f"Error in double_check_agent: {e}")
            raise

# Example usage
if __name__ == "__main__":
    agent = PageVerificationAgent()
    agent.double_check_agent("chrome open to youtube")