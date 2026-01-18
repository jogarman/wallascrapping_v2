import os
import logging
from pathlib import Path
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

logger = logging.getLogger(__name__)

class BigQueryService:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("BQ_DATASET")
        self.credentials_path = os.getenv("GCP_SA_KEY_PATH")
        
        if not all([self.project_id, self.dataset_id, self.credentials_path]):
            logger.warning("BigQuery config missing in .env. Upload will be skipped.")
            self.client = None
            return

        try:
            # Resolve relative path if needed
            creds_path = Path(self.credentials_path)
            if not creds_path.is_absolute():
                creds_path = Path(os.getcwd()) / creds_path
            
            if not creds_path.exists():
                logger.error(f"GCP Key file not found at: {creds_path}")
                self.client = None
                return

            self.credentials = service_account.Credentials.from_service_account_file(str(creds_path))
            self.client = bigquery.Client(credentials=self.credentials, project=self.project_id)
            
            # Ensure dataset exists
            try:
                self.client.get_dataset(self.dataset_id)
                logger.info(f"BigQuery Service initialized. Dataset {self.dataset_id} found.")
            except Exception:
                logger.warning(f"Dataset {self.dataset_id} not found or inaccessible. Creating...")
                dataset_ref = bigquery.Dataset(f"{self.project_id}.{self.dataset_id}")
                dataset_ref.location = "EU"
                try:
                    self.client.create_dataset(dataset_ref, exists_ok=True)
                    logger.info(f"Dataset {self.dataset_id} created.")
                except Exception as creation_err:
                     logger.error(f"Failed to create dataset: {creation_err}")
            
            logger.info(f"BigQuery Service initialized for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery Client: {e}")
            self.client = None

    def table_exists(self, table_name: str) -> bool:
        """Checks if a table exists in the dataset."""
        if not self.client:
            return False
            
        full_table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        try:
            self.client.get_table(full_table_id)
            return True
        except NotFound:
            return False
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False

    def upload_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = "append"):
        """
        Uploads a pandas DataFrame to BigQuery.
        if_exists: 'fail', 'replace', 'append'
        """
        if not self.client:
            logger.warning("BigQuery client not initialized. Skipping upload.")
            return False

        full_table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        logger.info(f"Uploading {len(df)} rows to {full_table_id}...")
        
        try:
            job_config = bigquery.LoadJobConfig(
                autodetect=True,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND if if_exists == 'append' else bigquery.WriteDisposition.WRITE_TRUNCATE
            )
            
            job = self.client.load_table_from_dataframe(
                df, full_table_id, job_config=job_config
            )
            job.result()  # Wait for the job to complete.

            table = self.client.get_table(full_table_id)
            logger.info(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {full_table_id}")
            return True

        except Exception as e:
            logger.error(f"BigQuery Upload Failed: {e}")
            return False

    def execute_query(self, query: str):
        """Executes a SQL query."""
        if not self.client:
            return False
            
        try:
            query_job = self.client.query(query)
            query_job.result()  # Wait for result
            logger.info("Query executed successfully.")
            return True
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return False
