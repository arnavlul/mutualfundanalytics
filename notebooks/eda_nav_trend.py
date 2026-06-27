import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

def nav_trend_analysis():
    print("Connecting to database...")
    conn = sqlite3.connect('../db/bluestock_mf.db')
    
    # Query NAV data joined with fund master to get scheme names
    query = """
    SELECT 
        f.scheme_name, 
        n.date, 
        n.nav 
    FROM fact_nav n
    JOIN dim_fund f ON n.amfi_code = f.amfi_code
    ORDER BY n.date
    """
    df = pd.read_sql_query(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    
    print(f"Data loaded: {df.shape[0]} rows.")
    
    # Create the Plotly figure
    fig = px.line(df, x='date', y='nav', color='scheme_name',
                  title='NAV Trend Analysis (2022-2026)',
                  labels={'nav': 'Net Asset Value (INR)', 'date': 'Date', 'scheme_name': 'Scheme Name'})
    
    # Highlight 2023 Bull Run (approx. April 2023 to Dec 2023)
    fig.add_vrect(
        x0="2023-04-01", x1="2023-12-31",
        fillcolor="green", opacity=0.1,
        layer="below", line_width=0,
        annotation_text="2023 Bull Run", annotation_position="top left"
    )
    
    # Highlight 2024 Market Corrections (approx. mid-2024, let's use Jun-Aug 2024 as an example or May-June)
    fig.add_vrect(
        x0="2024-05-01", x1="2024-07-31",
        fillcolor="red", opacity=0.1,
        layer="below", line_width=0,
        annotation_text="2024 Market Corrections", annotation_position="top left"
    )
    
    # Formatting
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="NAV (INR)",
        legend_title="Mutual Fund Scheme",
        hovermode="x unified",
        template="plotly_white"
    )
    
    # Save chart
    os.makedirs('../reports', exist_ok=True)
    # Note: saving to PNG might require kaleido, we can save to HTML for interactivity
    # But deliverables asked for exported PNG charts. 
    try:
        fig.write_image('../reports/nav_trend_analysis.png', width=1200, height=800)
        print("Successfully saved PNG.")
    except Exception as e:
        print("Could not save PNG (kaleido might be missing). Saving as HTML instead.")
        fig.write_html('../reports/nav_trend_analysis.html')
    
    print("NAV trend analysis complete.")

if __name__ == "__main__":
    nav_trend_analysis()
