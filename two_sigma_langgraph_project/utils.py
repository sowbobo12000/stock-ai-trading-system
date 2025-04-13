
"""
Utility functions for factor analysis
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def calculate_rolling_returns(returns, window=5):
    return (1 + returns).rolling(window).apply(lambda x: np.prod(x) - 1)

def exponential_weights(n, decay_factor=0.94):
    weights = np.power(decay_factor, np.arange(n - 1, -1, -1))
    return weights / weights.sum()

def orthogonalize_returns_rolling(target, base_factors, lookback_period=63, decay_factor=0.94):
    orthogonal_returns = pd.Series(index=target.index)
    weights = exponential_weights(lookback_period, decay_factor)

    for i in range(lookback_period, len(target)):
        y = target.iloc[i - lookback_period:i]
        X = base_factors.iloc[i - lookback_period:i]
        model = LinearRegression()
        model.fit(X, y, sample_weight=weights)
        current_X = base_factors.iloc[i:i+1]
        predicted = model.predict(current_X)
        orthogonal_returns.iloc[i] = target.iloc[i] - predicted[0]
    return orthogonal_returns
