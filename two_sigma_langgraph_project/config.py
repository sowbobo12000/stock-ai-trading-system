
# -*- coding: utf-8 -*-
"""
Configuration and constants
"""
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

start_date = '2014-01-01'
end_date = '2024-12-31'

factor_tickers = {
    'Global_Equity': 'ACWI',
    'Interest_Rates': 'IEF',
    'US_IG_Bond': 'LQD',
    'US_HY_Bond': 'HYG',
    'EU_IG_Bond': 'IEAC.L',
    'EU_HY_Bond': 'IHYG.L',
    'Commodities': 'DBC',
    'EM_Equity': 'EEM',
    'EM_Bond': 'EMB',
    'EM_Currency': 'CEW',
    'Volatility': 'PBP',
    'Inflation_Bond': 'TIP'
}
