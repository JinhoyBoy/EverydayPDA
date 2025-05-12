from enum import Enum

class Informations(Enum):
    NEWS_CATEGORY = (
        ("Business", "Entertainment", "General", "Health", "Science", "Sports", "Technology"),
        lambda x: x
    )

    TRAVEL_MEDIUM = (
        ("driving-car", "cycling-regular", "foot-walking", "wheelchair"),
        lambda x: x
    )

    def __new__(cls, allowed_values, func):
        obj = object.__new__(cls)
        obj._value_ = allowed_values
        obj.func = func
        return obj