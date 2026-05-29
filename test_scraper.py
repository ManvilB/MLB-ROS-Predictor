import pybaseball as pyb
import pandas as pd
import os

def fetch_initial_statcast_data():
    print("Fetching Statcast data. This might take a minute...")
    
    # Grab the first week of the 2024 season as our test sample
    data = pyb.statcast(start_dt="2024-03-28", end_dt="2024-04-04")
    
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save to CSV so we don't have to query the API every time we test
    filepath = "data/test_statcast_2024.csv"
    data.to_csv(filepath, index=False)
    
    print(f"Success! Data saved to {filepath}")
    print(f"Total pitches recorded: {len(data)}")
    
    # Preview the most important predictive columns for hitters
    columns_to_preview = ['player_name', 'events', 'launch_speed', 'launch_angle', 'estimated_woba_using_speedangle']
    print("\nSample of predictive hitting metrics:")
    print(data[columns_to_preview].head())

if __name__ == "__main__":
    fetch_initial_statcast_data()