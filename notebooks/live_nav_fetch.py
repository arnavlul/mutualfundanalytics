import pandas as pd
import requests

def fetch_and_save_nav(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}" 
    response = requests.get(url)
    data = response.json()

    nav_history = data.get("data", [])
    if not nav_history:
        print(f"No data found for scheme {scheme_code}")
        return
    
    df = pd.DataFrame(nav_history)
    save_path = f"../data/raw/live_schemes_fetched/{scheme_code}_live_nav.csv"
    df.to_csv(save_path, index=False)

    print(f"Saved {scheme_code} (Shape: {df.shape}) to {save_path}")


if __name__ == "__main__":
    schemes_to_fetch = [
                        125497, # HDFC Top 100 Direct
                        119551, # SBI Bluechip 
                        120503, # ICICI Bluechip
                        118632, # Nippon Large Cap
                        119092, # Axis Bluechip
                        120841  # Kotak Bluechip
                        ] 
    
    for scheme in schemes_to_fetch:
        fetch_and_save_nav(scheme)