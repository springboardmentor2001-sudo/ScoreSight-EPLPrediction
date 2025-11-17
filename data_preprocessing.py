import pandas as pd
import glob
import os
from datetime import datetime

# These are the columns we want to keep from each dataset
# They represent important match statistics we'll use for our predictions
req_cols = ['Date', 'HomeTeam', 'AwayTeam', 'HTHG', 'HTAG', 'HTR', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HST', 'AST', 'HC', 'AC', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR']

def standardize_datasets():
    """
    Process all season CSV files and combine them into one standardized dataset
    This makes it easier to work with the data for our machine learning models
    """
    # Find all the season CSV files in our directory
    season_files = glob.glob("season-*.csv")
    
    print(f"Found {len(season_files)} season files")
    print("Files:", season_files)
    
    # We'll store each processed season in this list
    all_seasons = []
    
    # Go through each file one by one
    for file in season_files:
        try:
            print(f"\nProcessing {file}...")
            # Load the CSV data
            df = pd.read_csv(file)
            
            # Get the season from the filename (e.g., "2010-2011" from "season-2010-2011.csv")
            season = file.replace("season-", "").replace(".csv", "")
            
            print(f"Original shape: {df.shape}")
            print(f"Original columns: {list(df.columns)}")
            
            # Check if we have all the columns we need
            missing_cols = [col for col in req_cols if col not in df.columns]
            if missing_cols:
                print(f"Missing columns in {file}: {missing_cols}")
                continue
            
            # Keep only the columns we need
            df_standardized = df[req_cols].copy()
            
            # Add a column to track which season this data is from
            df_standardized['Season'] = season
            
            # Convert the date column to proper date format
            df_standardized['Date'] = pd.to_datetime(df_standardized['Date'], errors='coerce')
            
            # Add this season's data to our list
            all_seasons.append(df_standardized)
            
            print(f"Successfully processed {file} - Shape: {df_standardized.shape}")
            
        except Exception as e:
            print(f"Error processing {file}: {str(e)}")
            continue
    
    # Combine all seasons into one big dataset
    if all_seasons:
        print(f"\nCombining {len(all_seasons)} seasons...")
        unified_df = pd.concat(all_seasons, ignore_index=True)
        
        # Sort by date so the data is in chronological order
        unified_df = unified_df.sort_values('Date').reset_index(drop=True)
        
        # Save our combined dataset to a new CSV file
        unified_df.to_csv('unified_dataset.csv', index=False)
        
        print(f"\nUnified dataset created successfully!")
        print(f"Total matches: {len(unified_df)}")
        print(f"Seasons covered: {unified_df['Season'].nunique()}")
        print(f"Date range: {unified_df['Date'].min()} to {unified_df['Date'].max()}")
        
        # Show some basic information about our dataset
        print("\nDataset Info:")
        print(unified_df.info())
        
        # Show a few sample rows
        print("\nSample data:")
        print(unified_df.head())
        
        return unified_df
    else:
        print("No datasets were successfully processed")
        return None

# This runs when we execute the script directly
if __name__ == "__main__":
    unified_data = standardize_datasets()