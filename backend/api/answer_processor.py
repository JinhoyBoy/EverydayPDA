import os
import sys
import traceback
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.usecase_handler import UseCaseHandler
from api.summary_generator import UserSummaryGenerator
from api.database_utils import get_all_users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnswerProcessor:
    """
    A class to process user messages and generate responses, morning summaries, and proactive suggestions.
    """

    # Process User Message
    #
    # Parameters:
    #   - message (str): The user's input message, e.g., "What's the weather like?"
    #   - user_id (str): Unique identifier for the user, e.g., "user123"
    #
    # Returns:
    #   - dict: Processed response based on the user's message, e.g., {"response": "It's sunny in Stuttgart."}
    async def get_answer(self, message: str, user_id: str):
        use_cases, info = await UseCaseHandler().get_use_cases_and_info(message, user_id)
        logger.info(f"Use Cases: {use_cases}, Info: {info}")
        api_data = UseCaseHandler().call_apis(use_cases, info)
        logger.info(f"API Data: {api_data}")
        response = UseCaseHandler().get_response(message, api_data)
        logger.info(f"Response: {response}")
        return {"response": response}

    # Generate Morning Summaries
    #
    # Parameters:
    #   - None
    #
    # Returns:
    #   - dict: Morning summaries for all users, e.g., {"results": [{"user_id": "user123", "response": "Good morning!"}]}
    async def get_morning(self):
        user_ids = await get_all_users()
        results = []

        for record in user_ids:
            user_id = record['username']
            try:
                result = await UserSummaryGenerator().get_user_morning(user_id)
                results.append({"user_id": user_id, "response": result["response"]})
            except Exception as e:
                results.append({"user_id": user_id, "response": f"Error: {str(e)}"})

        return {"results": results}

    # Generate Proactive Suggestions
    #
    # Parameters:
    #   - None
    #
    # Returns:
    #   - dict: Proactive suggestions for all users, e.g., {"results": [{"user_id": "user123", "response": "Hey, did you know..."}]}
    async def get_proactivity(self):
        user_ids = await get_all_users()
        results = []

        for record in user_ids:
            user_id = record['username']
            try:
                result = await UserSummaryGenerator().get_user_proactivity(user_id)
                results.append({"user_id": user_id, "response": result["response"]})
            except Exception as e:
                results.append({"user_id": user_id, "response": f"Error: {str(e)}\nTraceback:\n{traceback.format_exc()}"})

        return {"results": results}