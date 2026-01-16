import argparse
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from .config import CONFIG

# Setup logging
log_dir = Path("scrapping_outputs")
log_dir.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
log_file = log_dir / f"orchestrator_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_step(step_func, step_name, max_retries=3):
    """Executes a step with retry logic."""
    logger.info(f"Starting {step_name}...")
    for attempt in range(1, max_retries + 1):
        try:
            step_func()
            logger.info(f"{step_name} completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Error in {step_name} (Attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(2)  # Wait before retry
            else:
                logger.critical(f"{step_name} failed after {max_retries} attempts.")
                return False
    return False

from .step1_scraper import run_scraper
from .step2_filter_initial import run_initial_filter
from .step3_filter_logic import run_business_logic_filter
from .step4_enrich_gemini_basic import run_gemini_enrichment
from .step5_finalize import run_finalization
from .notifier import notify_completion, notify_error

import os
try:
    from apify_client import ApifyClient
except ImportError:
    ApifyClient = None

def main():
    parser = argparse.ArgumentParser(description="Wallascrap V2 Orchestrator")
    parser.add_argument("--pipeline", type=str, default="full", help="Pipeline to run: full, custom")
    args = parser.parse_args()

    # Apify Input Integration
    if os.getenv("APIFY_IS_AT_HOME"):
        logger.info("Running in Apify environment...")
        try:
            client = ApifyClient()
            # In local dev (not strictly on platform), default_key_value_store_client might need setup
            # But usually we just read INPUT.json manually or rely on env vars if pushed to platform
            # Simpler approach: Check for Actor Input
            # For this MVP, we will just proceed. Real integration would read the Key-Value store.
            pass
        except Exception as e:
            logger.warning(f"Apify setup warning: {e}")
            
    # Load config overrides from Env Vars (common pattern for Docker/Apify)
    if os.getenv("SEARCH_TERM"):
        search_term = os.getenv("SEARCH_TERM")
        logger.info(f"Overriding search term from Env Var: {search_term}")
        
        # Override the search_items list with a single item based on the env var
        CONFIG["search_items"] = [{
            "name": search_term,
            "filters": {
                # Default filters for dynamic input or read from other env vars if needed
                "min_price": None,
                "max_price": None,
                "estado": "all",
                "distancia": "50000", # Default 50km
                "municipio": None,
                "latitude": 40.41956, 
                "longitude": -3.69196,
                "conditions": {"new": True, "as_good_as_new": True, "good": True, "fair": True, "has_given_much": True}
            }
        }]

    if os.getenv("HEADLESS"):
        is_headless = os.getenv("HEADLESS", "true").lower() == "true"
        CONFIG["scraping"]["headless"] = is_headless
        logger.info(f"Overriding headless mode from Env Var: {is_headless}")
        
    if os.getenv("SCROLLS"):
        try:
            scrolls = int(os.getenv("SCROLLS"))
            CONFIG["scraping"]["scrolls"] = scrolls
            logger.info(f"Overriding scrolls from Env Var: {scrolls}")
        except ValueError:
            logger.warning("Invalid SCROLLS env var, ignoring.")


    logger.info(f"Initialization complete. Config loaded. Log file: {log_file}")
    
    try:
        # 1. Scraper
        if not run_step(run_scraper, "Step 1: Scraper"):
            notify_error("Step 1 failed.")
            sys.exit(1)
            
        # 2. Initial Filter
        if not run_step(run_initial_filter, "Step 2: Initial Filter"):
            notify_error("Step 2 failed.")
            sys.exit(1)

        # 3. Business Logic Filter
        if not run_step(run_business_logic_filter, "Step 3: Business Logic (Blacklist/Whitelist)"):
            notify_error("Step 3 failed.")
            sys.exit(1)

        # 4. Gemini Enrichment
        if not run_step(run_gemini_enrichment, "Step 4: Gemini Enrichment"):
            notify_error("Step 4 failed.")
            sys.exit(1)
            
        # 5. Finalize
        if not run_step(run_finalization, "Step 5: Finalize"):
            notify_error("Step 5 failed.")
            sys.exit(1)
            
        # Placeholder for future steps
        logger.info("All steps completed.")
        notify_completion("N/A (Check Logs)") # TODO: Pass actual count
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        notify_error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
