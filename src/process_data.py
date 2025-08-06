import pandas as pd
import os
import yaml
from pathlib import Path

# This script processes PM2.5 component data by splitting it into yearly files.
# The methodology follows this structure:
# - Data for 2000-2009 uses the -2000 file as input
# - Data for 2010-2020 uses the -2010 file as input (when available)
# - id columns are renamed and types are casted as per config
#TODO: add hydra, snakemake, and datapath handling

def load_config():
    """Load configuration from config files"""
    config_dir = Path(__file__).parent.parent / "conf"
    with open(config_dir / "config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    with open(config_dir / "datapaths" / "datapaths.yaml", 'r') as f:
        datapaths = yaml.safe_load(f)
    
    return config, datapaths


def split_data_by_year(input_file, spatial_resolution, output_dir, output_format, decade_suffix, id_column_mapping, base_name):
    """
    Split PM2.5 components data by year
    
    Parameters:
    input_file (str): Path to the input CSV file (e.g., zctas-2000.csv)
    output_dir (str): Directory to save the yearly files
    spatial_resolution (str): Spatial resolution (e.g., 'zctas', 'counties', 'tracts', 'block_groups', 'states')
    decade_suffix (str): Either '2000' or '2010' indicating the source decade
    output_format (str): Output format ('parquet' or 'csv')
    id_column_mapping (dict): Mapping of spatial levels to their original ID column names
    """
    print(f"Processing {input_file} for {spatial_resolution} resolution...")
    
    df = pd.read_csv(input_file)
    
    if 'year' not in df.columns:
        print(f"Warning: 'year' column not found in {input_file}. Available columns: {df.columns.tolist()}")
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
    
    os.makedirs(output_dir, exist_ok=True)
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
            output_file = os.path.join(output_dir, f"{base_name}__{spatial_resolution}_yearly__{year}.parquet")
            year_data.to_parquet(output_file, index=False)
            print(f"Saved {len(year_data)} records to {output_file}")
        else:
            print(f"No data found for year {year}")


def main():
    """Main processing function"""
    config, datapaths = load_config()
    
    workspace_root = Path(__file__).parent.parent
    
    input_dir = workspace_root / config['processing']['input_dir']
    output_base_dir = workspace_root / config['processing']['output_dir']
    output_format = config['processing']['output_format']
    file_mappings = config['file_mappings']
    id_column_mappings = config['id_column_mappings']
    base_name = config['data']['base_name']
    
    print(f"Processing {len(file_mappings)} spatial levels: {list(file_mappings.keys())}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_base_dir}")
    print(f"Output format: {output_format}")
    
    # Process each spatial resolution using file_mappings
    for output_name, input_filename in file_mappings.items():
        print(f"\n=== Processing {output_name.upper()} data ===")
        
        output_dir_name = output_name.replace('-', '_') + '_yearly'
        output_dir = output_base_dir / output_dir_name
        
        # Process 2000s decade data
        input_file_2000 = input_dir / f"{input_filename}-2000.csv"
        if input_file_2000.exists():
            split_data_by_year(str(input_file_2000), output_name.replace('-', '_'), 
                             str(output_dir), output_format, '2000', id_column_mappings, base_name)
        else:
            print(f"Input file not found: {input_file_2000}")
        
        # Process 2010s decade data
        input_file_2010 = input_dir / f"{input_filename}-2010.csv"
        if input_file_2010.exists():
            split_data_by_year(str(input_file_2010), output_name.replace('-', '_'), 
                             str(output_dir), output_format, '2010', id_column_mappings, base_name)
        else:
            print(f"Input file not found: {input_file_2010}")


if __name__ == "__main__":
    main()