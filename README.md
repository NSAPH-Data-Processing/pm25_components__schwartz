# pm25_components__schwartz

Code to process and format PM2.5 **component** estimates from Schwartz et al. at the Harvard Dataverse. This pipeline downloads pre-aggregated spatial data and processes it into standardized yearly files across multiple geographic resolutions.

This pipeline processes 15 PM2.5 components: br, ca, cu, ec, fe, k, nh4, ni, no3, oc, pb, si, so4, v, and zn for years 2000-2019 across 5 spatial resolutions: block groups, tracts, counties, states, and ZCTAs.

---

# Schwartz PM2.5 Components

The data comes from Schwartz et al.'s PM2.5 component estimates, made publicly available through the Harvard Dataverse at [doi:10.7910/DVN/F6PQAA](https://doi.org/10.7910/DVN/F6PQAA). The dataset provides spatially aggregated PM2.5 component concentrations (μg/m³) that have already been processed from satellite data and ground monitoring networks.

The dataset characteristics:
* **Temporal coverage**: 2000-2019 (20 years)
* **Spatial resolutions**: Block groups, census tracts, counties, states, and ZIP Code Tabulation Areas (ZCTAs)
* **Geographic region**: United States
* **Components**: 15 chemical components (br, ca, cu, ec, fe, k, nh4, ni, no3, oc, pb, si, so4, v, zn)
* **Format**: Pre-aggregated CSV files by spatial resolution and decade

The original data is organized by decade and spatial resolution:
* 2000s decade files: `block-groups-2000.csv`, `counties-2000.csv`, etc.
* 2010s decade files: `block-groups-2010.csv`, `counties-2010.csv`, etc.

In this repository, we download the complete dataset and reformat it into yearly files with standardized naming conventions and data types for easier analysis and integration with other datasets.

---

# Codebook

## Dataset Columns

The output files contain PM2.5 component concentrations aggregated by geographic units and year. Each file includes:

* **Spatial identifier**: Geographic unit identifier (varies by resolution)
  - `block_group`: Census block group identifier (string)
  - `tract`: Census tract identifier (string)
  - `county`: County FIPS code (string)
  - `state`: State FIPS code (string)
  - `zcta`: ZIP Code Tabulation Area identifier (string)
* **year**: Year of the data (2000-2019)
* **PM2.5 Component concentrations** (μg/m³):
  - `br`: Bromine component
  - `ca`: Calcium component
  - `cu`: Copper component
  - `ec`: Elemental carbon component
  - `fe`: Iron component
  - `k`: Potassium component
  - `nh4`: Ammonium component
  - `ni`: Nickel component
  - `no3`: Nitrate component
  - `oc`: Organic carbon component
  - `pb`: Lead component
  - `si`: Silicon component
  - `so4`: Sulfate component
  - `v`: Vanadium component
  - `zn`: Zinc component

## Output File Structure

Output files follow the naming convention: `pm25_components__schwartz__[spatial_level]_yearly__[year].parquet`

Examples:
* `pm25_components__schwartz__county_yearly__2015.parquet`
* `pm25_components__schwartz__zcta_yearly__2010.parquet`
* `pm25_components__schwartz__block_group_yearly__2005.parquet`

Files are stored in Parquet format for efficient storage and processing, organized in directories by spatial resolution:
* `output/county_yearly/`
* `output/tract_yearly/`
* `output/state_yearly/`
* `output/zcta_yearly/`
* `output/block_group_yearly/`

---

# Configuration Files

The configuration structure within the `/conf` folder allows you to modify parameters for:
* Data download: `src/download_data.py`
* Data processing: `src/process_data.py`
* Quality control: `src/qc_check.py`
* Directory path creation: `utils/create_dir_paths.py`

## Key Parameters

* **Dataverse settings**: Harvard Dataverse URL and persistent identifier (DOI)
* **Spatial levels**: Which geographic resolutions to process (block groups, tracts, counties, states, ZCTAs)
* **Year range**: Data processing period (2000-2019)
* **Data types**: Explicit type casting for ID columns and component values
* **File mappings**: Translation between input and output file naming conventions
* **ID column mappings**: Decade-specific column name mappings for spatial identifiers

## Configuration Files

* `conf/config.yaml`: Main pipeline configuration including dataverse settings, spatial levels, data types, and processing parameters
* `conf/datapaths/datapaths.yaml`: Input and output data path specifications

---

# Run

## Conda Environment

Clone the repository and create a conda environment:

```bash
git clone https://github.com/NSAPH-Data-Processing/pm25_components__schwartz
cd pm25_components__schwartz

conda env create -f requirements.yaml
conda activate pm25_components_schwartz  
```

It is also possible to use `mamba`:

```bash
mamba env create -f requirements.yaml
mamba activate pm25_components_schwartz
```

## Input and Output Paths

Run the directory creation utility:

```bash
python utils/create_dir_paths.py
```

This creates the necessary directory structure for input and output data based on the configuration in `conf/datapaths/datapaths.yaml`.

## Pipeline

You can run the pipeline steps manually:

**Step 1: Download data from Harvard Dataverse**

```bash
python src/download_data.py
```

This downloads and extracts the ZIP file containing all spatial resolution files from the Harvard Dataverse.

**Step 2: Process data into yearly files**

```bash
python src/process_data.py
```

This processes the raw CSV files into yearly Parquet files with:
- Standardized column names (ID columns renamed to spatial resolution names)
- String data type casting for all spatial identifiers
- Proper decade-based year splitting (2000-2009 from `-2000` files, 2010-2019 from `-2010` files)
- Consistent file naming convention

## References

The underlying PM2.5 component data comes from research by Schwartz et al. Please cite the original dataset when using this processed data:

Schwartz, J. (2024). PM2.5 Components Data [Dataset]. Harvard Dataverse. [doi:10.7910/DVN/F6PQAA](https://doi.org/10.7910/DVN/F6PQAA)

---

# Data Processing Details

## Decade-based Processing

The original data is organized into two decades:
- **2000s files** (`*-2000.csv`): Contains data for years 2000-2009 and 2010-2019
- **2010s files** (`*-2010.csv`): Contains data for years 2000-2019 with updated spatial boundaries

The pipeline correctly handles this by:
- Extracting years 2000-2009 from `-2000` files
- Extracting years 2010-2019 from `-2010` files
- Using appropriate ID column mappings for each decade (different column names between 2000 and 2010 Census boundaries)

## Spatial Resolution Details

| Resolution | Typical Count | ID Column | Description |
|------------|---------------|-----------|-------------|
| Block Groups | ~208K-216K | `block_group` | Finest geographic unit |
| Census Tracts | ~65K-73K | `tract` | Sub-county divisions |
| ZIP Code Tabulation Areas | ~32K | `zcta` | Postal code approximations |
| Counties | ~3K | `county` | County-level aggregations |
| States | 49 | `state` | State-level aggregations |