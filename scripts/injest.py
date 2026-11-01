import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

# 1. Set Kaggle API Token environment variable
os.environ["KAGGLE_KEY"] = "KGAT_347a62e398f8e71ebe56c9f14ef0dfff"

# 2. Parameters
DATASET_ID = "bwandowando/dpwh-flood-control-projects"
OUTPUT_DIR = Path("data/raw")


def run_ingestion():
    # Ensure raw data output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize and authenticate Kaggle API
    api = KaggleApi()
    api.authenticate()

    print(f"📥 Extracting dataset '{DATASET_ID}' into {OUTPUT_DIR}...")

    # Download and unzip files directly into data/raw
    api.dataset_download_files(DATASET_ID, path=OUTPUT_DIR, unzip=True)

    print("✅ Extraction complete! Downloaded files:")
    for file_path in OUTPUT_DIR.glob("*"):
        print(f"   📄 {file_path.name}")


if __name__ == "__main__":
    run_ingestion()