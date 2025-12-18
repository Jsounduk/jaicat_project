import requests

class NewsService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/top-headlines?"

    def get_news(self, category="general", country="us"):
        url = f"{self.base_url}country={country}&category={category}&apiKey={self.api_key}"
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            headlines = [article['title'] for article in news_data['articles']]
            return headlines[:5]  # Limit to top 5 news articles
        else:
            return "Unable to fetch news at the moment."
