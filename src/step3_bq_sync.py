import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from .services.bigquery_service import BigQueryService

load_dotenv()

# Setup Logging
logger = logging.getLogger(__name__)

def run_sync():
    logger.info("Starting Step 3: BigQuery Sync...")
    
    # 1. Load Data (Included and Excluded from Step 2)
    # Usually Step 2 outputs to data/step2_inc and data/step2_exc
    # We want the LATEST run.
    
    # Helper to find latest csv in a dir
    def get_latest_file(directory):
        paths = list(Path(directory).glob("*.csv"))
        if not paths:
            return None
        return max(paths, key=lambda p: p.stat().st_mtime)

    inc_file = get_latest_file("data/step2_inc")
    exc_file = get_latest_file("data/step2_exc")
    
    inc_file = get_latest_file("data/step2_inc")
    exc_file = get_latest_file("data/step2_exc")
    
    bq_service = BigQueryService()
    if not bq_service.client:
        logger.error("BigQuery client not available.")
        return False

    def sync_table(file_path, table_name):
        if not file_path:
            logger.info(f"No file for {table_name}")
            return True
            
        logger.info(f"Syncing {file_path} to {table_name}...")
        df = pd.read_csv(file_path)
        
        if df.empty:
            logger.warning(f"File {file_path} is empty.")
            return True

        # Ensure timestamps
        for col in ["created", "modified", "last_view", "time_scrap"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        # Force ID to string to avoid INT64/STRING mismatch in BQ
        if "id" in df.columns:
            df["id"] = df["id"].astype(str)
        
        staging_table = f"{table_name}_staging"
        full_target_id = f"{bq_service.project_id}.{bq_service.dataset_id}.{table_name}"
        full_staging_id = f"{bq_service.project_id}.{bq_service.dataset_id}.{staging_table}"
        
        # 1. Upload to Staging
        if not bq_service.upload_dataframe(df, staging_table, if_exists="replace"):
            logger.error(f"Failed to upload to {staging_table}")
            return False
            
        # 2. Check Exists
        if not bq_service.table_exists(table_name):
            logger.info(f"Target {table_name} missing. Creating...")
            create_query = f"CREATE TABLE `{full_target_id}` AS SELECT * FROM `{full_staging_id}`"
            return bq_service.execute_query(create_query)
            
        # 3. MERGE
        logger.info(f"Merging into {table_name}...")
        # Note: 'filter_status' might check mismatch if item jumped from Exc to Inc?
        # But here we handle tables separately.
        
        merge_query = f"""
        MERGE `{full_target_id}` T
        USING `{full_staging_id}` S
        ON T.id = S.id
        WHEN MATCHED AND (
            T.precio != S.precio OR 
            T.nombre != S.nombre OR 
            (T.filter_reason != S.filter_reason OR (T.filter_reason IS NULL AND S.filter_reason IS NOT NULL) OR (T.filter_reason IS NOT NULL AND S.filter_reason IS NULL))
        ) THEN
          UPDATE SET 
            modified = S.modified,
            last_view = S.last_view,
            precio = S.precio,
            nombre = S.nombre,
            filter_reason = S.filter_reason,
            url_articulo = S.url_articulo,
            municipio = S.municipio,
            distancia = S.distancia,
            search_term = S.search_term,
            filter_status = S.filter_status
        WHEN MATCHED THEN
          UPDATE SET
            last_view = S.last_view
        WHEN NOT MATCHED THEN
          INSERT ROW
        """
        result = bq_service.execute_query(merge_query)
        
        # Cleanup Staging Table
        if result:
            logger.info(f"Dropping staging table {staging_table}...")
            bq_service.execute_query(f"DROP TABLE `{full_staging_id}`")
            
        return result

    success_inc = sync_table(inc_file, "step2_inc")
    success_exc = sync_table(exc_file, "step2_exc")
    
    if success_inc and success_exc:
        logger.info("Sync completed successfully for both tables.")
        return True
    else:
        logger.error("Sync failed for one or more tables.")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_sync()
