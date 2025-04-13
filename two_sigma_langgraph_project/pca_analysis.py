
"""
Principal Component Analysis utilities
"""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run_pca_analysis(returns_data):
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(returns_data)
    pca = PCA()
    pca_result = pca.fit_transform(scaled_data)
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
    return pca, explained_variance_ratio, cumulative_variance_ratio

def analyze_parsimony(factor_returns):
    pca, var_ratio, cum_var = run_pca_analysis(factor_returns)
    n_components_90 = np.where(cum_var >= 0.9)[0][0] + 1
    return {
        "n_components_90": n_components_90,
        "variance_explained": var_ratio,
        "cumulative_variance": cum_var
    }
