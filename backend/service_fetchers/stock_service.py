import requests
import os
from dotenv import load_dotenv

# Load path to .env file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")        

# Stocks (Twelve Data)
#
# Parameters:
# - stock_names (list of str): Company names (e.g., ["Apple", "Google"])
#
# Returns:
# - dict: Maps each company name to a dict with:
#     - "price" (str): Latest stock price
#     - "timestamp" (str): Datetime of the latest price
#     - "changeFrom1hour" (str): Price change from one hour ago
def get_stock_price(stock_names):
    stocks = {}

    for stock_name in stock_names:
        # Lookup ticker symbol by company name
        search_url = (
            f"https://api.twelvedata.com/symbol_search?symbol={stock_name}&apikey={TWELVE_DATA_API_KEY}"
        )
        response = requests.get(search_url)
        datas = response.json()

        if not datas.get("data"):
            continue  # Skip if no match found

        symbol = None

        for data in datas.get("data", []):
            if data.get("exchange") == "NASDAQ":
                symbol = data.get("symbol")
                break

        # Get latest 1min time series
        url = (
            f"https://api.twelvedata.com/time_series"
            f"?symbol={symbol}&interval=1min&apikey={TWELVE_DATA_API_KEY}"
        )
        response = requests.get(url)
        stock = response.json()

        # Get quote with hourly change
        url = (
            f"https://api.twelvedata.com/quote"
            f"?symbol={symbol}&interval=1h&apikey={TWELVE_DATA_API_KEY}"
        )
        response = requests.get(url)
        stock.update(response.json())

        if response.json().get("code") == 400:
            continue
        else:
            # Filters price, timestamp and hourly change
            stocks[stock_name] = {
                "price": stock.get("values", [{}])[0].get("close"),
                "timestamp": stock.get("values", [{}])[0].get("datetime"),
                "changeFrom1hour": stock.get("change"),
            }

    return stocks

if __name__ == "__main__":
    # Example usage
    stock_names = ["NVIDIA"]
    stock_data = get_stock_price(stock_names)
    print(stock_data)