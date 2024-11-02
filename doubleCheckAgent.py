import pyautogui
import json
import groq
import os
from gradio_client import Client, handle_file
import tempfile
import re
import requests
from dotenv import load_dotenv
import base64

'''
* Screenshot retreival (call from the json file)
* take pass from the double check call (what should have been created)
* consolidate into one input
* pass to llama

return True or False to the calling function
'''

def parse_and_combine_output(output_string):
    # Split the input string to separate the text data and coordinate data
    output_parts = output_string.split("', '")
    text_data = output_parts[1].strip()  # The text box section
    coord_data = output_parts[2].strip().rstrip("')")  # The coordinate section

    # Parse the text box data using regex
    text_boxes = []
    text_pattern = r'Text Box ID (\d+): (.+)'
    for match in re.finditer(text_pattern, text_data):
        text_boxes.append({"id": int(match.group(1)), "content": match.group(2)})

    # Convert the coordinate data string to a dictionary
    coordinates = json.loads(coord_data.replace("'", '"'))

    # Combine text boxes with their corresponding coordinates
    combined_data = []
    for text_box in text_boxes:
        box_id = str(text_box["id"])
        if box_id in coordinates:
            combined_entry = {
                "id": text_box["id"],
                "content": text_box["content"],
                "coordinates": coordinates[box_id]
            }
            combined_data.append(combined_entry)

    # Return the combined data as a JSON
    return json.dumps(combined_data, indent=4)

def retrieveJson() -> dict:
    #request screenshot and convert to json through the api cv model

    screenshot = pyautogui.screenshot()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        screenshot.save(temp_file.name)
        temp_file_path = temp_file.name
    
    #testing:
    #screenshot.show()  WORKS

    currentPageDict = {}

    from gradio_client import Client, handle_file

    client = Client("derekalia/OmniParser2")
    result = client.predict(
            image_input=handle_file(temp_file_path),
            box_threshold=0.05,
            iou_threshold=0.1,
            api_name="/process"
    )
    #print(result)

    #testing with sim json path 
    '''file_path = "/Users/mob/Desktop/BitRich/TestCVOutput.json"
    with open(file_path, "r") as json_file:
        currentPageDict = json.load(json_file)'''
    
    return parse_and_combine_output(result)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def runLLaMaDoubleCheckAgent(stateCheckString: str, currentPageDict: dict, imagePath: str) -> bool:

    encoded_image = encode_image_to_base64(imagePath)

    load_dotenv()
    api_key = os.getenv("OPENROUTERAPIKEY")
    #print(f"apikey= {api_key}")
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
    }

    LLaMaSystemPrompt = (
    f"You are an AI agent tasked with verifying if a web page, described by a JSON representation of its elements and content, matches the expected page. "
    f"Your task is to analyze the central page elements and key headings while giving less priority to the top navigation or peripheral content. "
    f"Use the provided JSON dictionary and the attached image to check if they align with the expected page description. "
    f"Ensure that the analysis focuses on the primary content and structure of the page. Output only ‘true’ or ‘false’ based on this analysis."
    )

    LLaMaUserPrompt = (
    f"Review the JSON dictionary provided under ‘currentPageDict’, which contains all detected central elements and their attributes, as well as the attached image. Do not pay as much attention to the top bar including browser navigation elements such as (e.g., 'File', 'Edit', 'View'), date and time information"
    f"Compare these with the expected page description: {stateCheckString}. "
    f"Focus primarily on central elements and key headings that convey the main purpose of the page. Respond with ‘true’ if the central page content matches the expectation, or ‘false’ if it does not. Do not include anything else\n\n"
    f"currentPageDict= {currentPageDict}"
    )
    
    payload = {
    "model": "meta-llama/llama-3.2-90b-vision-instruct",  # Specify the model name
    "messages": [
        {"role": "system", "content": LLaMaSystemPrompt},
        {"role": "user", "content": LLaMaUserPrompt}
    ],
    "image": encoded_image,  # Add the base64-encoded image here
    "temperature": 0.0  # Set temperature as needed, 0.0 for deterministic response
}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        #print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error: {response.status_code} - {response.text}")

    return result['choices'][0]['message']['content']

def read_json_to_dict(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def doubleCheckAgent(desiredState: str):
    ''' load_dotenv()
    currentPageDict = retrieveJson()
    print(currentPageDict)
    '''
    file_path = '/Users/mob/Desktop/BitRich/TestCVOutput.json'  # Replace with your JSON file path
    local_dict = read_json_to_dict(file_path)

    currentPageDict = local_dict

    stateCheckStr = "MetaMask connect a wallet chrome extension pop up"

    imagePath= '/Users/mob/Desktop/BitRich/sampleImg.png'

    bool = runLLaMaDoubleCheckAgent(stateCheckStr, currentPageDict, imagePath)

    print(bool)
    


    return 

if __name__ == "__main__":
    doubleCheckAgent("testing")
