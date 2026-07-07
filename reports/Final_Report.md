# Bluestock Fintech: Mutual Fund Analytics Platform
## Final Project Report

### 1. Executive Summary
The Indian mutual fund industry is growing at an unprecedented pace, managing over ₹81 lakh crore in AUM across 1,908 schemes. However, retail investors often struggle with data fragmentation, making it difficult to compare funds on a risk-adjusted basis or track real performance against benchmark indices. This project delivers an end-to-end analytics platform that ingests raw mutual fund data, cleans and standardizes it through a robust ETL pipeline, and visualizes the key insights in an interactive dashboard.

### 2. Problem Statement
- **Data Fragmentation:** NAV, AUM, SIP flows, and portfolios existed in silos. We unified them into a single SQLite database.
- **Performance Gap:** Investors could not easily compare risk-adjusted metrics. We computed Sharpe, Alpha, Beta, and Sortino ratios to create a standardized Fund Scorecard.
- **No Benchmark Tracking:** We overlaid fund performance against NIFTY 50 and NIFTY 100 to calculate tracking error and alpha.
- **Slow Reporting:** Migrated static monthly PDF reports to a live, self-serve interactive dashboard.

### 3. Data Sources & ETL Pipeline Architecture
The project leverages public APIs and open data sources including AMFI India, mfapi.in, and NSE/BSE indices. 
The ETL architecture strictly followed:
1. **Extract:** Python scripts hitting REST APIs and parsing raw CSVs/TXT files.
2. **Transform:** Pandas handled missing weekend NAVs (forward-filling), parsed dates, and calculated daily returns.
3. **Load:** A highly optimized 5-table Star Schema (dim_fund, dim_date, fact_nav, fact_performance, fact_transactions) built in SQLite.
4. **Analyze:** Complex metrics like Historical VaR, Herfindahl-Hirschman Index (HHI), and cohort segmentation were calculated.

### 4. EDA & Performance Analysis Highlights
- **SIP Growth:** Identified record-breaking inflows reaching ₹31,002 Cr.
- **Top Performers:** The Fund Scorecard (ranking based on 3-year CAGR, Sharpe, Alpha, Expense Ratio, and Max Drawdown) revealed significant variance in risk-adjusted returns between mid-cap and large-cap categories.
- **Risk Profiles:** The Rolling 90-day Sharpe ratio highlighted that small-cap funds suffered massive standard deviations during market corrections compared to stable bluechips.
- **Cohort Behaviors:** Newer investor cohorts (2025) are registering more SIP accounts but with slightly lower average transaction amounts compared to the 2024 cohort.

### 5. Project Limitations & Recommendations
**Limitations:**
- Historical NAV data is anchored to provided API limits and does not account for intra-day trading volatility.
- Investor transaction data is synthetically modeled based on geographic distribution estimates, not real KYC data.

**Recommendations:**
- Automate the ETL pipeline using an orchestrator like Apache Airflow to fetch NAVs daily.
- Expand the recommender algorithm to utilize Modern Portfolio Theory (Markowitz Efficient Frontier) rather than just standalone Sharpe comparisons.
