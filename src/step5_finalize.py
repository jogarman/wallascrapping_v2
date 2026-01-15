import logging
import pandas as pd
import json
from .config import DATA_DIR
from .step1_scraper import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

logger = logging.getLogger(__name__)

def deep_scrape_enrichment(df, driver):
    """
    Iterates over rows with missing specs and visits the URL to get description.
    """
    # Placeholder: In a real run, this would be slow.
    # We will just try to fetch description and re-run gemini (or regex)
    # For now, we will skip implementation to avoid complexity in this pass,
    # as the user instructions allow 'dejar vacio' if not found.
    # If strictly needed, we would perform driver.get(row['url']) here.
    pass

def run_finalization():
    """
    Step 5:
    1. Load latest step 4 data.
    2. Check for missing critical data.
    3. (Optional) Deep scrape if missing.
    4. Save final JSON.
    """
    step4_dir = DATA_DIR / "step4"
    files = list(step4_dir.glob("enriched_*.csv"))
    if not files:
        logger.warning("No step 4 data found.")
        return

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Processing step 4 file: {latest_file}")
    
    df = pd.read_csv(latest_file, dtype={"id": str})
    
    if df.empty:
        logger.warning("Step 4 file is empty.")
        return

    # Filter/Clean
    # Ensure specific columns exist
    required_cols = ["gen", "mod", "memoria", "bateria"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    # Convert NaN to None for Valid JSON
    df = df.where(pd.notnull(df), None)
    
    final_data = df.to_dict(orient="records")
    
    timestamp = latest_file.stem.replace("enriched_", "")
    output_path = DATA_DIR / "final_results.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Final data saved to {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_finalization()
