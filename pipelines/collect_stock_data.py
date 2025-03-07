import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.download(ticker, start=start_date, end=end_date)
    stock.to_csv(f"data/raw/{ticker}_raw.csv")

# 예제 실행
fetch_stock_data("TSLA", "2024-01-01", "2024-03-01")
