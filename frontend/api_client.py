import requests


def get_answer(message: str, user_id: int) -> str:
    """
    Sends a GET request to retrieve an answer from the API.

    :param message: User message intended for the API.
    :param user_id: Telegram user ID for context.
    :return: A string containing the API's response or an error message.
    """
    url = "http://api:8000/answer"
    params = {
        "message": message,
        "user_id": str(user_id)
    }  # Query parameters

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()["response"]
        return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except:
        return "Ich kann mich gerade nicht mit der API verbinden."


def get_all_morning_messages() -> str:
    """
    Retrieves all morning messages from the API.

    :return: A list of morning messages or an error message.
    """
    url = "http://api:8000/morning"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results
        return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except requests.RequestException:
        return "Ich kann mich gerade nicht mit der API verbinden."


def get_all_proactivity_messages() -> str:
    """
    Retrieves all proactivity messages from the API.

    :return: A list of proactivity messages or an error message.
    """
    url = "http://api:8000/proactivity"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])
            return results
        return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except requests.RequestException:
        return "Ich kann mich gerade nicht mit der API verbinden."


def get_preferences(user_id: int) -> tuple:
    """
    Retrieves user preferences from the API.

    :param user_id: Telegram user ID.
    :return: A tuple containing preferences or an error message, and a status string.
    """
    url = f"http://api:8000/preferences/{user_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json(), "success"
        return (
            f"{response.status_code}: Fehler bei der Anzeige der Präferenzen.",
            "error"
        )
    except:
        return "Ich kann gerade deine Präferenzen nicht abrufen.", "error"


def post_preferences(user_id: int, preferences: dict) -> str:
    """
    Submits initial user preferences to the API.

    :param user_id: Telegram user ID.
    :param preferences: Dict containing user preferences collected from the user.
    :return: A confirmation message or an error message in German.
    """
    url = "http://api:8000/preferences/init"
    data = {
        "username": str(user_id),
        "course": "IN22",
        "cafeteria": preferences.get("canteen", ""),
        "city": preferences.get("city", ""),
        "preferred_transport_medium": preferences.get("transport", ""),
        "stocks": preferences.get("stocks", []),
        "news": preferences.get("news", [])
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return "Deine Präferenzen wurden erfolgreich gespeichert."
        return f"{response.status_code}: Fehler bei der Anfrage an die API."
    except:
        return "Du hast deine Präferenzen anscheinend schon initialisiert."


def put_preference(user_id: int, key: str, new_value):
    """
    Updates a particular user preference in the API.

    :param user_id: Telegram user ID.
    :param key: Preference name being updated.
    :param new_value: New value for the preference.
    :return: A confirmation message or an error message in German.
    """
    url = f"http://api:8000/preferences/{user_id}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return (
                f"Fehler beim Abrufen der aktuellen Präferenzen: "
                f"{response.status_code}"
            )

        current_data = response.json()
        extra_keys = [
            "delete_stocks",
            "add_stocks",
            "delete_news",
            "add_news"
        ]

        if key not in current_data and key not in extra_keys:
            return f"Ungültige Präferenz: {key}"

        current_data[key] = new_value
        put_response = requests.put(url, json=current_data)

        if put_response.status_code == 200:
            return "Deine Präferenz wurde erfolgreich aktualisiert."
        return f"Fehler bei der Aktualisierung: {put_response.status_code}"
    except requests.RequestException:
        return "Ich kann gerade deine Präferenz nicht ändern."