from pydantic import BaseModel
from typing import Dict, List, Optional

# User Model
#
# Attributes:
#   - username (str): The username of the user, e.g., "john_doe"
#   - course (str): The course the user is enrolled in, e.g., "Computer Science"
#   - cafeteria (str): The user's preferred cafeteria, e.g., "Main Cafeteria"
#   - city (str): The city where the user resides, e.g., "Stuttgart"
#   - preferred_transport_medium (str): The user's preferred mode of transport, e.g., "Car"
#   - stocks (Optional[List[str]]): A list of stock symbols the user is interested in, e.g., ["AAPL", "TSLA"]
#   - news (Optional[List[str]]): A list of news topics the user is interested in, e.g., ["Technology", "Finance"]
class User(BaseModel):
    username: str
    course: str
    cafeteria: str
    city: str
    preferred_transport_medium: str
    stocks: Optional[List[str]] = []
    news: Optional[List[str]] = []

# User Update Model
#
# Attributes:
#   - course (Optional[str]): The updated course of the user, e.g., "Data Science"
#   - cafeteria (Optional[str]): The updated preferred cafeteria, e.g., "North Cafeteria"
#   - city (Optional[str]): The updated city of the user, e.g., "Berlin"
#   - preferred_transport_medium (Optional[str]): The updated preferred mode of transport, e.g., "Bike"
#   - add_stocks (Optional[List[str]]): A list of stock symbols to add to the user's preferences, e.g., ["GOOGL"]
#   - delete_stocks (Optional[List[str]]): A list of stock symbols to remove from the user's preferences, e.g., ["AAPL"]
#   - add_news (Optional[List[str]]): A list of news topics to add to the user's preferences, e.g., ["Sports"]
#   - delete_news (Optional[List[str]]): A list of news topics to remove from the user's preferences, e.g., ["Finance"]
class UserUpdate(BaseModel):
    course: Optional[str] = None
    cafeteria: Optional[str] = None
    city: Optional[str] = None
    preferred_transport_medium: Optional[str] = None
    add_stocks: Optional[List[str]] = []
    delete_stocks: Optional[List[str]] = []
    add_news: Optional[List[str]] = []
    delete_news: Optional[List[str]] = []