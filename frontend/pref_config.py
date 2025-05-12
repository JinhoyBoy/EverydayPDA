# Define conversation flow states
(
    CANTEEN,
    CITY,
    TRANSPORT,
    STOCKS,
    NEWS
) = range(5)

# Define states for preference updates
(
    BUTTON,
    CANTEEN_UPDATE,
    CITY_UPDATE,
    TRANSPORT_UPDATE,
    STOCKS_DELETE,
    STOCKS_ADD,
    NEWS_DELETE,
    NEWS_ADD
) = range(5, 13)

# Categories for news and transport
NEWS_CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology"
]

TRANSPORT_CATEGORIES = [
    "driving-car",
    "cycling-regular",
    "foot-walking",
]