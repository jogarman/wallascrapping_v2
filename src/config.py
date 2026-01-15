import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def load_config():
    """Loads configuration from split files (general_scrap_config.json and elements_to_scrap.json) and overrides with environment variables."""
    
    general_config_path = BASE_DIR / "config/general_scrap_config.json"
    elements_config_path = BASE_DIR / "elements_to_scrap.json"
    
    config = {}
    
    # Load General Config
    if general_config_path.exists():
        with open(general_config_path, "r", encoding="utf-8") as f:
             config.update(json.load(f))
    else:
        # Fallback for older setups or error
        print(f"Warning: {general_config_path} not found.")

    # Load Search Items
    if elements_config_path.exists():
        with open(elements_config_path, "r", encoding="utf-8") as f:
             config.update(json.load(f))
    else:
         print(f"Warning: {elements_config_path} not found.")
    
    # Override with env vars (example pattern)
    if os.getenv("HEADLESS") and "scraping" in config:
        config["scraping"]["headless"] = os.getenv("HEADLESS").lower() == "true"
        
    return config

# Global config object
CONFIG = load_config()

# Paths (derived from config or defaults)
DATA_DIR = BASE_DIR / CONFIG.get("paths", {}).get("data_dir", "data")
GLOBAL_TRACKER_PATH = DATA_DIR / "global_tracker.csv"
