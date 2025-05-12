import requests
import os
from dotenv import load_dotenv
from .helpers import is_valid_date

# Load path to .env file and retrieve API keys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# Flight Search (Amadeus API)
#
# Parameters:
#   - origin_city (list[str]): Departure city, e.g. ["Stuttgart"]
#   - destination_city (list[str]): Arrival city, e.g. ["Hamburg"]
#   - departure_date (list[str]): Departure date, format "YYYY-MM-DD", or "DD.MM.YYYY", or "DD.MM.YY"
#   - return_date (list[str], optional): Return date, format "YYYY-MM-DD", or "DD.MM.YYYY", or "DD.MM.YY"
#
# Returns:
#   - dict: Contains flight details (max. 3 flights) or error message
def get_flights(origin_city, destination_city, departure_date, return_date=None):
    def get_access_token(): # Obtain OAuth2 token from Amadeus API.
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json().get("access_token")

    def city_to_iata(city_name, token): # Resolve city name to IATA code via Amadeus location API.
        url = "https://test.api.amadeus.com/v1/reference-data/locations"
        params = {"keyword": city_name, "subType": "AIRPORT"}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        data = response.json()

        if not data.get("data"):
            raise ValueError(f"No IATA code found for city: {city_name}")

        return data["data"][0]["iataCode"]

    try:
        token = get_access_token()
        origin_iata = city_to_iata(origin_city[0], token)
        destination_iata = city_to_iata(destination_city[0], token)
    except Exception as e:
        return {"error": str(e)}

    # Umwandlung der Datumsangaben ins richtige Format
    departure_date = is_valid_date(departure_date[0])
    if return_date:
        return_date = is_valid_date(return_date[0])

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin_iata,
        "destinationLocationCode": destination_iata,
        "departureDate": departure_date,
        "adults": 1,
        "currencyCode": "EUR",
        "max": 3
    }

    if return_date:
        params["returnDate"] = return_date

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {
            "error": f"API request failed: {response.status_code}",
            "details": response.text
        }

    data = response.json()
    if not data.get("data"):
        return {"error": "No flight data available."}

    flights = []
    for flight in data["data"][:3]:
        segment = flight["itineraries"][0]["segments"][0]
        flights.append({
            "flight_number": segment["carrierCode"],
            "airline": segment["carrierCode"],
            "departure": segment["departure"]["at"],
            "arrival": segment["arrival"]["at"],
            "price": flight["price"]["grandTotal"]
        })

    return {"flights": flights}
