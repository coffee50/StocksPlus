import yfinance as yf
from datetime import datetime


def fetch_data(tickers, start_date, end_date=None):
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    print(f"Fetching for ticker(s) {tickers} from {start_date} to {end_date}.")

    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

        if data.empty:
            print(f"Couldn't load ticker data for ticker(s) {tickers}. Maybe it doesn't exist?")
            return None

        print("Data loaded.")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None