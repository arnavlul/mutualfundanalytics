# Mutual Fund Analytics Platform - Data Dictionary

This document provides a comprehensive reference of all tables, columns, data types, business definitions, and sources in the normalized star schema.

The database is built on a **Star Schema** architecture optimized for analytics, queries, and dashboard reporting. It consists of **2 Dimension tables** and **6 Fact tables**.

---

## Table of Contents
1. [dim_fund](#1-dim_fund-dimension)
2. [dim_date](#2-dim_date-dimension)
3. [fact_nav](#3-fact_nav-fact)
4. [fact_transactions](#4-fact_transactions-fact)
5. [fact_performance](#5-fact_performance-fact)
6. [fact_portfolio](#6-fact_portfolio-fact)
7. [fact_aum](#7-fact_aum-fact)
8. [fact_sip_industry](#8-fact_sip_industry-fact)

---

## 1. `dim_fund` (Dimension)
Stores static descriptive information about the 40+ mutual fund schemes tracked in the database.
* **Source:** `01_fund_master.csv`
* **Primary Key:** `amfi_code`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Association of Mutual Funds in India (AMFI) unique identifier code. | `119551` |
| `fund_house` | TEXT | The Asset Management Company (AMC) managing the fund. | `SBI Mutual Fund` |
| `scheme_name` | TEXT | Full official name of the mutual fund scheme. | `SBI Bluechip Fund - Regular Plan - Growth` |
| `category` | TEXT | High-level asset class category. | `Equity`, `Debt` |
| `sub_category` | TEXT | Specific investment category style. | `Large Cap`, `Small Cap`, `Gilt`, `Liquid` |
| `plan` | TEXT | Distinguishes whether the fund is a Direct or Regular plan. | `Direct` or `Regular` |
| `launch_date` | TEXT | The date on which the mutual fund scheme was opened. | `YYYY-MM-DD` (`2006-02-14`) |
| `benchmark` | TEXT | The target index the fund performance is benchmarked against. | `NIFTY 100 TRI` |
| `expense_ratio_pct` | REAL | The annual fees charged by the scheme as a % of assets. | `1.54` (denotes 1.54%) |
| `exit_load_pct` | REAL | Penalty fee charged if an investor redeems shares early. | `1.0` (denotes 1.0%) |
| `fund_manager` | TEXT | Name of the primary portfolio manager of the fund. | `Sohini Andani` |
| `risk_category` | TEXT | SEBI-defined risk profile of the fund. | `Moderate`, `High`, `Very High`, `Low` |
| `sebi_category_code`| TEXT | Internal SEBI standard code for categorization. | `EC01` (Equity Large Cap), `EC03` (Equity Small Cap) |

---

## 2. `dim_date` (Dimension)
A generated calendar date lookup table used to link all transaction, portfolio, NAV, and performance timeframes.
* **Source:** Generated automatically during ETL based on date ranges of the input datasets.
* **Primary Key:** `date`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | The calendar day. | `YYYY-MM-DD` (`2024-01-01`) |
| `year` | INTEGER | The calendar year. | `2024` |
| `month` | INTEGER | The calendar month number (1-12). | `1` (January) |
| `quarter` | INTEGER | The calendar quarter (1-4). | `1` (Q1) |
| `is_weekday` | INTEGER | Binary flag indicating if the date is a business day (Mon-Fri). | `1` (Yes), `0` (No/Weekend) |

---

## 3. `fact_nav` (Fact)
Stores daily Net Asset Value (NAV) history for all mutual fund schemes.
* **Source:** `02_nav_history.csv` (cleaned with forward-filled holidays and weekends)
* **Composite Primary Key:** `(amfi_code, date)`
* **Foreign Keys:** 
  * `amfi_code` references `dim_fund(amfi_code)`
  * `date` references `dim_date(date)`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Fund identifier code. | `119551` |
| `date` | TEXT | Date of the NAV valuation. | `YYYY-MM-DD` (`2022-01-03`) |
| `nav` | REAL | Net Asset Value (price per unit) in Indian Rupees (INR). | `54.3856` |
| `daily_return_pct` | REAL | Calculated percentage change in NAV from the prior day (computed in Day 4). | `0.15` (denotes 0.15%) |

---

## 4. `fact_transactions` (Fact)
Stores transactions made by individual retail investors in various mutual fund schemes.
* **Source:** `08_investor_transactions.csv` (cleaned and validated)
* **Primary Key:** `tx_id` (Autoincremented)
* **Foreign Keys:**
  * `amfi_code` references `dim_fund(amfi_code)`
  * `transaction_date` references `dim_date(date)`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `tx_id` | INTEGER | Autoincrementing unique identifier for each transaction. | `1` |
| `investor_id` | TEXT | Unique identifier for the individual investor. | `INV003054` |
| `amfi_code` | INTEGER | Code of the fund in which the transaction took place. | `119092` |
| `transaction_date` | TEXT | Date the transaction was processed. | `YYYY-MM-DD` (`2024-01-01`) |
| `transaction_type` | TEXT | Category of transaction (Systematic Investment Plan, Lumpsum, or Redemption). | `SIP`, `Lumpsum`, `Redemption` |
| `amount_inr` | REAL | Total money value of the transaction in Indian Rupees. | `1834.0` |
| `state` | TEXT | State of residence of the investor. | `Telangana` |
| `city` | TEXT | City of residence of the investor. | `Hyderabad` |
| `city_tier` | TEXT | AMFI classification of the city size. | `T30` (Top 30 cities), `B30` (Beyond 30 cities) |
| `age_group` | TEXT | Demographics bucket of the investor. | `18-25`, `26-35`, `36-45`, `46-55`, `56+` |
| `gender` | TEXT | Gender of the investor. | `Male`, `Female` |
| `annual_income_lakh`| REAL | Annual income of the investor in Lakhs (100,000s) of INR. | `77.1` (represents 7,710,000 INR) |
| `payment_mode` | TEXT | Medium through which payment was processed. | `UPI`, `Net Banking`, `Cheque`, `Mandate` |
| `kyc_status` | TEXT | Know Your Customer verification status. | `Verified`, `Pending` |

---

## 5. `fact_performance` (Fact)
Stores consolidated performance and risk metrics calculated for each mutual fund scheme.
* **Source:** `07_scheme_performance.csv` (validated)
* **Primary Key:** `amfi_code`
* **Foreign Keys:**
  * `amfi_code` references `dim_fund(amfi_code)`
  * `as_of_date` references `dim_date(date)`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Fund identifier code. | `119551` |
| `as_of_date` | TEXT | Date at which these metrics were calculated. | `YYYY-MM-DD` (`2026-05-31`) |
| `return_1yr_pct` | REAL | Absolute return generated by the fund over the last 1 year. | `12.42` (denotes 12.42%) |
| `return_3yr_pct` | REAL | 3-year Compound Annual Growth Rate (CAGR). | `12.36` (denotes 12.36%) |
| `return_5yr_pct` | REAL | 5-year Compound Annual Growth Rate (CAGR). | `14.45` (denotes 14.45%) |
| `benchmark_3yr_pct` | REAL | Annualized 3-year return generated by the fund's benchmark index. | `11.49` (denotes 11.49%) |
| `alpha` | REAL | Under/over-performance of the fund relative to its benchmark. | `0.87` (positive is outperformance) |
| `beta` | REAL | Volatility relative to the market (1.0 means moves with index). | `0.89` (lower beta implies lower volatility) |
| `sharpe_ratio` | REAL | Risk-adjusted return measure (return per unit of volatility). | `0.88` (higher is better) |
| `sortino_ratio` | REAL | Risk-adjusted return measuring excess return per unit of downside risk. | `1.29` (higher is better) |
| `std_dev_ann_pct` | REAL | Annualized standard deviation of daily returns (volatility measure). | `14.0` (denotes 14.0%) |
| `max_drawdown_pct` | REAL | Maximum peak-to-trough drop in NAV value historically. | `-21.7` (denotes -21.7%) |
| `aum_crore` | REAL | Size of the specific fund scheme assets in Crores (10,000,000s) INR. | `14288.0` (142,880,000,000 INR) |
| `morningstar_rating`| INTEGER | Performance/Quality rating out of 5 stars. | `4` |
| `risk_grade` | TEXT | Qualitative assessment of the fund's volatility grade. | `Moderate`, `High`, `Very High`, `Low` |

---

## 6. `fact_portfolio` (Fact)
Stores top equity stock holdings for each equity mutual fund scheme.
* **Source:** `09_portfolio_holdings.csv`
* **Composite Primary Key:** `(amfi_code, stock_symbol, date)`
* **Foreign Keys:**
  * `amfi_code` references `dim_fund(amfi_code)`
  * `date` references `dim_date(date)`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | Fund identifier code. | `119551` |
| `stock_symbol` | TEXT | Stock symbol/ticker on national exchanges (NSE/BSE). | `POWERGRID`, `HDFCBANK` |
| `weight_pct` | REAL | Percentage of the fund's total assets invested in this stock. | `13.85` (denotes 13.85%) |
| `sector` | TEXT | Industry sector of the stock. | `Utilities`, `Banking`, `Pharma` |
| `date` | TEXT | Valuation date of the portfolio disclosure. | `YYYY-MM-DD` (`2025-12-31`) |

---

## 7. `fact_aum` (Fact)
Stores quarterly assets under management (AUM) trends grouped by fund houses (AMCs).
* **Source:** `03_aum_by_fund_house.csv`
* **Composite Primary Key:** `(fund_house, date)`
* **Foreign Keys:**
  * `date` references `dim_date(date)`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `fund_house` | TEXT | Asset Management Company name. | `SBI Mutual Fund` |
| `date` | TEXT | The final calendar date of the quarter. | `YYYY-MM-DD` (`2022-03-31`) |
| `aum_crore` | REAL | Total assets managed by this AMC in Crores of INR. | `605000.0` (6.05 Lakh Crore INR) |
| `num_schemes` | INTEGER | Total number of schemes offered by this AMC in that quarter. | `186` |

---

## 8. `fact_sip_industry` (Fact)
Stores industry-wide aggregate monthly SIP trends.
* **Source:** `04_monthly_sip_inflows.csv`
* **Primary Key:** `month`

| Column Name | SQLite Data Type | Business Definition | Sample / Format |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | Calendar month for the trend. | `YYYY-MM` (`2022-01`) |
| `sip_inflow_crore` | REAL | Total nationwide SIP inflows for that month in Crores INR. | `11517.0` |
| `active_sip_accounts_crore`| REAL | Number of active SIP accounts in Crores. | `4.91` (49,100,000 accounts) |
| `new_sip_accounts_lakh`| REAL | Number of new SIP accounts registered that month in Lakhs. | `9.1` (910,000 accounts) |
| `sip_aum_lakh_crore` | REAL | Cumulative industry assets managed under SIP plans in Lakh Crores. | `4.8` |
| `yoy_growth_pct` | REAL | Month-on-month Year-over-Year (YoY) percentage growth in SIP inflows. | `12.5` (denotes 12.5%) |
