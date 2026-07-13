import os
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
