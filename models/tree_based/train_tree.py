import pandas as pd
import xgboost as xgb

# 데이터 로드
df = pd.read_parquet("data/time_series/time_series_data.parquet")
X = df[["ema_20", "ema_50", "rsi", "macd", "volume"]]
y = df["close"]

# 모델 학습
model = xgb.XGBRegressor(objective="reg:squarederror")
model.fit(X, y)

# 저장
model.save_model("models/tree_based/xgb_model.json")
