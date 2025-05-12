import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
import time

# Load path to .env file and retrieve API keys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")

# Travel Time (OpenRouteService)
#
# Parameters:
# - transport_medium (list of str): A list containing one of the following:
#   "driving-car", "driving-hgv", "cycling-regular", "cycling-road", "cycling-mountain", "cycling-electric", "foot-walking", "foot-hiking", "wheelchair"
# - start_location (list of str): A list containing the start location name (e.g., "Stuttgart")
# - end_location (list of str): A list containing the destination name (e.g., "Hamburg")
#
# Returns:
# - dict: If successful:
#     - "distance_km" (float): Distance in kilometers
#     - "duration_min" (float): Duration in minutes
#   If error:
#     - "error" (str): Error message
def get_travel_info(transport_medium, start_location, end_location):
    def geocode_location(place):
        geolocator = Nominatim(user_agent="route_planner")
        location = geolocator.geocode(place)
        time.sleep(1)
        if location:
            return [location.longitude, location.latitude]
        return None

    # Use the first element of each list for the calculation
    transport = transport_medium[0]
    start_coords = geocode_location(start_location[0])
    end_coords = geocode_location(end_location[0])

    if not start_coords or not end_coords:
        return {"error": "Ungültiger Start- oder Zielort"}

    url = f"https://api.openrouteservice.org/v2/directions/{transport}/geojson"
    headers = {
        "Authorization": OPENROUTE_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [start_coords, end_coords]
    }

    response = requests.post(url, json=body, headers=headers)
    data = response.json()

    if "features" not in data:
        return {"error": data.get("error", response.text)}

    segment = data["features"][0]["properties"]["segments"][0]
    travel_info = {
        "distance_km": round(segment["distance"] / 1000, 2),
        "duration_min": round(segment["duration"] / 60, 2)
    }

    return travel_info
