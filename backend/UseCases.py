from enum import Enum
from service_fetchers.stock_service import get_stock_price
from service_fetchers.news_service import get_news
from service_fetchers.weather_service import get_weather
from service_fetchers.canteen_service import get_canteen_info
from service_fetchers.rapla_service import get_rapla_schedule
from service_fetchers.traveltime_service import get_travel_info
from service_fetchers.hotel_service import get_hotels
from service_fetchers.flight_service import get_flights

class UseCases(Enum):
    STOCKS = (1, "Stock Market Information", ["Stock-Name"], get_stock_price)
    NEWS = (2, "Latest News Updates", ["News-Topic"], get_news)
    WEATHER = (3, "Weather Forecasts", ["City"], get_weather)
    CAFETERIA = (4, "Canteen Menu", ["Canteen-Name"], get_canteen_info)
    TIMETABLE = (5, "Rapla-Class-Schedule", ["Date"], get_rapla_schedule)
    TRAVEL_TIME = (6, "Traveltime", ["Transport-Medium", "Start-Location", "Destination-Location"], get_travel_info)
    HOTEL_SEARCH = (7, "Hotel Booking", ["Hotel-Destination", "Check-in-Date", "Check-out-Date"], get_hotels)
    FLIGHT_INFORMATION = (8, "Flight Information", ["Start-Airport", "Destination-Airport", "Departure-Date", "Return-Date"], get_flights)


    def __new__(cls, value, description, information_needed, func):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value, description, information_needed, func):
        self._value_ = value
        self.description = description
        self.information_needed = information_needed
        self.func = func