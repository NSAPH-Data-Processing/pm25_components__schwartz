# pm25_components__schwartz

Code to process and format PM2.5 **component** estimates from Schwartz et al. at the Harvard Dataverse. This pipeline downloads pre-aggregated spatial data and processes it into standardized yearly files across multiple geographic resolutions using a Snakemake workflow.

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

# Workflow Structure

The pipeline consists of three main steps:

1. **Directory Setup**: Creates the required directory structure for input/output data
2. **Data Download**: Downloads raw CSV files from Harvard Dataverse
3. **Data Processing**: Converts raw files into yearly Parquet files with standardized formatting

---

# Data Processing Details

For each spatial level, the source data is organized into two files:
- **2000s files** (`*-2000.csv`): PM2.5 component data for 2000–2019, aggregated using the 2000 Census geographic boundaries 
- **2010s files** (`*-2010.csv`):  PM2.5 component data for 2000–2019, aggregated using the 2010 Census geographic boundaries

The pipeline handles this by:
- Extracting years 2000-2009 from `-2000` files
- Extracting years 2010-2019 from `-2010` files
- Using appropriate ID column mappings for each decade (different column names between 2000 and 2010 Census boundaries)

---

# Codebook

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

---

# Configuration and File Structure

## Key Configuration Files

* **`conf/config.yaml`**: Main pipeline settings including:
  - File mappings between input and output naming conventions
  - ID column mappings for different decades and spatial resolutions
  - Spatial levels and year ranges to process
  - Data type specifications for consistent formatting

* **`conf/defaults.yaml`**: Processing parameters that can be overridden:
  - `spatial_level`: Target spatial resolution for single-file processing
  - `year`: Target year for single-file processing

* **`conf/datapaths/`**: Environment-specific data path configurations
  - `datapaths.yaml`: Local development paths

---

# Quick Start

## Environment Setup

Clone the repository and create a conda environment:

```bash
git clone https://github.com/NSAPH-Data-Processing/pm25_components__schwartz
cd pm25_components__schwartz

conda env create -f requirements.yaml
conda activate pm25_components_schwartz  
```

You can also use `mamba` for faster package resolution:

```bash
mamba env create -f requirements.yaml
mamba activate pm25_components_schwartz
```

## Running the Complete Pipeline

**Option 1: Full pipeline execution (recommended)**

```bash
# Run the complete pipeline with parallel processing
snakemake --cores 4

```

**Option 3: Step-by-step manual execution**

```bash
# Step 1: Create directory structure
python utils/create_dir_paths.py

# Step 2: Download raw data from Harvard Dataverse
python src/download_data.py

# Step 3: Process specific combinations
python src/process_data.py spatial_level=county year=2015
python src/process_data.py spatial_level=zcta year=2010
```

## Output Validation

The processed files maintain strict formatting standards:
- **Spatial IDs**: Always cast as strings for consistent handling
- **Year column**: Integer type with values matching filename
- **PM2.5 components**: Float64 with appropriate null handling
- **File naming**: Consistent `pm25_components__schwartz__[spatial_level]_yearly__[year].parquet` pattern

---

# References

Amini, H., Danesh-Yazdi, M., Di, Q., Requia, W., Wei, Y., Abu-Awad, Y., Shi, L., Franklin, M., Kang, C.-M., Wolfson, J., James, P., Habre, R., Zhu, Q., Apte, J., Andersen, Z., Kloog, I., Dominici, F., Koutrakis, P., & Schwartz, J. (2022). Hyperlocal super-learned PM2.5 components across the contiguous US. Research Square Platform LLC. doi:10.21203/rs.3.rs-1745433/v1doi: 10.21203/rs.3.rs-1745433/v1

