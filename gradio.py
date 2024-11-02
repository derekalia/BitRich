from gradio_client import Client, handle_file
import os
import logging
from dotenv import load_dotenv
from huggingface_hub import login

# Login with your token to ensure authentication
#login(token = os.getenv("HUGGING_FACE_HUB_TOKEN"))

class GradioAPI:
    _instance = None

    def __new__(cls):
        """Ensures only one instance of GradioAPI exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(GradioAPI, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initializes the GradioAPI instance."""
        load_dotenv()
        #self.api_key = os.getenv("OPENROUTERAPIKEY")
        self.huggingFaceToken = os.getenv("HUGGING_FACE_HUB_TOKEN")
        self.client = Client.duplicate("derekalia/OmniParser2", hf_token= self.huggingFaceToken, sleep_timeout= 40.0)  # Initialize the Gradio client
        #print(self.huggingFaceToken)

        # Configure logging
        logging.basicConfig(
            filename='gradio_api.log', 
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def call_gradio_api(self, image_path):
        """Sends a request to the Gradio API with just the image path."""
        try:
            result = self.client.predict(
                image_input=handle_file(image_path),  # Use handle_file for local file path
                box_threshold=0.05,
                iou_threshold=0.1,
                api_name="/process"
            )
            return result
        except Exception as e:
            logging.error(f"Error calling Gradio API: {e}")
            print(f"Error calling Gradio API: {e}")
            raise

