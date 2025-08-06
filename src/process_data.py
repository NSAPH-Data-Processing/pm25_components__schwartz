"""
Data Processing Script for PM2.5 Components

This script processes PM2.5 component data by splitting it into yearly files.
The methodology follows this structure:
- Data for 2000-2009 uses the -2000 file as input
- Data for 2010-2020 uses the -2010 file as input (when available)
- Each year gets its own output file
"""

import pandas as pd
import os
import yaml
from pathlib import Path


def load_config():
    """Load configuration from config files"""
    config_dir = Path(__file__).parent.parent / "conf"
    
    # Load main config
    with open(config_dir / "config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Load datapaths
    with open(config_dir / "datapaths" / "datapaths.yaml", 'r') as f:
        datapaths = yaml.safe_load(f)
    
    return config, datapaths


def split_data_by_year(input_file, output_dir, spatial_resolution, decade_suffix):
    """
    Split PM2.5 components data by year
    
    Parameters:
    input_file (str): Path to the input CSV file (e.g., zctas-2000.csv)
    output_dir (str): Directory to save the yearly files
    spatial_resolution (str): Spatial resolution (e.g., 'zctas', 'counties', 'tracts', 'block-groups', 'states')
    decade_suffix (str): Either '2000' or '2010' indicating the source decade
    """
    print(f"Processing {input_file} for {spatial_resolution} resolution...")
    
    # Read the data
    df = pd.read_csv(input_file)
    
    # Print column names and first few rows for debugging
    print(f"Columns in {input_file}: {df.columns.tolist()}")
    print(f"Data shape: {df.shape}")
    print(f"First few rows:")
    print(df.head())
    
    # Check if 'year' column exists
    if 'year' not in df.columns:
        print(f"Warning: 'year' column not found in {input_file}. Available columns: {df.columns.tolist()}")
        return
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get unique years in the data
    years = sorted(df['year'].unique())
    
    # Determine year range based on decade suffix
    if decade_suffix == '2000':
        target_years = [year for year in years if 2000 <= year <= 2009]
    elif decade_suffix == '2010':
        target_years = [year for year in years if 2010 <= year <= 2020]
    else:
        target_years = years  # Process all years if suffix is unclear
    
    print(f"Found years: {years}")
    print(f"Processing years: {target_years}")
    
    # Split data by year
    for year in target_years:
        year_data = df[df['year'] == year].copy()
        
        if len(year_data) > 0:
            # Create output filename with .parquet extension
            output_file = os.path.join(output_dir, f"{spatial_resolution}_{year}.parquet")
            
            # Save the data as Parquet
            year_data.to_parquet(output_file, index=False)
            print(f"Saved {len(year_data)} records to {output_file}")
        else:
            print(f"No data found for year {year}")


def main():
    """Main processing function"""
    config, datapaths = load_config()
    
    # Get the workspace root directory
    workspace_root = Path(__file__).parent.parent
    
    # Define the input directory where extracted files are located
    input_dir = workspace_root / "data" / "input" / "pm25_components__randall__raw" / "block-groups-tracts-counties-states-zctas-2000-2010"
    
    # Define all spatial resolutions to process
    spatial_resolutions = ['block-groups', 'tracts', 'counties', 'states', 'zctas']
    
    # Process each spatial resolution
    for spatial_resolution in spatial_resolutions:
        print(f"\n=== Processing {spatial_resolution.upper()} data ===")
        
        # Create a single output directory for this spatial resolution
        # Replace hyphens with underscores and add "_yearly" suffix
        output_dir_name = spatial_resolution.replace('-', '_') + '_yearly'
        output_dir = workspace_root / "output" / output_dir_name
        
        # Process 2000s decade data
        input_file_2000 = input_dir / f"{spatial_resolution}-2000.csv"
        if input_file_2000.exists():
            split_data_by_year(str(input_file_2000), str(output_dir), spatial_resolution.replace('-', '_'), '2000')
        else:
            print(f"Input file not found: {input_file_2000}")
        
        # Process 2010s decade data
        input_file_2010 = input_dir / f"{spatial_resolution}-2010.csv"
        if input_file_2010.exists():
            split_data_by_year(str(input_file_2010), str(output_dir), spatial_resolution.replace('-', '_'), '2010')
        else:
            print(f"Input file not found: {input_file_2010}")


if __name__ == "__main__":
    main()