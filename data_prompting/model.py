from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv('API_KEY'))

class QueryModel:
    """
    The class that handles GPT-4 model queries and responses.
    """

    def __init__(self, params = None):
        """
        Constructor to initialise model parameters.
        Args:
            params (dict): The parameters of the model in dict format.
        """
        self.params = params or {
            'temperature': 0,
            'max_tokens': 1000,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }

    def __call__(self, model_name, query, image_base64, *args, **kwargs):
        """
        Query the GPT-4 model with text and image input.
            model_name (str): The name of the model
            query (str): The text prompt for the model.
            image_base64 (str): Base64-encoded image string. 
        Returns:
            response_text (str): The response from the model.
        """

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": query,
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url":  f"data:image/jpeg;base64,{image_base64}"
                    },
                    },
                ],
                }
            ],
            **self.params
            )
        
        response_text = response.choices[0].message.content
        
        print(response_text)
        return response_text