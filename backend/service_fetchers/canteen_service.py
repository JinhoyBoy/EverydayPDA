import requests
import time
import difflib

# Canteen Info (OpenMensa API)
#
# Parameters:
# - canteen_name (list of str): List of Approximate names of canteens (e.g., ["Mensa Central", "Mensa Hohenheim"])
#
# Returns:
# - dict: Maps each meal name to:
#     - "category" (str): Meal category (e.g., "Vegetarian", "Main dish")
#     - "price" (float or None): Price for students in EUR
#   Returns error message if the canteen is not found or request fails.
def get_canteen_info(canteen_names):
    min_ratio = 0.6

    # Helper function for normalizing names (lowercase and removing special characters)
    def normalize_name(name):
        name = name.lower()
        # Remove any special characters or extra spaces
        name = name.replace(",", "").replace("(", "").replace(")", "")
        return name.strip()

    # Weighted matching function that prioritizes certain keywords
    def weighted_match(name, candidates, min_ratio):
        best_match = None
        highest_score = 0

        for candidate_name, canteen_id in candidates.items():
            # Get base score using normal matching
            score = difflib.SequenceMatcher(None, name, candidate_name).ratio()

            # Weight the score higher if key terms like "Mensa Central" are present
            if "mensa central" in name and "mensa central" in candidate_name:
                score += 0.2  # Add bonus for matching key term "Mensa Central"

            # Update if we find a better match
            if score > highest_score and score >= min_ratio:
                best_match = canteen_id
                highest_score = score

        return best_match

    url = "https://openmensa.org/api/v2/canteens"
    page = 1
    candidates = {}

    while True:
        response = requests.get(url, params={"page": page})
        if response.status_code != 200:
            return {"error": f"Fehler beim Laden der Kantinen: {response.status_code}"}

        canteens = response.json()
        if not canteens:
            break

        # Process each canteen
        for canteen in canteens:
            full_name = f"{canteen.get('name', '')} {canteen.get('city', '')}"
            normalized_name = normalize_name(full_name)
            candidates[normalized_name] = canteen["id"]

        page += 1

    # Prepare the result for each canteen name in the input list
    all_menus = {}

    for canteen_name in canteen_names:
        normalized_input = normalize_name(canteen_name)

        # Find the best match based on the weighted matching
        canteen_id = weighted_match(normalized_input, candidates, min_ratio)
        if not canteen_id:
            all_menus[canteen_name] = {"error": "Kantine nicht gefunden."}
            continue

        date = time.strftime("%Y-%m-%d")  # Todays date with format YYYY-MM-DD

        url = f"https://openmensa.org/api/v2/canteens/{canteen_id}/days/{date}/meals"
        response = requests.get(url)

        if response.status_code != 200:
            all_menus[canteen_name] = {"error": f"Fehler beim Abrufen: {response.status_code}"}
            continue

        meals = {}
        for idx, meal in enumerate(response.json()):
            if idx >= 3:  # Stop after the first 3 meals
                break
            meals[meal.get("name")] = {
                "category": meal.get("category"),
                "price": meal.get("prices", {}).get("students"),
            }

        all_menus[canteen_name] = meals

    return all_menus
