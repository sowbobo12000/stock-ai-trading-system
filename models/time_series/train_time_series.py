import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 데이터 로드
df = pd.read_parquet("data/time_series/time_series_data.parquet")

# 시계열 모델 학습
model = ExponentialSmoothing(df["close"]).fit()
df["forecast"] = model.forecast(steps=10)

# 저장
df.to_csv("data/time_series/forecast.csv", index=False)
