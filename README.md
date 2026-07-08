# Bluestock Mutual Fund Analytics Capstone

## Project Overview
This project is an end-to-end data engineering and analytics platform built for the Indian mutual fund industry. It extracts raw mutual fund data from public sources (AMFI, mfapi.in, NSE/BSE), transforms and cleans it through a robust Python ETL pipeline, loads it into a normalized SQLite star schema, and surfaces key insights via an interactive dashboard.

## Folder Structure
- `data/`: Contains raw CSV downloads and processed datasets.
- `db/`: Stores the `bluestock_mf.db` SQLite database.
- `notebooks/`: Jupyter notebooks containing the step-by-step EDA and performance analytics.
- `scripts/`: Python scripts covering data ingestion, cleaning, metrics calculation, and ETL.
- `sql/`: Schema and query definitions for the database.
- `dashboard/`: Contains the interactive Power BI/Tableau dashboard files.
- `reports/`: Final exported charts, presentation deck, and project report.

## Setup Instructions
1. Clone this repository to your local machine.
2. Ensure you have Python 3.10+ installed.
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
5. Install the required dependencies: `pip install -r requirements.txt`

## Execution Steps for the ETL Pipeline
1. Run data ingestion to fetch from raw sources: `python scripts/data_ingestion.py`
2. Run data cleaning and SQLite loading: `python scripts/load_to_sqlite.py`
3. Generate performance analytics and risk metrics: `python scripts/compute_metrics.py` (or execute the relevant scripts).
4. Launch the dashboard by opening `dashboard/bluestock_mf.pbix`.
