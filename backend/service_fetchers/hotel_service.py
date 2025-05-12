import requests
from .helpers import is_valid_date

# Hotel Search (Hotellook)
#
# Parameters:
# - city_list (list): City name as first element, e.g. ["Berlin"]
# - checkin_list (list): Check-in date (YYYY-MM-DD, DD.MM.YYYY, DD.MM.YY, DD.MM.), e.g. ["2025-05-10"]
# - checkout_list (list): Check-out date (YYYY-MM-DD, DD.MM.YYYY, DD.MM.YY, DD.MM.), e.g. ["2025-05-12"]
#
# Returns:
# - dict: hotels – contains hotel name as key and:
#     - "price" (float or str): Price per night or "keine Angabe"
#     - "stars" (int or str): Star rating or "keine Angabe"
def get_hotels(city_list, checkin_list, checkout_list):
    city = city_list[0]
    
    # Changing dates into correct format
    check_in = is_valid_date(checkin_list[0])
    check_out = is_valid_date(checkout_list[0])

    url = "https://engine.hotellook.com/api/v2/cache.json"
    params = {
        "location": city,
        "currency": "eur",
        "checkIn": check_in,
        "checkOut": check_out,
        "limit": 3
    }

    response = requests.get(url, params=params)
    hotel_data = response.json()

    if isinstance(hotel_data, dict) and hotel_data.get("errorCode") == 2:
        return {}

    hotels = {}
    for hotel in hotel_data:
        hotels[hotel.get("hotelName")] = {
            "price": hotel.get("priceFrom", "keine Angabe"),
            "stars": hotel.get("stars", "keine Angabe")
        }

    return hotels
