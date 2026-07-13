import pandas as pd
import numpy as np

import os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)


nav_history_df = pd.read_csv("data/raw/02_nav_history.csv")

# Converting to datetime
nav_history_df["date"]  = pd.to_datetime(nav_history_df["date"])

# Removing Duplicates
nav_history_df = nav_history_df.drop_duplicates(subset=['amfi_code', 'date'])

# Sorting
nav_history_df = nav_history_df.sort_values(by=['amfi_code', 'date'])

# Forward Filling
nav_history_df['nav'] = nav_history_df.groupby('amfi_code')['nav'].ffill()

# Checking if any nav <= 0
invalid_nav_count = (nav_history_df['nav'] <= 0).sum()

if invalid_nav_count:
    print(f"{invalid_nav_count} entries have invalid NAV values. Dropping them.")
    nav_history_df = nav_history_df[nav_history_df['nav'] > 0]
    print("Invalid NAVs dropped, saving processed data")

else:
    print("No invalid NAV values, saving processed data")
    
nav_history_df.to_csv("data/processed/clean_nav_history.csv", index=False)                                          