import os
import sys
from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent

def run_script(script_name):
    script_path = BASE_DIR / "scripts" / script_name
    print(f"==================================================")
    print(f"Running: {script_name}...")
    print(f"==================================================")
    result = subprocess.run([sys.executable, str(script_path)], cwd=BASE_DIR / "scripts")
    if result.returncode != 0:
        print(f"Error executing {script_name} (exit code {result.returncode})")
        sys.exit(result.returncode)
    print(f"Finished {script_name} successfully.\n")

def main():
    print("Starting Bluestock Mutual Fund Analytics Master ETL Pipeline...")
    
    # 1. Data Ingestion
    run_script("data_ingestion.py")
    run_script("live_nav_fetch.py")
    
    # 2. Data Cleaning
    run_script("clean_nav_history.py")
    run_script("clean_investor_transactions.py")
    run_script("clean_scheme_performance.py")
    run_script("clean_remaining_datasets.py")
    
    # 3. Load to SQLite
    run_script("load_to_sqlite.py")
    
    # 4. Compute Metrics & Analytics
    run_script("compute_metrics.py")
    run_script("day6_analytics.py")
    
    print("Master ETL Pipeline completed successfully!")

if __name__ == "__main__":
    main()
