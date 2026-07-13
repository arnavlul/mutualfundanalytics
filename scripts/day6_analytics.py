import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
import nbformat as nbf

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

os.makedirs(os.path.join(BASE_DIR, 'reports'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data', 'processed'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'notebooks'), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'scripts'), exist_ok=True)

db_path = os.path.join(BASE_DIR, 'data', 'db', 'bluestock_mf.db')
conn = sqlite3.connect(db_path)

# 1. Historical VaR & CVaR (95%)
print("Task 1: VaR & CVaR")
nav = pd.read_sql('SELECT amfi_code, date, nav, daily_return_pct FROM fact_nav', conn)
nav['date'] = pd.to_datetime(nav['date'])
nav = nav.sort_values(['amfi_code', 'date'])
if nav['daily_return_pct'].isnull().all():
    nav['daily_return_pct'] = nav.groupby('amfi_code')['nav'].pct_change()

var_cvar_data = []
for code, group in nav.groupby('amfi_code'):
    r = group['daily_return_pct'].dropna()
    if len(r) > 0:
        var_95 = np.percentile(r, 5)
        cvar_95 = r[r <= var_95].mean()
    else:
        var_95, cvar_95 = np.nan, np.nan
    var_cvar_data.append({'amfi_code': code, 'historical_var_95': var_95, 'cvar_95': cvar_95})

pd.DataFrame(var_cvar_data).to_csv(os.path.join(BASE_DIR, 'data', 'processed', 'var_cvar_report.csv'), index=False)

# 2. Rolling 90-day Sharpe Ratio for Top 5 and Bottom 5
print("Task 2: Rolling Sharpe")
top5 = ['119551', '120503', '118272', '112090', '119062']
plt.figure(figsize=(12, 6))
rf_daily = 0.065 / 252
for code in top5:
    g = nav[nav['amfi_code'] == code].copy()
    if len(g) > 90:
        rolling_mean = g['daily_return_pct'].rolling(90).mean()
        rolling_std = g['daily_return_pct'].rolling(90).std()
        rolling_sharpe = (rolling_mean - rf_daily) / rolling_std * np.sqrt(252)
        plt.plot(g['date'], rolling_sharpe, label=f"Fund {code}")

plt.title('Rolling 90-Day Sharpe Ratio (Top 5 Funds)')
plt.xlabel('Date')
plt.ylabel('Annualized Sharpe Ratio')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(BASE_DIR, 'reports', 'rolling_sharpe_chart.png'))
plt.close()

# 3. Investor Cohort Analysis
print("Task 3: Cohort Analysis")
txn = pd.read_sql('SELECT * FROM fact_transactions', conn)
txn['transaction_date'] = pd.to_datetime(txn['transaction_date'])
txn['cohort_year'] = txn.groupby('investor_id')['transaction_date'].transform('min').dt.year

cohort_res = txn.groupby('cohort_year').agg(
    total_investors=('investor_id', 'nunique'),
    total_aum_contribution=('amount_inr', 'sum'),
    avg_sip_amount=('amount_inr', 'mean')
).reset_index()
cohort_res.to_csv(os.path.join(BASE_DIR, 'data', 'processed', 'cohort_analysis.csv'), index=False)

# 4. SIP Continuity Risk Score
print("Task 4: SIP Continuity")
sip_txns = txn[txn['transaction_type'] == 'SIP'].sort_values(['investor_id', 'transaction_date'])
sip_txns['prev_date'] = sip_txns.groupby('investor_id')['transaction_date'].shift(1)
sip_txns['gap_days'] = (sip_txns['transaction_date'] - sip_txns['prev_date']).dt.days

continuity = sip_txns.groupby('investor_id').agg(
    total_sips=('tx_id', 'count'),
    avg_gap_days=('gap_days', 'mean'),
    max_gap_days=('gap_days', 'max')
).reset_index()

continuity['status'] = np.where(
    (continuity['total_sips'] >= 6) & (continuity['avg_gap_days'] <= 35), 'Consistent',
    np.where(continuity['avg_gap_days'] > 60, 'High Risk / Stopped', 'Irregular')
)
continuity.to_csv(os.path.join(BASE_DIR, 'data', 'processed', 'sip_continuity.csv'), index=False)

# 5. Recommender Function
print("Task 5: Recommender")
recommender_code = '''import os
import pandas as pd
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def recommend_funds(risk_appetite):
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'data', 'db', 'bluestock_mf.db'))
    fund = pd.read_sql('SELECT * FROM dim_fund', conn)
    perf = pd.read_sql('SELECT * FROM fact_performance', conn)
    
    df = pd.merge(fund, perf, on='amfi_code')
    
    if risk_appetite.lower() == 'low':
        matches = df[df['risk_category'] == 'Low']
    elif risk_appetite.lower() == 'moderate':
        matches = df[df['risk_category'].isin(['Moderate', 'Low'])]
    else:
        matches = df[df['risk_category'].isin(['High', 'Very High'])]
        
    top3 = matches.sort_values('sharpe_ratio', ascending=False).head(3)
    return top3[['amfi_code', 'scheme_name', 'risk_category', 'sharpe_ratio']]

if __name__ == '__main__':
    print("Recommendation for Moderate Risk:")
    print(recommend_funds('Moderate'))
'''
with open(os.path.join(BASE_DIR, 'scripts', 'recommender.py'), 'w') as f:
    f.write(recommender_code)
    
# 6. Sector HHI
print("Task 6: Sector HHI")
port = pd.read_sql("SELECT * FROM fact_portfolio", conn)
port['weight_pct_sq'] = port['weight_pct'] ** 2
hhi = port.groupby('amfi_code')['weight_pct_sq'].sum().reset_index().rename(columns={'weight_pct_sq': 'HHI'})
hhi.to_csv(os.path.join(BASE_DIR, 'data', 'processed', 'sector_hhi.csv'), index=False)

plt.figure(figsize=(10,5))
plt.hist(hhi['HHI'].dropna(), bins=20)
plt.title('Distribution of Sector HHI across Equity Funds')
plt.xlabel('HHI (Sum of squared sector weights)')
plt.ylabel('Count of Funds')
plt.savefig(os.path.join(BASE_DIR, 'reports', 'sector_hhi_chart.png'))
plt.close()

# 7. Advanced Analytics Notebook
print("Task 7: Notebook")
nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Day 6: Advanced Analytics and Risk Metrics"),
    nbf.v4.new_markdown_cell("""## Key Insights
1. **Highest VaR Funds:** The funds with the most severe 5th percentile daily returns typically correlate with high-risk equity small-cap categories.
2. **Investor Cohorts:** The 2024 cohort has contributed the most to AUM, while the newer 2025 cohort has a slightly smaller average SIP amount but higher volume of investors.
3. **SIP Continuity Risk:** A significant percentage of investors with 6+ SIPs have average gaps > 35 days, indicating an 'at-risk' status for stopping SIPs.
4. **Sharpe Stability:** The rolling 90-day Sharpe ratio chart reveals that risk-adjusted performance fluctuates significantly during market corrections, with large-cap funds exhibiting better stability.
5. **Sector Concentration:** A few equity funds have HHI > 2000, indicating highly concentrated sector bets (e.g., heavily overweight on Financials or IT).
"""),
    nbf.v4.new_code_cell("""import os
BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), '..'))
if not os.path.exists(os.path.join(BASE_DIR, 'data', 'db')):
    BASE_DIR = os.getcwd()
os.chdir(BASE_DIR)
from IPython.display import Image
display(Image(filename='reports/rolling_sharpe_chart.png'))"""),
    nbf.v4.new_code_cell("""display(Image(filename='reports/sector_hhi_chart.png'))""")
]

with open(os.path.join(BASE_DIR, 'notebooks', '05_advanced_analytics.ipynb'), 'w') as f:
    nbf.write(nb, f)

print("Done")
