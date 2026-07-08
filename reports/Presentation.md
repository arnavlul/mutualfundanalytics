# Bluestock Mutual Fund Analytics Platform
**Presentation Deck Content (12 Slides)**

---
### Slide 1: Title Slide
- **Title:** Mutual Fund Analytics Platform
- **Subtitle:** End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard
- **Presenter:** Intern / Data Analyst — Bluestock Fintech

---
### Slide 2: Problem & Objective
- **Problem:** Data fragmentation, lack of risk-adjusted performance comparison, and poor benchmark tracking.
- **Objective:** Build a unified platform to track NAVs, AUM growth, compute complex risk metrics (Sharpe, Beta, VaR), and provide actionable insights via an interactive dashboard.

---
### Slide 3: Data Sources
- **Sources:** AMFI India (NAV, AUM, SIP data), mfapi.in (Historical NAV APIs), NSE/BSE (Benchmark index prices).
- **Volume:** Over 87K+ rows of transaction data, 46K+ NAV history records covering 40 real fund schemes.

---
### Slide 4: System Architecture
- **Extract:** API and CSV ingestion.
- **Transform:** Pandas-driven data cleaning, forward-filling weekends, calculating metrics.
- **Load:** Normalized 5-table SQLite Star Schema.
- **Analyze/Visualize:** Jupyter Notebooks, Power BI.

---
### Slide 5: EDA Highlights (Market Trends)
- **SIP Growth:** Monthly SIP inflows hit an all-time high of ₹31,002 crore in late 2025.
- **AUM Dominance:** Highlighted heavy concentration in large-cap and specific AMC dominances (e.g., SBI Mutual Fund at ₹12.5L Cr).

---
### Slide 6: EDA Highlights (Investor Behavior)
- **Demographics:** Strongest AUM contribution stems from the 2024 investor cohort.
- **Geographic Split:** Clear divergence in transaction volume between T30 (Top 30 cities) and B30 (Beyond 30 cities).

---
### Slide 7: Performance Metrics
- **Methodology:** Standardized calculations using 252 trading days.
- **Key Metrics Computed:** 1yr/3yr/5yr CAGR, Sharpe Ratio, Sortino Ratio, Alpha, Beta, and Maximum Drawdown.

---
### Slide 8: The Fund Scorecard
- **Ranking System:** Funds were objectively ranked out of 100 based on a weighted composite of 3yr CAGR (30%), Sharpe (25%), Alpha (20%), Expense Ratio (15%), and Max Drawdown (10%).

---
### Slide 9: Dashboard Screenshots (Overview)
- *(Insert Screenshot of Page 1: Industry Overview)*
- **Highlights:** Dynamic KPI cards for Total AUM, SIP Inflows, and Schemes.

---
### Slide 10: Dashboard Screenshots (Analytics)
- *(Insert Screenshot of Page 2: Fund Performance)*
- **Highlights:** Scatter plots mapping Return vs. Risk, accompanied by the actionable Fund Scorecard.

---
### Slide 11: Key Findings & Recommendations
- **Findings:** Small-cap funds showed high historical VaR (downside risk), and sector HHI revealed heavy concentration in financial stocks for certain equity funds.
- **Recommendations:** Deploy ETL as an automated daily cron job; integrate Markowitz Efficient Frontier for portfolio optimization.

---
### Slide 12: Thank You
- **Q&A Session**
- **Contact:** Bluestock Fintech
---
