import pandas as pd
import os

def clean_remaining_datasets():
    df_fund = pd.read_csv("../data/raw/01_fund_master.csv")
    df_fund = df_fund.drop_duplicates()
    for col in df_fund.select_dtypes(include=['object']).columns:
        df_fund[col] = df_fund[col].str.strip()
    fund_nans = df_fund.isna().sum().sum()
    if fund_nans > 0:
        print(f"  Note: Found {fund_nans} NaN values in Fund Master. Keeping them.")
    df_fund.to_csv("../data/processed/clean_fund_master.csv", index=False)

    df_aum = pd.read_csv("../data/raw/03_aum_by_fund_house.csv")
    df_aum = df_aum.drop_duplicates()
    for col in df_aum.select_dtypes(include=['object']).columns:
        df_aum[col] = df_aum[col].str.strip()
    aum_nans = df_aum.isna().sum().sum()
    if aum_nans > 0:
        print(f"  Note: Found {aum_nans} NaN values in AUM by Fund House.")
    df_aum.to_csv("../data/processed/clean_aum.csv", index=False)

    df_sip = pd.read_csv("../data/raw/04_monthly_sip_inflows.csv")
    df_sip = df_sip.drop_duplicates()
    for col in df_sip.select_dtypes(include=['object']).columns:
        df_sip[col] = df_sip[col].str.strip()
    sip_nans = df_sip.isna().sum().sum()
    if sip_nans > 0:
        print(f"  Note: Found {sip_nans} NaN values in Monthly SIP Inflows.")
    df_sip.to_csv("../data/processed/clean_monthly_sip_inflows.csv", index=False)

    df_cat = pd.read_csv("../data/raw/05_category_inflows.csv")
    df_cat = df_cat.drop_duplicates()
    for col in df_cat.select_dtypes(include=['object']).columns:
        df_cat[col] = df_cat[col].str.strip()
    cat_nans = df_cat.isna().sum().sum()
    if cat_nans > 0:
        print(f"  Note: Found {cat_nans} NaN values in Category Inflows.")
    df_cat.to_csv("../data/processed/clean_category_inflows.csv", index=False)

    df_folio = pd.read_csv("../data/raw/06_industry_folio_count.csv")
    df_folio = df_folio.drop_duplicates()
    for col in df_folio.select_dtypes(include=['object']).columns:
        df_folio[col] = df_folio[col].str.strip()
    folio_nans = df_folio.isna().sum().sum()
    if folio_nans > 0:
        print(f"  Note: Found {folio_nans} NaN values in Industry Folio Count.")
    df_folio.to_csv("../data/processed/clean_industry_folio_count.csv", index=False)

    df_port = pd.read_csv("../data/raw/09_portfolio_holdings.csv")
    df_port = df_port.drop_duplicates()
    for col in df_port.select_dtypes(include=['object']).columns:
        df_port[col] = df_port[col].str.strip()
    port_nans = df_port.isna().sum().sum()
    if port_nans > 0:
        print(f"  Note: Found {port_nans} NaN values in Portfolio Holdings.")
    df_port.to_csv("../data/processed/clean_portfolio_holdings.csv", index=False)

    df_bench = pd.read_csv("../data/raw/10_benchmark_indices.csv")
    df_bench = df_bench.drop_duplicates()
    for col in df_bench.select_dtypes(include=['object']).columns:
        df_bench[col] = df_bench[col].str.strip()
    bench_nans = df_bench.isna().sum().sum()
    if bench_nans > 0:
        print(f"  Note: Found {bench_nans} NaN values in Benchmark Indices.")
    df_bench.to_csv("../data/processed/clean_benchmark_indices.csv", index=False)

    print("\nAll remaining datasets cleaned and saved successfully.")

if __name__ == "__main__":
    clean_remaining_datasets()
