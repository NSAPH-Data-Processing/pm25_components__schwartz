import pandas as pd
import os
import hydra
from omegaconf import DictConfig

# This script processes PM2.5 component data by splitting it into yearly files.
# The methodology follows this structure:
# - Data for 2000-2009 uses the -2000 file as input
# - Data for 2010-2019 uses the -2010 file as input (when available)
# - ID columns are renamed and types are cast as per config
# - Uses hydra for configuration management and datapaths for directory structure


def process_single_year(input_file, spatial_resolution, output_dir, year, id_column_mapping, decade_suffix):
    """
    Process PM2.5 components data for a single year and spatial resolution
    
    Parameters:
    input_file (str): Path to the input CSV file
    spatial_resolution (str): Spatial resolution (e.g., 'zcta', 'county', etc.)
    output_dir (str): Directory to save the yearly file
    year (int): Specific year to process
    id_column_mapping (dict): Mapping of spatial levels to their original ID column names
    decade_suffix (str): Either '2000' or '2010' indicating the source decade
    """
    print(f"Processing {input_file} for {spatial_resolution} resolution, year {year}...")
    
    df = pd.read_csv(input_file)
    
    if 'year' not in df.columns:
        print(f"Warning: 'year' column not found in {input_file}. Available columns: {df.columns.tolist()}")
        return
    
    # Filter for the specific year
    df = df[df['year'] == year].copy()
    
    if len(df) == 0:
        print(f"No data found for year {year} in {input_file}")
        return
    
    # Rename the ID column to match the spatial level name
    if spatial_resolution in id_column_mapping and decade_suffix in id_column_mapping[spatial_resolution]:
        original_id_col = id_column_mapping[spatial_resolution][decade_suffix]
        if original_id_col and original_id_col in df.columns:
            df = df.rename(columns={original_id_col: spatial_resolution})
            print(f"Renamed ID column from '{original_id_col}' to '{spatial_resolution}'")
        else:
            print(f"Warning: Expected ID column '{original_id_col}' not found in {input_file}")
    else:
        print(f"Warning: No ID column mapping found for {spatial_resolution} and decade {decade_suffix}")
    
    if spatial_resolution in df.columns:
        df[spatial_resolution] = df[spatial_resolution].astype(str)
        print(f"Cast '{spatial_resolution}' column to string type")
    
    # Create output directory and save file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"pm25_components__schwartz__{spatial_resolution}_yearly__{year}.parquet")
    df.to_parquet(output_file, index=False)
    print(f"Saved {len(df)} records to {output_file}")


@hydra.main(config_path="../conf", config_name="config", version_base=None)
def main(cfg: DictConfig):
    """Main processing function - processes single spatial level and year"""
    
    # Standard directories (set up by create_dir_paths.py)
    input_dir = "data/input/pm25_components__schwartz__raw/block-groups-tracts-counties-states-zctas-2000-2010"
    output_base_dir = "data/output"
    
    # Configuration values
    file_mappings = cfg.file_mappings
    id_column_mappings = cfg.id_column_mappings
    
    # Get command line overrides for spatial level and year
    spatial_level = cfg.get('spatial_level', None)
    year = cfg.get('year', None)
    
    if not spatial_level:
        print("❌ Error: spatial_level must be specified")
        print(f"Available spatial levels: {list(file_mappings.keys())}")
        return
        
    if not year:
        print("❌ Error: year must be specified")
        print(f"Available year range: {cfg.data.year_min}-{cfg.data.year_max}")
        return
    
    if spatial_level not in file_mappings:
        print(f"❌ Error: Unknown spatial level '{spatial_level}'")
        print(f"Available spatial levels: {list(file_mappings.keys())}")
        return
    
    year = int(year)
    if year < cfg.data.year_min or year > cfg.data.year_max:
        print(f"❌ Error: Year {year} is outside the configured range {cfg.data.year_min}-{cfg.data.year_max}")
        return
    
    print(f"Processing spatial level: {spatial_level}")
    print(f"Processing year: {year}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_base_dir}")
    
    # Get input filename for this spatial level
    input_filename = file_mappings[spatial_level]
    output_dir = f"{output_base_dir}/{spatial_level}_yearly"
    
    # Determine which decade file to use and decade suffix
    if 2000 <= year <= 2009:
        input_file = f"{input_dir}/{input_filename}-2000.csv"
        decade_suffix = '2000'
    elif 2010 <= year <= 2019:
        input_file = f"{input_dir}/{input_filename}-2010.csv"
        decade_suffix = '2010'
    else:
        print(f"❌ Error: Year {year} is not in a supported decade range")
        return
    
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        return
    
    # Process the single year and spatial level
    process_single_year(input_file, spatial_level, output_dir, year, id_column_mappings, decade_suffix)


if __name__ == "__main__":
    main()