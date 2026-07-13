import pandas as pd

import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)


df = pd.read_csv("data/raw/07_scheme_performance.csv")

# Converting all return columns to numeric
return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']

for col in return_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

return_nan_values = 0
for col in return_cols:
    return_nan_values += df[col].isna().sum()

print(f"NaN Return Values: {return_nan_values}\n")

# Flagging Negative Sharpe Ratio
neg_sharpe_ratio = (df['sharpe_ratio'] < 0).sum()
print(f"{neg_sharpe_ratio} entries with negative Sharpe Ratio")


# Checking Expense Ratio
expense_ratio_check = ((df['expense_ratio_pct'] < 0.1) | (df['expense_ratio_pct'] > 2.5)).sum()
print(f"{expense_ratio_check} entries with Expense Ratio < 0.1% or > 2.5 %")

# Saving
df.to_csv("data/processed/clean_scheme_performance.csv", index=False)
