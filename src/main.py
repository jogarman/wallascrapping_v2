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

def main():
    parser = argparse.ArgumentParser(description="Wallascrap V2 Orchestrator")
    parser.add_argument("--pipeline", type=str, default="full", help="Pipeline to run: full, custom")
    args = parser.parse_args()

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
