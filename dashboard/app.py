import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Bluestock MF Analytics", layout="wide")

st.title("Bluestock Mutual Fund Analytics Platform")
st.markdown("Interactive alternative dashboard to Power BI/Tableau.")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@st.cache_data
def load_data():
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'data', 'db', 'bluestock_mf.db'))
    fund_df = pd.read_sql("SELECT * FROM dim_fund", conn)
    perf_df = pd.read_sql("SELECT * FROM fact_performance", conn)
    return fund_df, perf_df

try:
    fund, perf = load_data()
    
    # Merge data
    df = pd.merge(fund, perf, on="amfi_code")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_category = st.sidebar.multiselect("Select Category", df['category'].unique(), default=df['category'].unique())
    selected_risk = st.sidebar.multiselect("Select Risk Grade", df['risk_category'].unique(), default=df['risk_category'].unique())
    
    filtered_df = df[(df['category'].isin(selected_category)) & (df['risk_category'].isin(selected_risk))]
    
    st.subheader("Fund Performance Overview")
    st.dataframe(filtered_df[['scheme_name', 'category', 'risk_category', 'return_3yr_pct', 'sharpe_ratio', 'alpha']].sort_values('sharpe_ratio', ascending=False))
    
    # Top 5 by Sharpe
    st.subheader("Top 5 Funds by Sharpe Ratio")
    top5 = filtered_df.nlargest(5, 'sharpe_ratio')
    st.bar_chart(top5.set_index('scheme_name')['sharpe_ratio'])
    
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.info("Make sure you run the app from the dashboard folder so the relative paths resolve correctly.")
