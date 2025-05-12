import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Type
from openai import OpenAI


class ChatGPTProcessor:
    """
    Singleton class to process input via the OpenAI GPT-4o-mini model.
    
    This class provides methods to process plain and structured input.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Create a new instance only if one doesn't already exist.
        if cls._instance is None:
            cls._instance = super(ChatGPTProcessor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the ChatGPTProcessor by loading the OpenAI API key.
        Prevent reinitialization if the instance is already initialized.
        """
        if hasattr(self, "_initialized") and self._initialized:
            # Already initialized, so skip reinit.
            return
        # Define the base directory relative to current file location.
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        # Build path to the .env file.
        env_path = os.path.join(BASE_DIR, ".env")
        load_dotenv(env_path)
        # Retrieve OpenAI API key from environment variables.
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found. Please set in .env file.")
        # Set the global OpenAI API key.
        openai.api_key = api_key
        self._initialized = True

    def process_input(self, user_input: str) -> str:
        """
        Process user input using GPT-4o-mini model.
        
        :param user_input: The input string from the user.
        :return: The response content from the model as a string.
        """
        client = OpenAI()
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_input}],
                max_tokens=400
            )
            # Return the content of the first message in the response.
            return response.choices[0].message.content
        except Exception as e:
            # Provide a detailed error message if processing fails.
            raise Exception("Error processing input: " + str(e))

    def process_input_with_context(self, user_input: str, context: str, 
                                   schema: Type[BaseModel]) -> BaseModel:
        """
        Process user input with additional context and parse response into a schema.
        
        :param user_input: The user input string.
        :param context: The system context to assist the model.
        :param schema: Pydantic BaseModel schema to validate the response.
        :return: Instance of the schema with parsed data from the response.
        """
        client = OpenAI()
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_input}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema.__name__,
                        "schema": schema.model_json_schema()
                    }
                }
            )
            parsed_response = response.choices[0].message.parsed
            if not parsed_response:
                # Fallback: use manual parsing if parsed response is empty.
                parsed_response = schema.model_validate_json(response.choices[0].message.content)
            return parsed_response
        except Exception as e:
            # Raise an exception with additional details upon failure.
            raise Exception("Error processing structured input: " + str(e))


if __name__ == "__main__":
    # Instantiate the ChatGPTProcessor singleton.
    processor1 = ChatGPTProcessor()
    processor2 = ChatGPTProcessor()
    # Confirm singleton behavior.
    print(processor1 is processor2)   # This should print True to confirm the singleton behavior.
    
    # Example usage of the process_input method.
    user_input = "Hello, how is the weather today in Stuttgart?"
    response = processor1.process_input(user_input)
    print(response)