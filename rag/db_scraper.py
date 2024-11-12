import os
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
from decouple import config
from langdetect import detect
import bs4 as bs
import time

# Initialize MongoDB client
mongo_client = MongoClient(config('MONGODB_URI'))
db = mongo_client['financial_data']
news_collection = db['finance_news']

class FinnHubScraper:
    """A class to handle scraping financial news using the FinnHub API and storing it in MongoDB."""

    def __init__(self, start_date="2020-02-10", end_date="2020-03-20", tickers=None):
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        self.finhub_key = config('FINHUB_KEY')
        self.tickers = tickers if tickers else self.get_sp500_tickers()
        self.max_calls = 60
        self.sleep_time = 60
        self.request_count = 0

    def get_sp500_tickers(self):
        """Fetches a list of S&P 500 company symbols."""
        response = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = bs.BeautifulSoup(response.text, 'lxml')
        table = soup.find_all('table')[0]
        tickers = [row.findAll('td')[0].text.strip() for row in table.findAll('tr')[1:]]
        return tickers

    def fetch_news(self, ticker, date):
        """Fetches financial news for a specific ticker and date using the FinnHub API."""
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={date}&to={date}&token={self.finhub_key}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else []

    def store_news(self, news_data):
        """Stores news data in MongoDB after filtering for English-language content."""
        for news in news_data:
            if detect(news['headline']) == 'en':
                news['ticker'] = news['related'] if 'related' in news else ''
                news['date'] = datetime.fromtimestamp(news['datetime']).strftime('%Y-%m-%d')
                news_collection.update_one(
                    {'id': news['id']},
                    {'$set': news},
                    upsert=True
                )

    def scrape_and_store_news(self):
        """Loops through each day between the start and end date for each ticker and stores the data."""
        for ticker in self.tickers:
            date = self.start_date_obj
            while date <= self.end_date_obj:
                self.request_count += 1
                news_data = self.fetch_news(ticker, date.strftime('%Y-%m-%d'))
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

if __name__ == "__main__":
    scraper = FinnHubScraper(start_date="2020-02-10", end_date="2020-03-20", tickers=['AAPL', 'MSFT'])
    scraper.run()
