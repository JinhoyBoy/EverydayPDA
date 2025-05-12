from typing import Dict, Optional
import os
import sys
from datetime import date, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.database import get_db_connection

class DataFiller:
    """
    A utility class to fill missing data fields for user inputs using default values or database queries.
    """

    # Fetch Data from Database
    #
    # Parameters:
    #   - key (str): The key for which data needs to be fetched, e.g., "Stock-Name"
    #   - user_id (str): The unique identifier of the user, e.g., "user123"
    #
    # Returns:
    #   - Optional[str]: A list of values fetched from the database for the given key, or None if no data is found
    @staticmethod
    async def __fetch_from_database(key: str, user_id: str) -> Optional[str]:
        query_map = {
            'Stock-Name': "SELECT stock_name FROM stocks s JOIN user_stocks us ON s.s_id = us.s_id JOIN users u ON us.u_id = u.u_id WHERE u.username = $1",
            'News-Topic': "SELECT news_name FROM news n JOIN user_news un ON n.n_id = un.n_id JOIN users u ON un.u_id = u.u_id WHERE u.username = $1",
            'City': "SELECT city FROM users WHERE username = $1",
            'Canteen-Name': "SELECT cafeteria FROM users WHERE username = $1",
            'Transport-Medium': "SELECT preferred_transport_medium FROM users WHERE username = $1",
            'Start_Airpot': "SELECT city FROM users WHERE username = $1",
            'Start_Location': "SELECT city FROM users WHERE username = $1",
        }

        query = query_map.get(key)
        if not query:
            return None

        conn = await get_db_connection()
        try:
            result = await conn.fetch(query, user_id)
            return [record[0] for record in result] if result else None
        finally:
            await conn.close()

    # Get Default Value for Missing Data
    #
    # Parameters:
    #   - key (str): The key for which a default value is needed, e.g., "Check-in-Date"
    #
    # Returns:
    #   - str: The default value for the given key, e.g., "2025-04-15"
    @staticmethod
    def __get_default_value(key: str) -> str:
        default_values = {
            'Destination-Location': 'DHBW Stuttgart',
            'Hotel-Destination': 'Maldives',
            'Destination-Airport': 'Maldives',
            'Check-in-Date': date.today().strftime('%Y-%m-%d'),
            'Check-out-Date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'Departure-Date': date.today().strftime('%Y-%m-%d'),
            'Return-Date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'Date': date.today().strftime('%Y-%m-%d')
        }
        return default_values.get(key)

    # Fill Missing Values in Data
    #
    # Parameters:
    #   - data (Dict[str, str]): A dictionary containing data fields and their values, e.g., {"City": ""}
    #   - user_id (str): The unique identifier of the user, e.g., "user123"
    #
    # Returns:
    #   - Dict[str, str]: The updated dictionary with missing values filled, e.g., {"City": "Stuttgart"}
    async def fill_missing_values(self, data: Dict[str, str], user_id: str) -> Dict[str, str]:
        for key in data:
            if data[key] == "" or data[key] == [""]:
                if key in ['Stock-Name', 'News-Topic', 'City', 'Canteen-Name', 'Transport-Medium', 'Start-Airpot', 'Start-Location']:
                    data[key] = await self.__fetch_from_database(key, user_id) or None
                else:
                    data[key] = self.__get_default_value(key)
        return data