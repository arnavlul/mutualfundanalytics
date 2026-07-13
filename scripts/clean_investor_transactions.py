import pandas as pd

import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)


df = pd.read_csv("data/raw/08_investor_transactions.csv")

print(f"Transaction types in data:\n{df['transaction_type'].unique()}")
print(f"KYC_Status types in data:\n{df['kyc_status'].unique()}")

# Unique value in both are valid
# Standardising them
df['transaction_type'] = df['transaction_type'].str.strip().str.capitalize().replace({'Sip' : 'SIP'})
df['kyc_status'] = df['kyc_status'].str.strip().str.capitalize()


# Removing invalid amounts
invalid_amount = (df['amount_inr'] <= 0).sum()
if invalid_amount:
    print(f"{invalid_amount} entries have invalid amounts, dropping them")
    df = df[df['amount_inr'] > 0]

# Standardising date
df['transaction_date'] = pd.to_datetime(df['transaction_date'])


print(f"All changes done, saving to processed directory.")
df.to_csv("data/processed/clean_investor_transactions.csv", index=False)