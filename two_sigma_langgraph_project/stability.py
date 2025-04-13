
"""
Factor stability analysis using rolling regression
"""
import pandas as pd
import statsmodels.api as sm

def analyze_factor_stability(factor_data, base_factors, window=21, lag=1):
    loadings = {}
    autocorrelations = {}

    for target in ['Credit', 'Commodities']:
        rolling_betas = pd.DataFrame(index=factor_data.index, columns=base_factors)
        for i in range(window, len(factor_data)):
            y = factor_data[target].iloc[i - window:i]
            X = factor_data[base_factors].iloc[i - window:i]
            model = sm.OLS(y, sm.add_constant(X)).fit()
            rolling_betas.loc[factor_data.index[i], base_factors] = model.params[1:]
        loadings[target] = rolling_betas.astype(float)

        autocorrelations[target] = {
            col: loadings[target][col].dropna().autocorr(lag) for col in base_factors
        }

    return {"rolling_loadings": loadings, "autocorrelations": autocorrelations}
