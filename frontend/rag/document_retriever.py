import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decouple import config
from rich import print
from langdetect import detect
import bs4 as bs
import time


class FinnHubScraper:
    """A class to handle scraping financial news using the FinnHub API and storing it in a list."""

    def __init__(self, start_date=None, end_date=None, tickers=None):
        # Set start_date to 7 days ago by default if None is provided
        self.start_date = (
            start_date
            if start_date
            else (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        )
        # Set end_date to today's date if None is provided
        self.end_date = end_date if end_date else datetime.now().strftime("%Y-%m-%d")

        self.start_date_obj = datetime.strptime(self.start_date, "%Y-%m-%d")
        self.end_date_obj = datetime.strptime(self.end_date, "%Y-%m-%d")

        self.finhub_key = config("FINHUB_API_KEY", default=None)
        self.tickers = tickers if tickers else self.get_sp500_tickers()
        self.max_calls = 30
        self.sleep_time = 60
        self.request_count = 0
        self.scraped_news = []  # List to store scraped news articles

    def get_sp500_tickers(self):
        """Fetches a list of S&P 500 company symbols."""
        response = requests.get(
            "http://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        )
        soup = bs.BeautifulSoup(response.text, "lxml")
        table = soup.find_all("table")[0]
        tickers = [row.findAll("td")[0].text.strip() for row in table.findAll("tr")[1:]]
        return tickers

    def fetch_news(self, ticker, date):
        """Fetches financial news for a specific ticker and date using the FinnHub API."""
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={date}&to={date}&token={self.finhub_key}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else []

    def store_news(self, news_data):
        """Stores news data in a list after filtering for English-language content."""
        for news in news_data:
            if detect(news["headline"]) == "en":
                news["ticker"] = news.get("related", "")
                news["date"] = datetime.fromtimestamp(news["datetime"]).strftime(
                    "%Y-%m-%d"
                )
                self.scraped_news.append(
                    news
                )  # Append news to the list instead of storing in a database

    def scrape_and_store_news(self):
        """Loops through each day between the start and end date for each ticker and stores the data in a list."""
        for ticker in self.tickers:
            date = self.start_date_obj
            while date <= self.end_date_obj:
                self.request_count += 1
                news_data = self.fetch_news(ticker, date.strftime("%Y-%m-%d"))
                if news_data:
                    self.store_news(news_data)
                date += timedelta(days=1)

                # Handle rate limiting
                if self.request_count >= self.max_calls:
                    time.sleep(self.sleep_time)
                    self.request_count = 0

    def run(self):
        """Runs the scraping and storage process for all specified tickers."""
        self.scrape_and_store_news()
        return self.scraped_news  # Return the list of scraped news


# if __name__ == "__main__":
# scraper = FinnHubScraper(tickers=['AAPL', 'MSFT'])
# scraped_data = scraper.run()
# print(scraped_data)  # Print the scraped news data
