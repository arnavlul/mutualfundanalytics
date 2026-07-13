import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)


os.makedirs('../reports', exist_ok=True)
conn = sqlite3.connect('data/db/bluestock_mf.db')

# 1. NAV Trend Analysis
query = '''SELECT f.scheme_name, n.date, n.nav FROM fact_nav n JOIN dim_fund f ON n.amfi_code = f.amfi_code ORDER BY n.date'''
df_nav = pd.read_sql_query(query, conn)
df_nav['date'] = pd.to_datetime(df_nav['date'])
fig = px.line(df_nav, x='date', y='nav', color='scheme_name', title='NAV Trend Analysis (2022-2026)')
fig.add_vrect(x0="2023-04-01", x1="2023-12-31", fillcolor="green", opacity=0.1, annotation_text="2023 Bull Run")
fig.add_vrect(x0="2024-05-01", x1="2024-07-31", fillcolor="red", opacity=0.1, annotation_text="2024 Corrections")
fig.update_layout(showlegend=False)
fig.write_image('reports/nav_trend.png', width=1000, height=600)

# 2. AUM Growth Bar Chart
df_aum = pd.read_sql_query("SELECT fund_house, date, aum_crore FROM fact_aum", conn)
df_aum['date'] = pd.to_datetime(df_aum['date'])
df_aum['year'] = df_aum['date'].dt.year
df_aum_yearly = df_aum.groupby(['fund_house', 'year'])['aum_crore'].last().reset_index()
plt.figure(figsize=(12, 6))
sns.barplot(data=df_aum_yearly, x='year', y='aum_crore', hue='fund_house')
plt.title('AUM Growth by Fund House (2022-2025)')
plt.ylabel('AUM (Crores INR)')
plt.xlabel('Year')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('reports/aum_growth.png')

# 3. SIP Inflow Time-Series
df_sip = pd.read_sql_query("SELECT month, sip_inflow_crore FROM fact_sip_industry", conn)
df_sip['month'] = pd.to_datetime(df_sip['month'] + '-01')
fig2 = px.line(df_sip, x='month', y='sip_inflow_crore', title='Monthly SIP Inflow Trend (Jan 2022 - Dec 2025)', markers=True)
fig2.add_annotation(x="2025-12-01", y=31002, text="₹31,002 Cr All-Time High", showarrow=True, arrowhead=1)
fig2.write_image('reports/sip_inflow.png', width=1000, height=600)

# 4. Category Inflow Heatmap
df_cat = pd.read_csv('data/processed/clean_category_inflows.csv')
df_cat_heatmap = df_cat.pivot(index='month', columns='category', values='net_inflow_crore')
plt.figure(figsize=(14, 8))
sns.heatmap(df_cat_heatmap.T, cmap='YlGnBu', annot=False)
plt.title('Net Inflow by Category Heatmap')
plt.xlabel('Month')
plt.ylabel('Fund Category')
plt.tight_layout()
plt.savefig('reports/category_heatmap.png')

# 5. Investor Demographics
df_tx = pd.read_sql_query("SELECT age_group, amount_inr, gender FROM fact_transactions WHERE transaction_type='SIP'", conn)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
age_counts = df_tx['age_group'].value_counts()
axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%')
axes[0].set_title('Age Group Distribution')
sns.boxplot(data=df_tx, x='age_group', y='amount_inr', ax=axes[1])
axes[1].set_title('SIP Amount by Age Group')
axes[1].set_yscale('log')
gender_counts = df_tx['gender'].value_counts()
axes[2].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%')
axes[2].set_title('Gender Split')
plt.tight_layout()
plt.savefig('reports/demographics.png')

# 6. Geographic Distribution
df_geo = pd.read_sql_query("SELECT state, city_tier, amount_inr FROM fact_transactions WHERE transaction_type='SIP'", conn)
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
state_amt = df_geo.groupby('state')['amount_inr'].sum().sort_values(ascending=True)
state_amt.plot(kind='barh', ax=axes[0])
axes[0].set_title('Total SIP Amount by State')
tier_counts = df_geo.groupby('city_tier')['amount_inr'].sum()
axes[1].pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%')
axes[1].set_title('T30 vs B30 SIP Contribution')
plt.tight_layout()
plt.savefig('reports/geographic.png')

# 7. Folio Count Growth
df_folio = pd.read_csv('data/processed/clean_industry_folio_count.csv')
fig3 = px.line(df_folio, x=df_folio.columns[0], y=df_folio.columns[-1], title='Mutual Fund Folio Growth (2022-2025)')
fig3.add_annotation(x='2022-01-01', y=13.26, text="13.26 Cr")
fig3.add_annotation(x='2025-12-01', y=26.12, text="26.12 Cr")
fig3.write_image('reports/folio_growth.png', width=1000, height=600)

# 8. NAV Return Correlation Matrix
query_corr = '''
SELECT f.scheme_name, n.date, n.daily_return_pct 
FROM fact_nav n 
JOIN dim_fund f ON n.amfi_code = f.amfi_code 
WHERE f.scheme_name IN (SELECT scheme_name FROM dim_fund LIMIT 10)
'''
df_corr = pd.read_sql_query(query_corr, conn)
df_pivot = df_corr.pivot(index='date', columns='scheme_name', values='daily_return_pct')
plt.figure(figsize=(10, 8))
sns.heatmap(df_pivot.corr(), cmap='coolwarm', annot=True, fmt='.2f')
plt.title('Daily Return Correlation Matrix (Top 10 Funds)')
plt.tight_layout()
plt.savefig('reports/correlation_matrix.png')

# 9. Sector Allocation Donut
df_port = pd.read_sql_query("SELECT sector, weight_pct FROM fact_portfolio", conn)
sector_weights = df_port.groupby('sector')['weight_pct'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(8, 8))
plt.pie(sector_weights, labels=sector_weights.index, autopct='%1.1f%%', wedgeprops=dict(width=0.4))
plt.title('Top 10 Sector Allocation in Equity Funds')
plt.tight_layout()
plt.savefig('reports/sector_allocation.png')

conn.close()
print("Successfully generated all reports!")
