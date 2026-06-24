import pandas as pd
import sqlite3
import os

def load_data_to_sqlite():
    # Relative paths (relative to the notebooks directory)
    db_path = "../db/bluestock_mf.db"
    schema_path = "../sql/schema.sql"
    processed_dir = "../data/processed"
    
    # Ensure db directory exists
    os.makedirs("../db", exist_ok=True)
    
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Initialize schema
    print(f"Reading schema DDL from {schema_path}...")
    with open(schema_path, 'r') as f:
        schema_ddl = f.read()
    
    print("Executing schema DDL...")
    cursor.executescript(schema_ddl)
    conn.commit()
    print("Schema initialized successfully.")
    
    # Helper to check loaded row count
    def check_row_count(table_name):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]

    # Helper to load dataframe into table
    def load_df(df, table_name, if_exists='append'):
        print(f"Loading {len(df)} rows into '{table_name}'...")
        # SQLite handles datetime as string ISO format. Let's make sure date cols are formatted correctly.
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        db_count = check_row_count(table_name)
        print(f"Verify '{table_name}': loaded={len(df)}, DB total={db_count}")
        assert db_count >= len(df), f"Row count mismatch for {table_name}!"

    # 2. Load dim_fund (from clean_fund_master.csv)
    fund_master_path = f"{processed_dir}/clean_fund_master.csv"
    df_fund = pd.read_csv(fund_master_path)
    # Filter to only the columns defined in the SQLite table
    fund_cols = [
        'amfi_code', 'fund_house', 'scheme_name', 'category', 'sub_category', 
        'plan', 'launch_date', 'benchmark', 'expense_ratio_pct', 'exit_load_pct', 
        'fund_manager', 'risk_category', 'sebi_category_code'
    ]
    df_fund = df_fund[fund_cols]
    
    # Clear existing data first to prevent duplicate PK errors on multiple runs
    cursor.execute("DELETE FROM dim_fund")
    load_df(df_fund, 'dim_fund')

    # 3. Load Cleaned Fact Tables
    # Clear existing facts to support clean re-runs
    cursor.execute("DELETE FROM fact_nav")
    cursor.execute("DELETE FROM fact_transactions")
    cursor.execute("DELETE FROM fact_performance")
    cursor.execute("DELETE FROM fact_portfolio")
    cursor.execute("DELETE FROM fact_aum")
    cursor.execute("DELETE FROM fact_sip_industry")
    cursor.execute("DELETE FROM dim_date")
    conn.commit()

    # fact_nav (from clean_nav.csv)
    df_nav = pd.read_csv(f"{processed_dir}/clean_nav.csv")
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    load_df(df_nav, 'fact_nav')

    # fact_transactions (from clean_investor_transactions.csv)
    df_tx = pd.read_csv(f"{processed_dir}/clean_investor_transactions.csv")
    df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
    load_df(df_tx, 'fact_transactions')

    # fact_performance (from clean_scheme_performance.csv)
    df_perf = pd.read_csv(f"{processed_dir}/clean_scheme_performance.csv")
    max_nav_date = df_nav['date'].max().strftime('%Y-%m-%d')
    df_perf['as_of_date'] = max_nav_date
    df_perf = df_perf[[
        'amfi_code', 'as_of_date', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct',
        'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio',
        'std_dev_ann_pct', 'max_drawdown_pct', 'aum_crore', 'morningstar_rating', 'risk_grade'
    ]]
    load_df(df_perf, 'fact_performance')

    # fact_portfolio (from clean_portfolio_holdings.csv)
    df_port = pd.read_csv(f"{processed_dir}/clean_portfolio_holdings.csv")
    df_port['date'] = pd.to_datetime(df_port['portfolio_date'])
    df_port = df_port[['amfi_code', 'stock_symbol', 'weight_pct', 'sector', 'date']]
    load_df(df_port, 'fact_portfolio')

    # fact_aum (from clean_aum.csv)
    df_aum = pd.read_csv(f"{processed_dir}/clean_aum.csv")
    df_aum['date'] = pd.to_datetime(df_aum['date'])
    df_aum = df_aum[['fund_house', 'date', 'aum_crore', 'num_schemes']]
    load_df(df_aum, 'fact_aum')

    # fact_sip_industry (from clean_monthly_sip_inflows.csv)
    df_sip = pd.read_csv(f"{processed_dir}/clean_monthly_sip_inflows.csv")
    load_df(df_sip, 'fact_sip_industry')

    # 4. Generate and load dim_date
    print("Generating Date Dimension (dim_date)...")
    all_dates = pd.concat([
        df_nav['date'],
        df_tx['transaction_date'],
        df_port['date'],
        df_aum['date']
    ]).dropna().unique()
    
    min_date = pd.to_datetime(all_dates).min()
    max_date = pd.to_datetime(all_dates).max()
    print(f"Generating date dimension range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    df_date = pd.DataFrame({'date': date_range})
    df_date['year'] = df_date['date'].dt.year
    df_date['month'] = df_date['date'].dt.month
    df_date['quarter'] = df_date['date'].dt.quarter
    df_date['is_weekday'] = (df_date['date'].dt.weekday < 5).astype(int)
    
    load_df(df_date, 'dim_date')
    
    conn.commit()
    conn.close()
    print("All data loaded successfully to SQLite!")

if __name__ == "__main__":
    load_data_to_sqlite()
