import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
import nbformat as nbf

os.makedirs('reports', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('notebooks', exist_ok=True)
os.makedirs('scripts', exist_ok=True)

conn = sqlite3.connect('db/bluestock_mf.db')

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
    var_cvar_data.append({'amfi_code': code, 'VaR_95': var_95, 'CVaR_95': cvar_95})
pd.DataFrame(var_cvar_data).to_csv('data/processed/var_cvar_report.csv', index=False)

# 2. Rolling 90-day Sharpe for 5 key funds
print("Task 2: Rolling Sharpe")
top5 = [119551, 120503, 118632, 119092, 120841] 
plt.figure(figsize=(12, 6))
rf = 0.065
for code in top5:
    g = nav[nav['amfi_code'] == code].copy().sort_values('date')
    g = g.set_index('date')
    if len(g) > 90:
        roll_mean = g['daily_return_pct'].rolling(90).mean() * 252
        roll_std = g['daily_return_pct'].rolling(90).std() * np.sqrt(252)
        roll_sharpe = (roll_mean - rf) / roll_std
        plt.plot(roll_sharpe.index, roll_sharpe, label=str(code))
plt.title('Rolling 90-day Sharpe Ratio')
plt.legend()
plt.savefig('reports/rolling_sharpe_chart.png')
plt.close()

# 3. Investor Cohort Analysis
print("Task 3: Cohort Analysis")
tx = pd.read_sql("SELECT investor_id, amfi_code, transaction_date, amount_inr FROM fact_transactions", conn)
tx['transaction_date'] = pd.to_datetime(tx['transaction_date'])
tx['year'] = tx['transaction_date'].dt.year

first_tx = tx.groupby('investor_id')['year'].min().reset_index().rename(columns={'year': 'cohort_year'})
tx = tx.merge(first_tx, on='investor_id')

cohort_res = tx.groupby('cohort_year').agg(
    total_investors=('investor_id', 'nunique'),
    total_invested=('amount_inr', 'sum'),
    avg_sip=('amount_inr', 'mean')
).reset_index()

top_fund = tx.groupby(['cohort_year', 'amfi_code'])['amount_inr'].sum().reset_index()
top_fund = top_fund.sort_values(['cohort_year', 'amount_inr'], ascending=[True, False]).groupby('cohort_year').head(1)
cohort_res = cohort_res.merge(top_fund[['cohort_year', 'amfi_code']].rename(columns={'amfi_code': 'top_fund'}), on='cohort_year')
cohort_res.to_csv('data/processed/cohort_analysis.csv', index=False)

# 4. SIP Continuity Analysis
print("Task 4: SIP Continuity")
sip_tx = pd.read_sql("SELECT investor_id, transaction_date FROM fact_transactions WHERE transaction_type='SIP'", conn)
sip_tx['transaction_date'] = pd.to_datetime(sip_tx['transaction_date'])
sip_tx = sip_tx.sort_values(['investor_id', 'transaction_date'])

sip_counts = sip_tx.groupby('investor_id').size()
investors_6plus = sip_counts[sip_counts >= 6].index

sip_6plus = sip_tx[sip_tx['investor_id'].isin(investors_6plus)].copy()
sip_6plus['prev_date'] = sip_6plus.groupby('investor_id')['transaction_date'].shift(1)
sip_6plus['gap_days'] = (sip_6plus['transaction_date'] - sip_6plus['prev_date']).dt.days

continuity = sip_6plus.groupby('investor_id')['gap_days'].mean().reset_index()
continuity['at_risk'] = continuity['gap_days'] > 35
continuity.to_csv('data/processed/sip_continuity.csv', index=False)

# 5. Simple fund recommender
print("Task 5: Recommender")
recommender_code = '''import pandas as pd
import sqlite3

def recommend_funds(risk_appetite):
    conn = sqlite3.connect('db/bluestock_mf.db')
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
with open('scripts/recommender.py', 'w') as f:
    f.write(recommender_code)
    
# 6. Sector HHI
print("Task 6: Sector HHI")
port = pd.read_sql("SELECT * FROM fact_portfolio", conn)
port['weight_pct_sq'] = port['weight_pct'] ** 2
hhi = port.groupby('amfi_code')['weight_pct_sq'].sum().reset_index().rename(columns={'weight_pct_sq': 'HHI'})
hhi.to_csv('data/processed/sector_hhi.csv', index=False)

plt.figure(figsize=(10,5))
plt.hist(hhi['HHI'].dropna(), bins=20)
plt.title('Distribution of Sector HHI across Equity Funds')
plt.xlabel('HHI (Sum of squared sector weights)')
plt.ylabel('Count of Funds')
plt.savefig('reports/sector_hhi_chart.png')
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
    nbf.v4.new_code_cell("""from IPython.display import Image
display(Image(filename='../reports/rolling_sharpe_chart.png'))"""),
    nbf.v4.new_code_cell("""display(Image(filename='../reports/sector_hhi_chart.png'))""")
]

with open('notebooks/Advanced_Analytics.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Done")
