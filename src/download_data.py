import hydra
import os
import zipfile
from omegaconf import DictConfig
from pyDataverse.api import DataAccessApi, NativeApi


@hydra.main(config_path="../conf", config_name="config", version_base=None)
def main(cfg: DictConfig):    
    
    # connect to dataverse
    api = NativeApi(cfg.dataverse.baseurl)
    data_api = DataAccessApi(cfg.dataverse.baseurl)
    dataset = api.get_dataset(cfg.dataverse.pid)

    # extract filename mapping from dataverse
    files_list = dataset.json()["data"]["latestVersion"]["files"]
    file2id = {f["dataFile"]["filename"]: f["dataFile"]["id"] for f in files_list}
    
    print(f"Available files in dataverse: {list(file2id.keys())}")
    
    # Define the specific ZIP file to download
    target_zip_filename = "block-groups-tracts-counties-states-zctas-2000-2010.zip"
    
    if target_zip_filename not in file2id:
        print(f"Error: File {target_zip_filename} not found in dataverse.")
        print(f"Available files: {list(file2id.keys())}")
        return
    
    print(f"Downloading {target_zip_filename}...")
    
    # Download the ZIP file
    response = data_api.get_datafile(str(file2id[target_zip_filename]), is_pid=False, auth=False)
    
    # Create output directory using config
    output_dir = cfg.processing.input_dir.replace('block-groups-tracts-counties-states-zctas-2000-2010', '').rstrip('/')
    output_dir_path = os.path.abspath(output_dir)
    os.makedirs(output_dir_path, exist_ok=True)
    
    # Save the ZIP file
    zip_path = os.path.join(output_dir_path, target_zip_filename)
    with open(zip_path, "wb") as f:
        f.write(response.content)
    
    print(f"Downloaded {target_zip_filename} to {zip_path}")
    
    # Extract the ZIP file
    print(f"Extracting {target_zip_filename}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir_path)
    
    print(f"Extracted files to {output_dir_path}")
    
    # List extracted files
    extracted_files = []
    for root, dirs, files in os.walk(output_dir_path):
        for file in files:
            if file.endswith('.csv'):
                extracted_files.append(os.path.join(root, file))
    
    print(f"Extracted CSV files: {extracted_files}")
    
    # Optionally, remove the ZIP file after extraction
    os.remove(zip_path)
    print(f"Removed ZIP file: {zip_path}")
    
    print(f"\nData download and extraction complete!")
    print(f"Files are ready for processing in: {cfg.processing.input_dir}")

    
if __name__ == "__main__":
    main()