import logging
import pandas as pd
from pathlib import Path
from .config import DATA_DIR, CONFIG
# from .tracker import load_tracker, update_tracker, get_existing_ids, mark_as_filtered

logger = logging.getLogger(__name__)

def run_initial_filter():
    """
    Step 2:
    1. Load latest raw CSV from step 1.
    2. Filter out IDs that are already in the global tracker.
    3. Update global tracker with NEW IDs (marking them as seen).
    4. Save filtered list to step 2.
    """
    # Find latest file in step1
    step1_dir = DATA_DIR / "step1"
    files = list(step1_dir.glob("raw_*.csv"))
    if not files:
        logger.warning("No raw data found in data/step1/")
        return

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Processing latest file: {latest_file}")
    
    df = pd.read_csv(latest_file, dtype={"id": str})
    
    if df.empty:
        logger.warning("Raw file is empty.")
        return

    # Filter against tracker first (we only want to process new IDs)
    # existing_ids = get_existing_ids()
    # new_items_mask = ~df["id"].isin(existing_ids)
    # df_new = df[new_items_mask].copy()
    df_new = df.copy() # FORCE ALL (Tracker ignored)
    
    # if df_new.empty:
    #    logger.info("No new items to process.")
    #    return
    
    # if df_new.empty:
    #    logger.info("No new items to process.")
    #    return
    
    # if df_new.empty:
    #    logger.info("No new items to process.")
    #    return
    
    # if df_new.empty:
    #    logger.info("No new items to process.")
    #    return
    
    if df_new.empty:
        logger.info("No new items to process.")
        return

    # Update tracker with newly seen IDs immediately
    # update_tracker(df_new)

    # ---------------------------------------------------------
    # Apply Keyword Filtering (Inclusion / Exclusion)
    # ---------------------------------------------------------
    # We need to map items back to their config rules. 
    # 'search_term' column in CSV helps us know which rule applied.
    
    included_rows = []
    excluded_rows = []

    import re

    # Helper function to check keywords (Legacy Logic Replication)
    def check_filter(row):
        title = str(row.get("nombre", "")).lower()
        search_term = str(row.get("search_term", "")).lower()
        
        if not title or title == "no title":
            return False, "Empty or invalid title"

        # Find config for this search term
        item_config = next((item for item in CONFIG["search_items"] if item["name"].lower() == search_term), None)
        
        if not item_config:
            return False, "Config not found"

        # Updated logic: Split by non-alphanumeric characters AND split numbers from letters (e.g. "11pro" -> "11", "pro")
        # This allows "iPhone 11pro" to match "iPhone 11"
        tokens_list = re.findall(r'[a-zA-Z]+|\d+', title)
        if not tokens_list:
             return False, "No tokens found"
             
        title_tokens = set(tokens_list)
        first_token = tokens_list[0].lower()

        start_exclude_keywords = set()
        exclude_keywords = set()

        # Load blacklists from file if defined
        if "blacklist_dir" in item_config:
            blacklist_path = Path(item_config["blacklist_dir"])
            
            # First word blacklist
            first_word_file = blacklist_path / "first_word_blacklist.txt"
            if first_word_file.exists():
                with open(first_word_file, "r", encoding="utf-8") as f:
                    start_exclude_keywords = set(line.strip().lower() for line in f if line.strip())
            
            # Rest of words blacklist
            rest_file = blacklist_path / "rest_of_words_blacklist.txt"
            if rest_file.exists():
                with open(rest_file, "r", encoding="utf-8") as f:
                    exclude_keywords = set(line.strip().lower() for line in f if line.strip())
            
            # DEBUG
            # print(f"DEBUG: Start Exclusions: {start_exclude_keywords}")
        else:
             # Fallback to config lists (legacy support or inline config)
             start_exclude_keywords = set(k.lower() for k in item_config.get("start_exclude_keywords", []))
             exclude_keywords = set(k.lower() for k in item_config.get("exclude_keywords", []))

        # 1. Start Exclusion (First word only)
        if first_token[0].isdigit():
             return False, f"First char is digit: {first_token}"

        if first_token in start_exclude_keywords:
             return False, f"First word excluded: {first_token}"

        # 2. General Exclusion (Anywhere)
        # Intersection: if any excluded word appears in title tokens
        common_exclusions = title_tokens.intersection(exclude_keywords)
        if common_exclusions:
            return False, f"Excluded term found: {common_exclusions}"

        # 2. Check Inclusion (Token based)
        # We will require ALL tokens of the search term to be in the title tokens.
        required_tokens = set(re.findall(r'[a-zA-Z]+|\d+', search_term))
        
        if not required_tokens.issubset(title_tokens):
            missing = required_tokens - title_tokens
            return False, f"Missing required tokens: {missing}"
        
        # 3. Check Price
        # Parse price from string like "1.200 €" or "10,50 €"
        raw_price = str(row.get("precio", "0"))
        try:
            # Remove '€' and '.' (thousands), replace ',' with '.' (decimal)
            clean_price = raw_price.replace("€", "").replace(".", "").replace(",", ".").strip()
            # Handle empty string if price was just symbol
            if not clean_price: 
                clean_price = "0"
                
            price_val = float(clean_price)
            
            # Get min price from config (default 0 if not set)
            min_price = item_config.get("filters", {}).get("precio_min", 0)
            
            if price_val < min_price:
                 return False, f"Price too low: {price_val} < {min_price}"
        except ValueError:
            # If price cannot be parsed (e.g. "A convenir"), we default to keeping it 
            # or could log a warning. For now, pass.
            pass 

        return True, "OK"

    for _, row in df_new.iterrows():
        is_ok, reason = check_filter(row)
        if is_ok:
            included_rows.append(row)
        else:
            # Add reason to row for debugging
            row["filter_reason"] = reason
            excluded_rows.append(row)

    # Convert to DataFrames
    df_inc = pd.DataFrame(included_rows) if included_rows else pd.DataFrame(columns=df_new.columns)
    df_exc = pd.DataFrame(excluded_rows) if excluded_rows else pd.DataFrame(columns=df_new.columns)

    # ---------------------------------------------------------
    # Save to separate folders
    # ---------------------------------------------------------
    timestamp = latest_file.stem.replace("raw_", "")

    # Save Included
    if included_rows:
        dir_inc = DATA_DIR / "step2_inc"
        dir_inc.mkdir(parents=True, exist_ok=True)
        path_inc = dir_inc / f"filtered_{timestamp}.csv"
        df_inc.to_csv(path_inc, index=False)
        logger.info(f"Saved {len(df_inc)} INCLUDED items to {path_inc}")
    
    # Save Excluded
    if excluded_rows:
        dir_exc = DATA_DIR / "step2_exc"
        dir_exc.mkdir(parents=True, exist_ok=True)
        path_exc = dir_exc / f"excluded_{timestamp}.csv"
        df_exc.to_csv(path_exc, index=False)
        logger.info(f"Saved {len(df_exc)} EXCLUDED items to {path_exc}")

    if not included_rows and not excluded_rows:
         logger.info("All new items were processed but none saved? (Matches logic error)")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_initial_filter()
