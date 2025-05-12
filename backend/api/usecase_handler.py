import os
import sys
import asyncio

# Append parent directory to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_fetchers.UseCaseProcessor import UseCaseProcessor
from UseCases import UseCases
from Informations import Informations
from api.data_filler import DataFiller

class UseCaseHandler:
    """
    Handles the processing of user messages to determine use cases, extract required information,
    and interact with APIs to generate responses.
    """

    # Get Use Cases and Information
    #
    # Parameters:
    #   - message (str): User's input message, e.g., "Was gibt es neues?"
    #   - user_id (str): Unique identifier for the user, e.g., "user123"
    #
    # Returns:
    #   - tuple: Contains a list of selected use case IDs and a dictionary of extracted information
    async def get_use_cases_and_info(self, message: str, user_id: str):
        processor = UseCaseProcessor()
        
        # Determine the use cases based on the user's message
        use_cases = processor.declare_usecase(message)
        
        # Collect all required information fields for the selected use cases
        needed_info = ", ".join([
            info for use_case in UseCases if use_case.value in use_cases
            for info in use_case.information_needed
        ])
        
        # Extract the required information from the user's message
        info = processor.get_information(message, needed_info)

        # Handle specific use cases (e.g., news topics or travel mediums)
        if 2 in use_cases:  # News use case
            news_topic_options = ", ".join(Informations.NEWS_CATEGORY.value)
            news_topic = processor.extract_specific_information(message, news_topic_options)
            if news_topic:
                info["News-Topic"] = [news_topic]
        if 6 in use_cases:  # Travel use case
            travel_medium_options = ", ".join(Informations.TRAVEL_MEDIUM.value)
            travel_medium = processor.extract_specific_information(message, travel_medium_options)
            if travel_medium:
                info["Transport-Medium"] = [travel_medium]
        
        # Fill in any missing values using the DataFiller
        info = await DataFiller().fill_missing_values(info, user_id)
        return use_cases, info

    # Call APIs for Use Cases
    #
    # Parameters:
    #   - use_cases (list[int]): List of selected use case IDs, e.g., [1, 2]
    #   - info (dict): Extracted information required for API calls, e.g., {"City": ["Stuttgart"]}
    #
    # Returns:
    #   - dict: Results from the API calls, keyed by use case descriptions
    #
    # Raises:
    #   - KeyError: If required information for a use case is missing
    def call_apis(self, use_cases, info):
        results = {}
        for uc_id in use_cases:
            use_case = UseCases(uc_id)
            
            # Check for missing required information
            missing = [key for key in use_case.information_needed if key not in info]
            if missing:
                raise KeyError(f"Missing keys {missing} for {use_case.name}")
            
            # Prepare arguments for the use case function
            args = [info[key] for key in use_case.information_needed]
            
            # Call the use case function and store the result
            results[use_case.description] = use_case.func(*args)
        return results

    # Generate Response
    #
    # Parameters:
    #   - message (str): User's input message, e.g., "Was gibt es neues?"
    #   - api_data (str): Combined results from API calls, e.g., "Stock prices: ..."
    #
    # Returns:
    #   - str: A plain-text response in the same language as the user's input
    def get_response(self, message, api_data):
        return UseCaseProcessor().response(message, api_data)
    
if __name__ == "__main__":
    # Main function for testing the UseCaseHandler
    #
    # Example:
    #   - Input: User message and user ID
    #   - Output: Selected use cases, extracted information, API data, and final response
    async def main():
        handler = UseCaseHandler()
        message = "Was gibt es neues?"
        user_id = "user123"
        
        # Get use cases and extracted information
        use_cases, info = await handler.get_use_cases_and_info(message, user_id)
        print(f"Use Cases: {use_cases}, Info: {info}")
        
        # Call APIs for the selected use cases
        api_data = handler.call_apis(use_cases, info)
        print(f"API Data: {api_data}")
        
        # Generate a response based on the API data
        response = handler.get_response(message, api_data)
        print(f"Response: {response}")

    # Run the main function asynchronously
    asyncio.run(main())