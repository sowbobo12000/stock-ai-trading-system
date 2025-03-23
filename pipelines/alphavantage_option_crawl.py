import json
import os
import requests
import json
from datetime import datetime, date, timedelta

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
# Specify a date to retrieve options data for any trading day in the past 15+ years (since 2008-01-01)
# https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&date=2017-11-15&apikey=demo

def get_option_data(symbol, date):
    url = f"https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol={symbol}&date={date}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

# from date since 2008-01-01 to today get SPY and QQQ into file
start_date = date(2008, 1, 1)
end_date = date.today()
delta = end_date - start_date

for symbol in ["SPY", "QQQ"]:
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        data = get_option_data(symbol, day)
        with open(f"../data/{symbol}/{day}.json", "w") as f:
            json.dump(data, f)
