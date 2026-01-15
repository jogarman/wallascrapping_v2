import logging
import pandas as pd
import google.generativeai as genai
import os
import json
import time
from pathlib import Path
from .config import DATA_DIR
from .tracker import mark_as_ia_processed

logger = logging.getLogger(__name__)

def configure_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment variables.")
        return False
    genai.configure(api_key=api_key)
    return True

def extract_specs(model, text):
    prompt = f"""
    Analyze the following product title and description to extract specifications for an iPhone.
    Return ONLY a JSON object with these keys: "gen" (generation, e.g. "13", "14 Pro"), "mod" (model, e.g. "Pro", "Max", "Mini"), "memoria" (storage, e.g. "128GB"), "bateria" (battery health %, e.g. "90%").
    If a value is missing, use null.
    
    Text: "{text}"
    """
    try:
        response = model.generate_content(prompt)
        # simplistic cleanup
        text_resp = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text_resp)
    except Exception as e:
        logger.warning(f"Gemini error for text '{text}': {e}")
        return {"gen": None, "mod": None, "memoria": None, "bateria": None}

def run_gemini_enrichment():
    """
    Step 4:
    1. Load latest from step 3.
    2. For each item, call Gemini to get details.
    3. Save to step 4.
    """
    if not configure_gemini():
        return

    # Find latest file in step3
    step3_dir = DATA_DIR / "step3"
    files = list(step3_dir.glob("refined_*.csv"))
    if not files:
        logger.warning("No step 3 data found.")
        return

    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    logger.info(f"Processing step 3 file: {latest_file}")
    
    df = pd.read_csv(latest_file, dtype={"id": str})
    
    if df.empty:
        logger.warning("Step 3 file is empty.")
        return

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    enriched_data = []
    
    for i, row in df.iterrows():
        item_id = str(row["id"])
        title = str(row.get("nombre", ""))
        
        # Rate limiting simplistic approach
        if i > 0 and i % 10 == 0:
            time.sleep(2)
            
        specs = extract_specs(model, title)
        
        # Merge
        row_dict = row.to_dict()
        row_dict.update(specs)
        enriched_data.append(row_dict)
        
        mark_as_ia_processed([item_id])

    enriched_df = pd.DataFrame(enriched_data)
    
    if not enriched_df.empty:
        timestamp = latest_file.stem.replace("refined_", "")
        output_path = DATA_DIR / "step4" / f"enriched_{timestamp}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        enriched_df.to_csv(output_path, index=False)
        logger.info(f"Step 4 complete. Enriched {len(enriched_df)} items. Saved to {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_gemini_enrichment()
