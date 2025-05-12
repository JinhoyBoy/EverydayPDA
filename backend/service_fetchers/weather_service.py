import requests
import os
from dotenv import load_dotenv

# Load path to .env file and retrieve API keys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Weather (WeatherAPI)
#
# Parameters:
# - cities (list of str): List of city names (e.g., ["Berlin", "Paris", "New York"])
#
# Returns:
# - dict: Maps each city to a dict with:
#     - "temperature" (float): Current temperature in °C
#     - "feelslike" (float): Feels-like temperature in °C
#     - "max_temp" (float): Forecasted max temperature for the day in °C
#     - "min_temp" (float): Forecasted min temperature for the day in °C
def get_weather(cities):
    weather_cities = {}

    for city in cities:
        url = (
            f"http://api.weatherapi.com/v1/forecast.json"
            f"?key={WEATHER_API_KEY}&q={city}"
        )
        response = requests.get(url)
        condition = response.json()

        if condition.get("error", {}).get("message") == "No matching location found.":
            continue

        weather_cities[city] = {
            "temperature": condition.get("current", {}).get("temp_c"),
            "feelslike": condition.get("current", {}).get("feelslike_c"),
            "max_temp": condition
                .get("forecast", {})
                .get("forecastday", [{}])[0]
                .get("day", {})
                .get("maxtemp_c"),
            "min_temp": condition
                .get("forecast", {})
                .get("forecastday", [{}])[0]
                .get("day", {})
                .get("mintemp_c"),
        }

    return weather_cities
