import pandas as pd

fund_master = pd.read_csv("../data/raw/01_fund_master.csv")
nav_history = pd.read_csv("../data/raw/02_nav_history.csv")

print(f"\nUnique Fund Houses:\n")
print(fund_master['fund_house'].unique())

print(f"\nUnique Categories:\n")
print(fund_master['category'].unique())


print(f"\nUnique Sub-categories:\n")
print(fund_master['sub_category'].unique())

print(f"Unique Risk Grades:\n")
print(fund_master['risk_category'].unique())

# Validating AMFI COdes
print("\n--- Data Validation ---")
fund_master_codes = fund_master['amfi_code'].unique()
nav_history_codes = nav_history['amfi_code'].unique()

missing_codes = [code for code in fund_master_codes if code not in nav_history_codes]

if len(missing_codes) == 0:
    print(f"All {len(fund_master_codes)} codes in fund_master exist in nav_history")
else:
    print(f"Warning: {len(missing_codes)} codes missing from nav_history\n")
    print(f"Missing Codes: {missing_codes}")