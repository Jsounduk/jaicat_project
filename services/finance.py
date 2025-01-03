import requests

class FinanceService:
    def __init__(self):
        self.api_key = "IVNDXIMRJTU38ZPF"
        self.base_url = "https://www.alphavantage.co/query?"

    def get_stock_price(self, symbol):
        url = f"{self.base_url}function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={self.api_key}"
        response = requests.get(url)
        data = response.json()
        if "Time Series (1min)" in data:
            latest_data = next(iter(data["Time Series (1min)"].values()))
            return latest_data["1. open"]
        else:
            return "Unable to fetch stock price."
