import os
import json
import pyautogui
import tempfile
import logging
from gradio_client import handle_file
from dotenv import load_dotenv
from doubleCheckAgent import PageVerificationAgent

class MotherAgent:
    def __init__(self):
        load_dotenv()
        self.verification_agent = PageVerificationAgent()
        self.goal_attempts = 3  # Number of attempts before giving up
        self.completed_goals = []  # List of completed goals
        self.overall_goal = ""
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

        # Configure logging
        logging.basicConfig(filename='mother_agent.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    def log_goal(self, message):
        """Logs goal messages."""
        logging.info(message)

    def create_initial_goal(self, overall_goal):
        """Creates the initial goal based on the overall objective."""
        self.overall_goal = overall_goal
        return f"Determine the first step to achieve the overall goal: {overall_goal}"

    def generate_next_goal(self, current_screen_json, screenshot_path, current_goal, previous_goals):
        """Generates the next goal using LLaMA based on the current state and previous goals."""
        encoded_image = self.verification_agent.encode_image_to_base64(screenshot_path)

        headers = {
            "Authorization": f"Bearer {self.verification_agent.api_key}",
            "Content-Type": "application/json"
        }

        llama_system_prompt = (
            f"You are an AI tasked with creating incremental goals to accomplish an overall task. The current state of the page is described by a JSON dictionary and a screenshot. "
            f"Generate a clear, actionable next step that progresses towards the overall goal. If the previous goal wasn't met, make the new goal simpler and achievable.\n\n"
            f"Overall goal: {self.overall_goal}\n"
            f"Current goal: {current_goal}\n"
            f"Previous goals: {previous_goals}\n"
            f"currentPageDict= {current_screen_json}"
        )

        llama_user_prompt = (
            f"Review the current JSON dictionary and image of the page and create the next actionable goal that can be achieved. Ensure it is clear enough for an action function to follow.\n"
        )
        
        payload = {
            "model": "meta-llama/llama-3.2-90b-vision-instruct",
            "messages": [
                {"role": "system", "content": llama_system_prompt},
                {"role": "user", "content": llama_user_prompt}
            ],
            "image": encoded_image,
            "temperature": 0.5  # Slight randomness for diverse goal suggestions
        }

        response = requests.post(self.verification_agent.base_url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def run(self, overall_goal):
        """Main function to run the mother agent loop."""
        current_goal = self.create_initial_goal(overall_goal)
        goal_completed = False
        attempt_count = 0

        while not goal_completed and attempt_count < self.goal_attempts:
            self.log_goal(f"Attempt {attempt_count + 1} - Current goal: {current_goal}")
            current_screen_json, screenshot_path = self.verification_agent.retrieve_json()

            # Run the action function here (not implemented in this sample)
            # action_result = run_action_function(current_goal)

            # For now, assume the action was taken; check if the goal was met
            result = self.verification_agent.double_check_agent("Expected state after: " + current_goal)

            if result == "true":
                self.completed_goals.append(current_goal)
                self.log_goal(f"Goal achieved: {current_goal}")
                if current_goal == overall_goal:
                    goal_completed = True
                    break
                else:
                    current_goal = self.generate_next_goal(current_screen_json, screenshot_path, current_goal, self.completed_goals)
            else:
                attempt_count += 1
                if attempt_count < self.goal_attempts:
                    self.log_goal(f"Goal not achieved. Generating a simpler goal.")
                    current_goal = self.generate_next_goal(current_screen_json, screenshot_path, current_goal, self.completed_goals)

        if not goal_completed:
            self.log_goal("Failed to achieve the goal after multiple attempts.")
            raise Exception("Goal not achieved after maximum retry attempts.")

# Example usage
if __name__ == "__main__":
    mother_agent = MotherAgent()
    mother_agent.run("Type 'hello' in the search bar and click submit")