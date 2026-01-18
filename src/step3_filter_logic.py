import logging
import pandas as pd
from pathlib import Path
from .config import DATA_DIR, BASE_DIR
from .tracker import mark_as_filtered, update_tracker

logger = logging.getLogger(__name__)

BLACKLIST_PATH = BASE_DIR / "config/blacklist.txt"
WHITELIST_PATH = BASE_DIR / "config/whitelist.txt"

def load_list(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

def run_business_logic_filter():
    """
    Step 3:
    1. Load latest from step 2 (filtered items).
    2. Apply Blacklist (exclude if title contains X).
    3. Apply Whitelist (include ONLY if title contains Y - if whitelist not empty).
    4. Save to step 3.
    """
    # Find latest file in step2
    step2_dir = DATA_DIR / "step2_inc"
    files = list(step2_dir.glob("filtered_*.csv"))
    if not files:
        logger.warning("No step 2 data found.")
        return

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Processing step 2 file: {latest_file}")
    
    df = pd.read_csv(latest_file, dtype={"id": str})
    
    if df.empty:
        logger.warning("Step 2 file is empty.")
        return

    blacklist = load_list(BLACKLIST_PATH)
    whitelist = load_list(WHITELIST_PATH)
    
    logger.info(f"Loaded {len(blacklist)} blacklist terms and {len(whitelist)} whitelist terms.")

    valid_items = []
    
    for _, row in df.iterrows():
        title = str(row.get("nombre", "")).lower()
        item_id = str(row["id"])
        
        # Check Blacklist
        if any(term in title for term in blacklist):
            logger.debug(f"Item {item_id} excluded by blacklist: {title}")
            mark_as_filtered([item_id], stage=3, passed=False)
            continue
            
        # Check Whitelist (if stricter logic is needed)
        # Assuming whitelist is 'must contain at least one' if not empty
        if whitelist and not any(term in title for term in whitelist):
            logger.debug(f"Item {item_id} excluded by whitelist: {title}")
            mark_as_filtered([item_id], stage=3, passed=False)
            continue
            
        valid_items.append(row)
        mark_as_filtered([item_id], stage=3, passed=True)
        
    filtered_df = pd.DataFrame(valid_items)
    
    if not filtered_df.empty:
        timestamp = latest_file.stem.replace("filtered_", "")
        output_path = DATA_DIR / "step3" / f"refined_{timestamp}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        filtered_df.to_csv(output_path, index=False)
        logger.info(f"Step 3 complete. retained {len(filtered_df)} items. Saved to {output_path}")
    else:
        logger.info("Step 3 complete. No items remained after filtering.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_business_logic_filter()
