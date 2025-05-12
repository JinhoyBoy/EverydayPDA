import requests
import os
from dotenv import load_dotenv

# Load path to .env file and retrieve API keys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# News (NewsAPI)
#
# Parameters:
# - categories (list of str): News categories to query. Must be one or more of:
#     "business", "entertainment", "general", "health", "science", "sports", "technology"
#
# Returns:
# - dict: Maps each category to a list of articles, where each article contains:
#     - "title" (str): Headline of the article
#     - "source" (str): URL of the article
#     - "publishedAt" (str): Publication datetime in ISO format
def get_news(news_topics):
    news = {}

    for news_topic in news_topics:
        url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?category={news_topic}&pageSize=1&apiKey={NEWS_API_KEY}"
        )
        response = requests.get(url)
        articles = response.json().get("articles", [])

        if response.json().get("totalResults") == 0:
            continue

        if news_topic not in news:
            news[news_topic] = []

        # Extracts article title, URL, and publication date
        for article in articles:
            news[news_topic].append({
                "title": article.get("title"),
                "source": article.get("url"),
                "publishedAt": article.get("publishedAt"),
            })

    return news

if __name__ == "__main__":
    # Example usage
    news_topics = ["Business", "Technology"]
    news_data = get_news(news_topics)
    print(news_data)