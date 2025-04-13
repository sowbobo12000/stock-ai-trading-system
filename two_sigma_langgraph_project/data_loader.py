
"""
Factor return data loading using yfinance
"""
import yfinance as yf
import pandas as pd

def get_factor_data(tickers_dict, start_date, end_date):
    all_data = None
    for factor, ticker in tickers_dict.items():
        try:
            ticker_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not ticker_data.empty and 'Close' in ticker_data.columns:
                returns = ticker_data['Close'].pct_change()
                if all_data is None:
                    all_data = pd.DataFrame(index=returns.index)
                all_data[factor] = returns
                print(f"Successfully downloaded {factor} ({ticker})")
            else:
                print(f"Warning: No data for {factor} ({ticker})")
        except Exception as e:
            print(f"Error downloading {factor} ({ticker}): {str(e)}")
    return all_data.dropna() if all_data is not None else None
