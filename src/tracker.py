import pandas as pd
from datetime import datetime
import os
from .config import GLOBAL_TRACKER_PATH

COLUMNS = [
    "id", 
    "t_first_scrap", 
    "t_last_scrap", 
    "filter_1", 
    "filter_2", 
    "ia_processed"
]

def load_tracker():
    """Loads the global tracker CSV."""
    if not os.path.exists(GLOBAL_TRACKER_PATH):
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(GLOBAL_TRACKER_PATH, dtype={"id": str})

def save_tracker(df):
    """Saves the global tracker CSV."""
    df.to_csv(GLOBAL_TRACKER_PATH, index=False)

def get_existing_ids():
    """Returns a set of all article IDs in the tracker."""
    df = load_tracker()
    return set(df["id"].tolist())

def update_tracker(new_data):
    """
    Updates the tracker with new articles or updates timestamps for existing ones.
    new_data: DataFrame or list of dicts with 'id'.
    """
    df = load_tracker()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ensure new_data is a DataFrame
    if isinstance(new_data, list):
        new_df = pd.DataFrame(new_data)
    else:
        new_df = new_data.copy()

    if new_df.empty:
        return

    new_df["id"] = new_df["id"].astype(str)

    # Separate new vs existing
    existing_ids = set(df["id"])
    new_articles = new_df[~new_df["id"].isin(existing_ids)].copy()
    seen_articles_ids = new_df[new_df["id"].isin(existing_ids)]["id"].tolist()

    # Add new articles
    if not new_articles.empty:
        new_articles["t_first_scrap"] = current_time
        new_articles["t_last_scrap"] = current_time
        new_articles["filter_1"] = False # Default
        new_articles["filter_2"] = False # Default
        new_articles["ia_processed"] = False # Default
        
        # Keep only relevant columns
        for col in COLUMNS:
            if col not in new_articles.columns:
                new_articles[col] = False if "filter" in col or "ia" in col else None
                if col == "t_last_scrap" or col == "t_first_scrap":
                     new_articles[col] = current_time
        
        df = pd.concat([df, new_articles[COLUMNS]], ignore_index=True)

    # Update timestamp for seen articles
    if seen_articles_ids:
        df.loc[df["id"].isin(seen_articles_ids), "t_last_scrap"] = current_time

    save_tracker(df)

def mark_as_filtered(ids, stage=1, passed=True):
    """Marks articles as passing or failing a filter stage."""
    df = load_tracker()
    col = f"filter_{stage}"
    if col in df.columns:
        df.loc[df["id"].isin(ids), col] = passed
        save_tracker(df)

def mark_as_ia_processed(ids):
    """Marks articles as having been processed by IA."""
    df = load_tracker()
    df.loc[df["id"].isin(ids), "ia_processed"] = True
    save_tracker(df)
