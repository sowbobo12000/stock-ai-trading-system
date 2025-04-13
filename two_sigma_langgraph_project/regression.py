
"""
Newey-West adjusted regression and factor regression analysis
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

def run_factor_regression(portfolio_returns, factor_returns):
    aligned_data = pd.concat([portfolio_returns, factor_returns], axis=1).dropna()
    if aligned_data.empty:
        raise ValueError("Aligned data is empty")
    y = aligned_data.iloc[:, 0]
    X = aligned_data.iloc[:, 1:]

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), index=X.index, columns=X.columns)
    X_scaled = sm.add_constant(X_scaled)

    model = sm.OLS(y, X_scaled)
    results = model.fit(cov_type='HAC', cov_kwds={'maxlags': 6})

    t_stats = results.tvalues[1:]
    r_squared = results.rsquared
    return dict(zip(X.columns, t_stats)), r_squared
