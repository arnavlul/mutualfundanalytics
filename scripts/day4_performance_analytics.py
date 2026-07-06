import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import sqlite3
import os
import nbformat as nbf

# Ensure output directories exist
os.makedirs('reports', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('notebooks', exist_ok=True)

# 1. Connect to DB and Load Data
print("Connecting to DB and loading data...")
conn = sqlite3.connect('db/bluestock_mf.db')

nav = pd.read_sql('SELECT * FROM fact_nav', conn)
fund = pd.read_sql('SELECT * FROM dim_fund', conn)

nav['date'] = pd.to_datetime(nav['date'])
nav = nav.sort_values(['amfi_code', 'date'])

# Task 1: Compute daily returns
print("Task 1: Computing daily returns...")
nav['prev_nav'] = nav.groupby('amfi_code')['nav'].shift(1)
nav['daily_return_pct'] = nav['nav'] / nav['prev_nav'] - 1

# Annualised return (1+R).prod()^(252/n) - 1
returns_computed = []
for code, group in nav.groupby('amfi_code'):
    r = group['daily_return_pct'].dropna()
    n = len(r)
    if n > 0:
        ann_ret = (1 + r).prod() ** (252/n) - 1
    else:
        ann_ret = np.nan
    returns_computed.append({'amfi_code': code, 'annualised_return': ann_ret})
    
pd.DataFrame(returns_computed).to_csv('data/processed/returns_computed.csv', index=False)

# Task 2: Calculate CAGR
print("Task 2: Calculating CAGR...")
cagr_data = []
for code, group in nav.groupby('amfi_code'):
    group = group.sort_values('date')
    if len(group) == 0:
        continue
    nav_end = group['nav'].iloc[-1]
    
    def get_cagr(years):
        start_date = group['date'].iloc[-1] - pd.DateOffset(years=years)
        start_group = group[group['date'] <= start_date]
        if len(start_group) == 0:
            return np.nan
        nav_start = start_group['nav'].iloc[-1]
        n_trading_days = len(group[group['date'] > start_group['date'].iloc[-1]])
        if n_trading_days == 0: return np.nan
        return (nav_end / nav_start) ** (252 / n_trading_days) - 1
        
    cagr_data.append({
        'amfi_code': code,
        'cagr_1yr': get_cagr(1),
        'cagr_3yr': get_cagr(3),
        'cagr_5yr': get_cagr(5)
    })
cagr_df = pd.DataFrame(cagr_data)
cagr_df.to_csv('data/processed/cagr_report.csv', index=False)

# Task 3: Compute Sharpe Ratio
print("Task 3: Computing Sharpe...")
rf = 0.065
sharpe_data = []
for code, group in nav.groupby('amfi_code'):
    r = group['daily_return_pct'].dropna()
    if len(r) > 0:
        mean_ret = r.mean() * 252
        std_ret = r.std() * np.sqrt(252)
        sharpe = (mean_ret - rf) / std_ret if std_ret > 0 else np.nan
    else:
        sharpe = np.nan
    sharpe_data.append({'amfi_code': code, 'sharpe': sharpe, 'std_dev_ann': std_ret})
sharpe_df = pd.DataFrame(sharpe_data)
sharpe_df.to_csv('data/processed/sharpe_values.csv', index=False)

# Task 4: Compute Sortino Ratio
print("Task 4: Computing Sortino...")
sortino_data = []
for code, group in nav.groupby('amfi_code'):
    r = group['daily_return_pct'].dropna()
    if len(r) > 0:
        mean_ret = r.mean() * 252
        downside = r[r < 0]
        downside_std = downside.std() * np.sqrt(252)
        sortino = (mean_ret - rf) / downside_std if downside_std > 0 else np.nan
    else:
        sortino = np.nan
    sortino_data.append({'amfi_code': code, 'sortino': sortino})
pd.DataFrame(sortino_data).to_csv('data/processed/sortino_values.csv', index=False)

# Task 5: Alpha & Beta vs benchmark (Nifty 100)
print("Task 5: Computing Alpha & Beta...")
benchmarks = pd.read_csv('data/processed/clean_benchmark_indices.csv')
benchmarks['date'] = pd.to_datetime(benchmarks['date'])
nifty100 = benchmarks[benchmarks['index_name'] == 'NIFTY100'][['date', 'close_value']].rename(columns={'close_value': 'nifty_close'})
nifty100['nifty_ret'] = nifty100['nifty_close'].pct_change()

alpha_beta_data = []
for code, group in nav.groupby('amfi_code'):
    merged = pd.merge(group, nifty100, on='date', how='inner').dropna(subset=['daily_return_pct', 'nifty_ret'])
    if len(merged) > 10:
        slope, intercept, r, p, se = stats.linregress(merged['nifty_ret'], merged['daily_return_pct'])
        alpha = intercept * 252
        beta = slope
    else:
        alpha, beta = np.nan, np.nan
    alpha_beta_data.append({'amfi_code': code, 'alpha': alpha, 'beta': beta})
alpha_beta_df = pd.DataFrame(alpha_beta_data)
alpha_beta_df.to_csv('data/processed/alpha_beta.csv', index=False)

# Task 6: Compute Maximum Drawdown
print("Task 6: Computing Max Drawdown...")
max_dd_data = []
for code, group in nav.groupby('amfi_code'):
    group = group.sort_values('date')
    if len(group) == 0: continue
    running_max = group['nav'].cummax()
    drawdown = group['nav'] / running_max - 1
    max_dd = drawdown.min()
    max_dd_data.append({'amfi_code': code, 'max_drawdown': max_dd})
max_dd_df = pd.DataFrame(max_dd_data)
max_dd_df.to_csv('data/processed/max_drawdown.csv', index=False)

# Task 7: Build Fund Scorecard
print("Task 7: Building Scorecard...")
metrics = fund[['amfi_code', 'expense_ratio_pct']].merge(cagr_df, on='amfi_code')
metrics = metrics.merge(sharpe_df, on='amfi_code')
metrics = metrics.merge(alpha_beta_df, on='amfi_code')
metrics = metrics.merge(max_dd_df, on='amfi_code')

metrics['rank_3yr'] = metrics['cagr_3yr'].rank(ascending=True)
metrics['rank_sharpe'] = metrics['sharpe'].rank(ascending=True)
metrics['rank_alpha'] = metrics['alpha'].rank(ascending=True)
metrics['rank_expense'] = metrics['expense_ratio_pct'].rank(ascending=False)
metrics['rank_max_dd'] = metrics['max_drawdown'].rank(ascending=True) # less negative is better

metrics['score'] = (
    0.30 * metrics['rank_3yr'] +
    0.25 * metrics['rank_sharpe'] +
    0.20 * metrics['rank_alpha'] +
    0.15 * metrics['rank_expense'] +
    0.10 * metrics['rank_max_dd']
)
metrics['score'] = (metrics['score'] / metrics['score'].max()) * 100
metrics.to_csv('data/processed/fund_scorecard.csv', index=False)

# Task 8: Benchmark comparison chart
print("Task 8: Benchmark comparison chart...")
top5 = metrics.nlargest(5, 'score')['amfi_code'].tolist()
plt.figure(figsize=(12, 6))
start_date = nav['date'].max() - pd.DateOffset(years=3)

# Plot Nifty 50 and Nifty 100
nifty50 = benchmarks[benchmarks['index_name'] == 'NIFTY50'][['date', 'close_value']].rename(columns={'close_value': 'nifty50'})
nifty100 = benchmarks[benchmarks['index_name'] == 'NIFTY100'][['date', 'close_value']].rename(columns={'close_value': 'nifty100'})
b_merged = pd.merge(nifty50, nifty100, on='date', how='inner')
b_merged = b_merged[b_merged['date'] >= start_date].sort_values('date')
if not b_merged.empty:
    plt.plot(b_merged['date'], b_merged['nifty50'] / b_merged['nifty50'].iloc[0], label='NIFTY 50', color='black', linewidth=2, linestyle='--')
    plt.plot(b_merged['date'], b_merged['nifty100'] / b_merged['nifty100'].iloc[0], label='NIFTY 100', color='grey', linewidth=2, linestyle='--')

for code in top5:
    g = nav[(nav['amfi_code'] == code) & (nav['date'] >= start_date)].sort_values('date')
    name = fund[fund['amfi_code'] == code]['scheme_name'].iloc[0]
    if not g.empty:
        plt.plot(g['date'], g['nav'] / g['nav'].iloc[0], label=f"{name[:20]}...")

plt.title('Top 5 Funds vs Benchmarks (3 Years, Normalized to 1)')
plt.xlabel('Date')
plt.ylabel('Growth of 1 Unit')
plt.legend()
plt.grid(True)
plt.savefig('reports/benchmark_chart.png')
plt.close()

# Generate Notebook
print("Generating Notebook...")
nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Day 4: Fund Performance Analytics"),
    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect('../db/bluestock_mf.db')
nav = pd.read_sql('SELECT * FROM fact_nav', conn)
nav['date'] = pd.to_datetime(nav['date'])
fund = pd.read_sql('SELECT * FROM dim_fund', conn)"""),
    nbf.v4.new_markdown_cell("## Scorecard Preview"),
    nbf.v4.new_code_cell("""scorecard = pd.read_csv('../data/processed/fund_scorecard.csv')
scorecard.nlargest(10, 'score')"""),
    nbf.v4.new_markdown_cell("## Benchmark Chart"),
    nbf.v4.new_code_cell("""from IPython.display import Image
Image(filename='../reports/benchmark_chart.png')""")
]

with open('notebooks/04_performance_analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Done!")
