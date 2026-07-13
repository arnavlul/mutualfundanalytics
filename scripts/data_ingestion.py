import pandas as pd

import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)


def inspect_dataframe(name, df):
    print(f"Loading: {name}")
    print(f"Shape: {df.shape}")
    print("\nData Types:")
    print(df.dtypes)
    print("\nHead (First 5 rows):")
    print(df.head())
    print("-" * 50)

if __name__ == "__main__":
    print("Starting data ingestion from: ../data/raw/\n")
    print("-" * 50)

    # 1. Fund Master
    df_fund_master = pd.read_csv("data/raw/01_fund_master.csv")
    inspect_dataframe("01_fund_master.csv", df_fund_master)

    # 2. NAV History
    df_nav_history = pd.read_csv("data/raw/02_nav_history.csv")
    inspect_dataframe("02_nav_history.csv", df_nav_history)

    # 3. AUM by Fund House
    df_aum_by_fund_house = pd.read_csv("data/raw/03_aum_by_fund_house.csv")
    inspect_dataframe("03_aum_by_fund_house.csv", df_aum_by_fund_house)

    # 4. Monthly SIP Inflows
    df_monthly_sip_inflows = pd.read_csv("data/raw/04_monthly_sip_inflows.csv")
    inspect_dataframe("04_monthly_sip_inflows.csv", df_monthly_sip_inflows)

    # 5. Category Inflows
    df_category_inflows = pd.read_csv("data/raw/05_category_inflows.csv")
    inspect_dataframe("05_category_inflows.csv", df_category_inflows)

    # 6. Industry Folio Count
    df_industry_folio_count = pd.read_csv("data/raw/06_industry_folio_count.csv")
    inspect_dataframe("06_industry_folio_count.csv", df_industry_folio_count)

    # 7. Scheme Performance
    df_scheme_performance = pd.read_csv("data/raw/07_scheme_performance.csv")
    inspect_dataframe("07_scheme_performance.csv", df_scheme_performance)

    # 8. Investor Transactions
    df_investor_transactions = pd.read_csv("data/raw/08_investor_transactions.csv")
    inspect_dataframe("08_investor_transactions.csv", df_investor_transactions)

    # 9. Portfolio Holdings
    df_portfolio_holdings = pd.read_csv("data/raw/09_portfolio_holdings.csv")
    inspect_dataframe("09_portfolio_holdings.csv", df_portfolio_holdings)

    # 10. Benchmark Indices
    df_benchmark_indices = pd.read_csv("data/raw/10_benchmark_indices.csv")
    inspect_dataframe("10_benchmark_indices.csv", df_benchmark_indices)
