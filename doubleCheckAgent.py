import pyautogui
import json
import groq
import os
import gradio_client

'''
* Screenshot retreival (call from the json file)
* take pass from the double check call (what should have been created)
* consolidate into one input
* pass to llama

return True or False to the calling function
'''

def retrieveJson() -> dict:
    #request screenshot and convert to json through the api cv model

    screenshot = pyautogui.screenshot()
    
    #testing:
    #screenshot.show()  WORKS

    currentPageDict = {}

    from gradio_client import Client, handle_file

    client = Client("derekalia/OmniParser2")
    result = client.predict(
            image_input=handle_file('https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png'),
            box_threshold=0.05,
            iou_threshold=0.1,
            api_name="/process"
    )
    print(result)

    #testing with sim json path 
    '''file_path = "/Users/mob/Desktop/BitRich/TestCVOutput.json"
    with open(file_path, "r") as json_file:
        currentPageDict = json.load(json_file)'''
    
    return currentPageDict

def runLLaMaDoubleCheckAgent(stateCheckString: str, currentPageDict: dict) -> bool:

    client = groq(api_key=os.getenv("GROQ_API_KEY"))

    LLaMaSystemPrompt = f"You are an AI agent tasked with verifying if a web page, described by a JSON representation of its elements and content, matches the expected page. Your task is to analyze the page structure and content, using the provided JSON dictionary and an expected page description, and determine if they align. Consider the overall page structure and text content as the most important factors but allow for minor variations that do not change the core meaning of the page. Output only ‘true’ or ‘false’ based on this analysis."
    LLaMaUserPrompt = f"Review the JSON dictionary provided under ‘currentPageDict’, which contains all detected elements and their attributes. Compare it to the expected page description: {stateCheckString}. Based on this comparison, determine if the page matches the expectation. Respond with ‘true’ if it does, or ‘false’ if it does not.\n\n currentPageDict= {currentPageDict}"
    
    chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": f"{LLaMaSystemPrompt}"},
        {"role": "user", "content": f"{LLaMaUserPrompt}"}
        ],
    model="llama3-70b-8192"
    )

    print(chat_completion)

    return chat_completion

def doubleCheckAgent(desiredState: str):
    
    currentPageDict = retrieveJson()
    
    print(currentPageDict)

    return 

if __name__ == "__main__":
    doubleCheckAgent("testing")
