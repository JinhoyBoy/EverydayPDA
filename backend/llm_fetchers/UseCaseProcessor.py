import ast
import sys
import os

# Append parent directory to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UseCases import UseCases
from Informations import Informations
from llm_fetchers.ChatGPTProcessor import ChatGPTProcessor

from pydantic import BaseModel
from typing import List, Dict


class UseCaseSelection(BaseModel):
    """
    Pydantic model to specify selected use cases.
    """
    use_case_ids: List[int]  # List of IDs corresponding to selected use cases


class ExtractedInformation(BaseModel):
    """
    Pydantic model for representing extracted information.
    """
    info: Dict[str, List[str]]  # Mapping from field names to list of extracted strings


class UseCaseInformation(BaseModel):
    """
    Pydantic model for specific use case information extraction.
    """
    info: str  # Extracted information returned as plain text


class UseCaseProcessor(ChatGPTProcessor):
    """
    Processor that extends ChatGPTProcessor to handle use case and additional 
    information processing via LLM calls.
    """
    def __init__(self):
        # Initialize by calling the parent class constructor.
        super().__init__()

    def parse_response(self, response: str):
        """
        Attempt to parse a string response into a Python literal using ast.literal_eval.
        If parsing fails, return the original string.
        
        :param response: The response string to parse.
        :return: Parsed object or the original string if parsing fails.
        """
        try:
            return ast.literal_eval(response)  # Try to convert the response string into a literal
        except Exception:
            return response  # Return original response if parsing fails

    def declare_usecase(self, user_input: str) -> List[int]:
        """
        Process the user input to select use cases.
        
        :param user_input: User provided input.
        :return: List of integers representing selected use case IDs.
        """
        # Build a comma-separated string of available use cases and their descriptions.
        use_cases = ", ".join(f"{use_case.value}: {use_case.description}" for use_case in UseCases)
        context = (
            f"You are given this user input: {user_input} "
            "If the input isn't in English, internally translate it. "
            f"Available APIs with their IDs are listed here: {use_cases}. "
            "Return a list of numbers corresponding to the APIs mentioned in the user input."
        )
        # Process input with context using structured schema validation.
        structured = self.process_input_with_context(user_input, context, UseCaseSelection)
        valid_ids = [uc.value for uc in UseCases]  # Build a list of valid use case IDs.
        selected_ids = self.parse_response(structured.use_case_ids)  # Parse and extract IDs.
        return [uid for uid in selected_ids if uid in valid_ids]  # Return only valid IDs.

    def get_information(self, user_input: str, information_needed: str) -> dict:
        """
        Retrieve additional information based on required fields from user input.
        
        :param user_input: The user's query.
        :param information_needed: Comma-separated fields expected to be extracted.
        :return: Dictionary mapping each field to a list of extracted strings.
        """
        context = (
            f"These are the required fields: {information_needed}. "
            f"Here's the user input: {user_input}. "
            "If the input isn't in English, internally translate it. "
            "Return a dictionary where each key is one of the fields, and the value is a list of strings provided in the input."
            "Usually the information provided is a single word"
            "If the value isn't provided always return ['']. Never return the whole question. Only return the dictionary."  
        )
        # Process input and extract information using the schema.
        structured = self.process_input_with_context(user_input, context, ExtractedInformation)
        return self.parse_response(structured.info)

    def extract_specific_information(self, user_input: str, information_needed: str) -> dict:
        """
        Extract a single plain text string for specific information from user input.
        
        :param user_input: The user's query.
        :param information_needed: Required field(s) to extract.
        :return: Extracted information as plain text, or empty string if not found.
        """
        context = (
            f"These are the required fields: {information_needed}. "
            f"Here's the user input: {user_input}. "
            "If the input isn't in English, internally translate it. "
            "Only return the single plain text string with the extracted information. Please try as hard as possbile to categories it but of course if nothing is found, return an empty string." 
        )
        # Process input to extract specific information.
        structured = self.process_input_with_context(user_input, context, UseCaseInformation)
        parsed_info = self.parse_response(structured.info)
        # Ensure the extracted data is a plain string.
        if isinstance(parsed_info, str):
            extracted = parsed_info.strip()
            # Build a list of allowed words based on Informations.
            allowed = [word for info in Informations for word in info.value]
            extracted_lower = extracted.lower()
            # Check if any allowed word is present in the extracted string.
            for word in allowed:
                if word.lower() in extracted_lower:
                    return word  # Return the first matching allowed word.
        return ""

    def response(self, user_input: str, api_calls: str) -> str:
        """
        Generate a plain-text response based on user input and API call information.
        
        :param user_input: The user's query.
        :param api_calls: Combined results from API calls.
        :return: A plain text response matching the user input language.
        """
        prompt = (
            f"Here is the information provided by the API calls: {api_calls}. "
            f"And here is the prompt by the user: {user_input}. "
            "Ensure the response is provided in plain text and in the same language as the user input."
        )
        return self.process_input(prompt)


if __name__ == "__main__":
    # Example test input for UseCaseProcessor.
    user_input = "Gebe mir bitte die neusten Nachrichten zu Aktien. und ich möchte wissen, wie ich zur Arbeit komme nach Stuttgart?"
    user_input = "Was gibt es neues in Gesundheit?"  # Overriding previous input for testing
    information_needed = "Stocks, News Services, City, Cafeteria Name, Course Name, Transport Medium, Destination, Check-in Date, Check-out Date, Departure Date, Return Date"
    #information_needed_extracted = "driving-car, driving-hgv, cycling-regular, cycling-road, cycling-mountain, cycling-electric, foot-walking, foot-hiking, wheelchair"

    # Instantiate the UseCaseProcessor.
    processor = UseCaseProcessor()
    use_case = processor.declare_usecase(user_input)
    info = processor.get_information(user_input, information_needed)
    
    # If use case with ID 2 is selected, extract news topic information.
    if 2 in use_case:
        news_topic_options = ", ".join(Informations.NEWS_CATEGORY.value)
        news_topic = processor.extract_specific_information(user_input, news_topic_options)
        if news_topic:
            info["News-Topic"] = [news_topic]
    else:
        news_topic = ""
    
    # If use case with ID 6 is selected, extract travel medium information.
    if 6 in use_case:
        travel_medium_options = ", ".join(Informations.TRAVEL_MEDIUM.value)
        travel_medium = processor.extract_specific_information(user_input, travel_medium_options)
        if travel_medium:
            info["Transport-Medium"] = [travel_medium]
    else:
        travel_medium = ""

    print(use_case)  # e.g., [1, 5]
    print(info)      # e.g., {'Stocks': [''], 'News Services': [''], 'City': [''], 'Cafeteria Name': [''], 'Course Name': [''], 'Transport Medium': [''], 'Destination': [''], 'Check-in Date': [''], 'Check-out Date': [''], 'Departure Date': [''], 'Return Date': ['']}
    print(news_topic, travel_medium)  # e.g., 'driving-car'