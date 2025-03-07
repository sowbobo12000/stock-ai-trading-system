import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 데이터 로드
df = pd.read_parquet("data/time_series/time_series_data.parquet")

# 모델 불러오기 및 예측
model = ExponentialSmoothing(df["close"]).fit()
forecast = model.forecast(steps=10)
print(forecast)
