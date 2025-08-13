"""
Snakemake workflow for  downloading PM2.5 components data from Harvard Dataverse and processing into LEGO format across multiple spatial levels.
"""

import os
from omegaconf import OmegaConf

# Load config and extract parameters
config_path = "conf/config.yaml"
cfg = OmegaConf.load(config_path)

SPATIAL_LEVELS = cfg.data.spatial_levels
FILE_MAPPINGS = cfg.file_mappings
YEARS = list(range(cfg.data.year_min, cfg.data.year_max + 1))

rule all:
    input:
        expand("data/output/{spatial_level}_yearly/pm25_components__schwartz__{spatial_level}_yearly__{year}.parquet",
               spatial_level=SPATIAL_LEVELS,
               year=YEARS)

rule create_directories:
    output:
        touch("outputs/directories_created.txt")
    shell:
        "python utils/create_dir_paths.py"

rule download_data:
    input:
        "outputs/directories_created.txt"
    output:
        expand("data/input/pm25_components__schwartz__raw/block-groups-tracts-counties-states-zctas-2000-2010/{file_prefix}-{decade}.csv",
               file_prefix=FILE_MAPPINGS.values(),
               decade=["2000", "2010"])
    shell:
        "python src/download_data.py"

rule process_data:
    input:
        rules.download_data.output
    output:
        "data/output/{spatial_level}_yearly/pm25_components__schwartz__{spatial_level}_yearly__{year}.parquet"
    params:
        spatial_level="{spatial_level}",
        year="{year}"
    shell:
        "python src/process_data.py spatial_level={params.spatial_level} year={params.year}"
