PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekday INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER,
    date TEXT,
    nav REAL NOT NULL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    as_of_date TEXT NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (as_of_date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_portfolio (
    amfi_code INTEGER,
    stock_symbol TEXT,
    weight_pct REAL NOT NULL,
    sector TEXT,
    date TEXT NOT NULL,
    PRIMARY KEY (amfi_code, stock_symbol, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    fund_house TEXT,
    date TEXT,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER,
    PRIMARY KEY (fund_house, date),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

CREATE INDEX IF NOT EXISTS idx_fact_nav_amfi_date ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_amfi_date ON fact_transactions(amfi_code, transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_portfolio_amfi_date ON fact_portfolio(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_fact_performance_date ON fact_performance(as_of_date);
CREATE INDEX IF NOT EXISTS idx_fact_aum_date ON fact_aum(date);
