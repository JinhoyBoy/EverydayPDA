from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.answer_processor import AnswerProcessor
from api.models import User, UserUpdate
from api.database_utils import (
    init_user_preferences,
    get_user_preferences,
    update_user_preferences,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"]
)

# Process User Message
#
# Parameters:
#   - message (str): The user's input message, e.g., "What's the weather like?"
#   - user_id (str): Unique identifier for the user, e.g., "user123"
#
# Returns:
#   - dict: Processed answer based on the user's message
@app.get("/answer")
async def get_answer(message: str = Query(..., min_length=1), user_id: str = Query(..., min_length=1)):
    """
    Process a user's message and return an answer.
    """
    answer_processor = AnswerProcessor()
    return await answer_processor.get_answer(message, user_id)

# Generate Morning Summaries
#
# Parameters:
#   - None
#
# Returns:
#   - dict: Morning summaries for all users
@app.get("/morning")
async def get_morning():
    """
    Generate morning summaries for all users.
    """
    answer_processor = AnswerProcessor()
    return await answer_processor.get_morning()

# Generate Proactive Suggestions
#
# Parameters:
#   - None
#
# Returns:
#   - dict: Proactive suggestions for all users
@app.get("/proactivity")
async def get_proactivity():
    """
    Generate proactive suggestions for all users.
    """
    answer_processor = AnswerProcessor()
    return await answer_processor.get_proactivity()

# Initialize User Preferences
#
# Parameters:
#   - user (User): User object containing preferences, e.g., {"username": "john_doe", "city": "Stuttgart"}
#
# Returns:
#   - dict: Confirmation of successful initialization
@app.post("/preferences/init")
async def init_preferences(user: User):
    """
    Initialize user preferences in the database.
    """
    return await init_user_preferences(user)

# Retrieve User Preferences
#
# Parameters:
#   - username (str): The username of the user, e.g., "john_doe"
#
# Returns:
#   - User: User object containing preferences, or None if the user does not exist
@app.get("/preferences/{username}", response_model=User)
async def get_preferences(username: str) -> Optional[User]:
    """
    Retrieve user preferences from the database.
    """
    return await get_user_preferences(username)

# Update User Preferences
#
# Parameters:
#   - username (str): The username of the user, e.g., "john_doe"
#   - user (UserUpdate): Object containing updated preferences, e.g., {"city": "Berlin"}
#
# Returns:
#   - dict: Confirmation of successful update
@app.put("/preferences/{username}")
async def update_preferences(username: str, user: UserUpdate):
    """
    Update user preferences in the database.
    """
    return await update_user_preferences(username, user)