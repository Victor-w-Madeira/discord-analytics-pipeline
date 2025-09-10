from google.cloud import bigquery
import os
import json
from .settings import PROJECT_ID

def get_bigquery_client():
    """Get BigQuery client instance."""
    # Try to use service account file path first
    service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if service_account_path and os.path.exists(service_account_path):
        return bigquery.Client.from_service_account_json(service_account_path)
    
    # Fallback to service account info from environment
    service_account_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO')
    if service_account_info:
        service_account_data = json.loads(service_account_info)
        return bigquery.Client.from_service_account_info(service_account_data)
    
    # Use default credentials (for Google Cloud environments)
    return bigquery.Client(project=PROJECT_ID)

# BigQuery table schemas
SCHEMAS = {
    'members': [
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("user_name", "STRING"),
        bigquery.SchemaField("display_name", "STRING"),
        bigquery.SchemaField("is_bot", "BOOLEAN"),
        bigquery.SchemaField("is_booster", "BOOLEAN"),
        bigquery.SchemaField("role", "STRING"),
        bigquery.SchemaField("joined_at", "TIMESTAMP"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("updated_at", "TIMESTAMP"),
    ],
    'message_counts': [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("channel_id", "STRING"),
        bigquery.SchemaField("message_count", "INTEGER"),
    ],
    'message_details': [
        bigquery.SchemaField("message_id", "STRING"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("channel_id", "STRING"),
        bigquery.SchemaField("thread_id", "STRING"),
        bigquery.SchemaField("message_content", "STRING"),
    ],
    'voice_activity': [
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("channel_id", "STRING"),
        bigquery.SchemaField("duration_seconds", "INTEGER"),
    ],
    'threads': [
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("thread_name", "STRING"),
        bigquery.SchemaField("channel_id", "STRING"),
        bigquery.SchemaField("thread_id", "STRING"),
    ],
    'presence_logs': [
        bigquery.SchemaField("logged_at", "TIMESTAMP"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("user_name", "STRING"),
    ]
}