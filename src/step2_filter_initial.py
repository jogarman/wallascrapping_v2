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

    df_new = df.copy() # FORCE ALL (Tracker ignored)

    if df_new.empty:
        logger.info("No new items to process.")
        return

    included_rows = []
    excluded_rows = []

    import re

    # Helper function to check keywords
    def check_filter(row):
        title = str(row.get("nombre", "")).lower()
        search_term = str(row.get("search_term", "")).lower()
        
        if not title or title == "no title":
            return False, "Empty or invalid title"

        # Find config for this search term
        item_config = next((item for item in CONFIG["search_items"] if item["name"].lower() == search_term), None)
        if not item_config:
            return False, "Config not found"

        # Separate letters and numbers (e.g., "iphone12" -> "iphone 12")
        title = re.sub(r'([a-z])(\d)', r'\1 \2', title)
        title = re.sub(r'(\d)([a-z])', r'\1 \2', title)
        
        # Remove punctuation (except hyphens and underscores which are word separators)
        title = re.sub(r'[^\w\s\-_]', ' ', title)
        
        # Split title into words (by spaces, hyphens, underscores)
        words = re.split(r'[\s\-_]+', title)
        words = [w for w in words if w]  # Remove empty strings
        
        if not words:
            return False, "No words found"
        
        first_word = words[0]
        
        # Load blacklists
        start_exclude_keywords = set()
        exclude_keywords = set()
        
        if "blacklist_dir" in item_config:
            blacklist_path = Path(item_config["blacklist_dir"])
            
            first_word_file = blacklist_path / "first_word_blacklist.txt"
            if first_word_file.exists():
                with open(first_word_file, "r", encoding="utf-8") as f:
                    start_exclude_keywords = set(line.strip().lower() for line in f if line.strip())
            
            rest_file = blacklist_path / "rest_of_words_blacklist.txt"
            if rest_file.exists():
                with open(rest_file, "r", encoding="utf-8") as f:
                    exclude_keywords = set(line.strip().lower() for line in f if line.strip())
        
        # 1. Check if first word is in blacklist
        if first_word in start_exclude_keywords:
            return False, f"First word excluded: {first_word}"
        
        # 2. Get search term words (e.g., "iphone 16" -> ["iphone", "16"])
        search_words = search_term.split()
        if not search_words:
            return False, "Invalid search term"
        
        search_first_word = search_words[0]
        
        # 3. Check if title starts with search term first word
        if first_word != search_first_word:
            # 4. Check for blacklisted words in rest of title
            if any(word in exclude_keywords for word in words):
                matched = next((word for word in words if word in exclude_keywords), "unknown")
                return False, f"Blacklisted word: {matched}"
            
            # 5. If search term has a second word (number), check it exists in title
            if len(search_words) > 1:
                search_number = search_words[1]
                if search_number not in words:
                    return False, f"Missing number: {search_number}"
        
        # 6. Check Price
        raw_price = str(row.get("precio", "0"))
        try:
            # Remove '€' and '.' (thousands), replace ',' with '.' (decimal)
            clean_price = raw_price.replace("€", "").replace(".", "").replace(",", ".").strip()
            if not clean_price:
                clean_price = "0"
            
            price_val = float(clean_price)
            min_price = item_config.get("filters", {}).get("precio_min", 0)
            
            if price_val < min_price:
                return False, f"Price too low: {price_val} < {min_price}"
        except ValueError:
            # If price cannot be parsed, keep it
            pass
        
        return True, "OK"

    for _, row in df_new.iterrows():
        is_ok, reason = check_filter(row)
        if is_ok:
            included_rows.append(row)
        else:
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
