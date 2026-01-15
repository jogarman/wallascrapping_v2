import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def load_config():
    """Loads configuration from config.json and overrides with environment variables."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Override with env vars (example pattern)
    if os.getenv("HEADLESS"):
        config["scraping"]["headless"] = os.getenv("HEADLESS").lower() == "true"
        
    return config

# Global config object
CONFIG = load_config()

# Paths (derived from config or defaults)
DATA_DIR = BASE_DIR / CONFIG.get("paths", {}).get("data_dir", "data")
GLOBAL_TRACKER_PATH = DATA_DIR / "global_tracker.csv"
