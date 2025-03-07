import pandas as pd
import xgboost as xgb

# 데이터 로드
df = pd.read_parquet("data/time_series/time_series_data.parquet")
X = df[["ema_20", "ema_50", "rsi", "macd", "volume"]]

# 모델 로드
model = xgb.XGBRegressor()
model.load_model("models/tree_based/xgb_model.json")

# 예측
predictions = model.predict(X)
print(predictions)
