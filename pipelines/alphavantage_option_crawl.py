import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import pandas_market_calendars as mcal
import pytz
import requests

API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

# Configure logging to record successes, skips, and failures
logging.basicConfig(
    filename='download_options.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Get the repository root directory
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_option_data(symbol, date_str):
    url = (
        f'https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol={symbol}'
        f'&date={date_str}&apikey={API_KEY}&datatype=csv'
    )
    response = requests.get(url)
    response.raise_for_status()
    content = response.content
    # Check if the response is JSON with an "Information" field indicating an error (like rate limits)
    try:
        json_data = response.json()
        if "Information" in json_data:
            raise Exception(f"API Error: {json_data['Information']}")
        elif json_data == {}:
            raise Exception("API Error: Empty response")
    except ValueError:
        # Not JSON, so likely valid CSV data
        pass
    return content

# Define the start date for data collection
# Calculate start date as 7 business days before today
us_eastern = pytz.timezone('America/New_York')
now_et = datetime.now(us_eastern)
market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
today_str = now_et.strftime('%Y-%m-%d')

# Get NYSE calendar and valid trading days
nyse = mcal.get_calendar('NYSE')
valid_days = nyse.valid_days(start_date=(now_et - pd.Timedelta(days=14)).strftime('%Y-%m-%d'), end_date=today_str)

# Get the date 7 business days before today
if len(valid_days) >= 7:
    start_date_dt = valid_days[-7]
else:
    start_date_dt = valid_days[0]

start_date = start_date_dt.strftime('%Y-%m-%d')
print(f"Using start_date: {start_date}")

# Determine current US Eastern Time and adjust for market open hours
us_eastern = pytz.timezone('America/New_York')
now_et = datetime.now(us_eastern)
market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
today_str = now_et.strftime('%Y-%m-%d')

# Get NYSE calendar and valid trading days up to today
nyse = mcal.get_calendar('NYSE')
valid_days = nyse.valid_days(start_date=start_date, end_date=today_str)

# Determine appropriate end_date:
# If market hasn't opened yet on a valid trading day, use the previous valid day.
if now_et < market_open_time and pd.Timestamp(today_str) in valid_days:
    end_date_dt = valid_days[-2]
else:
    end_date_dt = valid_days[-1]

end_date = end_date_dt.strftime('%Y-%m-%d')
print(f"Using end_date: {end_date}")

def process_symbol(symbol):
    # Use absolute path from repository root
    directory = os.path.join(REPO_ROOT, "data", "raw", "options", symbol)
    os.makedirs(directory, exist_ok=True)

    # Get valid trading days up to the determined end_date
    valid_days_for_symbol = nyse.valid_days(start_date=start_date, end_date=end_date)

    for trading_day in valid_days_for_symbol:
        date_str = trading_day.strftime("%Y-%m-%d")
        file_path = os.path.join(directory, f"{date_str}.csv")

        # If the file already exists, skip downloading it
        if os.path.exists(file_path):
            logging.info(f"SKIPPED: {symbol} on {date_str} - file already exists.")
            print(f"Skipped {symbol} on {date_str} (file exists).")
            continue

        try:
            data = get_option_data(symbol, date_str)
            with open(file_path, "wb") as f:
                f.write(data)
            logging.info(f"SUCCESS: Saved data for {symbol} on {date_str}")
            print(f"Saved data for {symbol} on {date_str}")
        except Exception as e:
            logging.error(f"FAILED: {symbol} on {date_str}: {e}")
            print(f"Error fetching data for {symbol} on {date_str}: {e}")

# Use ThreadPoolExecutor to process symbols in parallel
symbols = ['QQQ', 'SPY', 'NFLX']
with ThreadPoolExecutor() as executor:
    executor.map(process_symbol, symbols)
