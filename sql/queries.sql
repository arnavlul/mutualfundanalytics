SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

SELECT 
    d.year,
    d.month,
    f.scheme_name,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month, f.scheme_name
ORDER BY d.year, d.month;

SELECT 
    t1.month AS current_month,
    t1.sip_inflow_crore AS current_inflow_cr,
    t2.month AS previous_year_month,
    t2.sip_inflow_crore AS previous_inflow_cr,
    ROUND(((t1.sip_inflow_crore - t2.sip_inflow_crore) / CAST(t2.sip_inflow_crore AS REAL)) * 100, 2) AS calculated_yoy_growth_pct,
    t1.yoy_growth_pct AS reported_yoy_growth_pct
FROM fact_sip_industry t1
JOIN fact_sip_industry t2 ON 
    substr(t1.month, 6, 2) = substr(t2.month, 6, 2)
    AND CAST(substr(t1.month, 1, 4) AS INTEGER) = CAST(substr(t2.month, 1, 4) AS INTEGER) + 1
ORDER BY t1.month;

SELECT 
    state,
    COUNT(tx_id) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_transaction_size_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    plan,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

WITH RankedPerformance AS (
    SELECT 
        f.category,
        f.scheme_name,
        p.return_3yr_pct,
        ROW_NUMBER() OVER (PARTITION BY f.category ORDER BY p.return_3yr_pct DESC) as rank
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    WHERE p.return_3yr_pct IS NOT NULL
)
SELECT 
    category,
    scheme_name,
    return_3yr_pct AS cagr_3yr_pct
FROM RankedPerformance
WHERE rank <= 3
ORDER BY category, rank;

SELECT 
    f.scheme_name,
    f.category,
    f.benchmark,
    p.return_3yr_pct AS fund_return_3yr,
    p.benchmark_3yr_pct AS benchmark_return_3yr,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS underperformance_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_3yr_pct < p.benchmark_3yr_pct
ORDER BY underperformance_pct ASC;

SELECT 
    transaction_type,
    COUNT(*) AS tx_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_transactions), 2) AS tx_percentage,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS avg_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY tx_count DESC;

SELECT 
    stock_symbol,
    sector,
    COUNT(DISTINCT amfi_code) AS holding_funds_count,
    ROUND(AVG(weight_pct), 2) AS avg_portfolio_weight_pct,
    ROUND(SUM(weight_pct), 2) AS total_cumulative_weight_pct
FROM fact_portfolio
GROUP BY stock_symbol, sector
ORDER BY total_cumulative_weight_pct DESC
LIMIT 5;

SELECT 
    city_tier,
    COUNT(tx_id) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_investment_inr,
    ROUND(SUM(amount_inr) * 100.0 / (SELECT SUM(amount_inr) FROM fact_transactions), 2) AS investment_share_pct
FROM fact_transactions
WHERE city_tier IS NOT NULL AND city_tier != ''
GROUP BY city_tier;
