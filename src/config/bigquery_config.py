from google.cloud import bigquery
import os
import json
import logging
from .settings import PROJECT_ID

logger = logging.getLogger(__name__)

def get_bigquery_client():
    """Get BigQuery client instance with file-based service account info."""
    try:
        # Method 1: Try to use service account file path from environment
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if service_account_path and os.path.exists(service_account_path):
            logger.info(f"Using service account file from GOOGLE_APPLICATION_CREDENTIALS: {service_account_path}")
            return bigquery.Client.from_service_account_json(service_account_path)
        
        # Method 2: Check if GOOGLE_SERVICE_ACCOUNT_INFO contains a file path
        service_account_info = os.getenv('GOOGLE_SERVICE_ACCOUNT_INFO')
        if service_account_info:
            service_account_info = service_account_info.strip()
            
            # Check if it's a file path (ends with .json or starts with /)
            if (service_account_info.endswith('.json') or 
                service_account_info.startswith('/') or 
                service_account_info.startswith('./') or
                service_account_info.startswith('../')):
                
                logger.info(f"GOOGLE_SERVICE_ACCOUNT_INFO appears to be a file path: {service_account_info}")
                
                # Try to read the file
                if os.path.exists(service_account_info):
                    try:
                        logger.info(f"Reading service account JSON from file: {service_account_info}")
                        return bigquery.Client.from_service_account_json(service_account_info)
                    except Exception as e:
                        logger.error(f"Failed to read service account file {service_account_info}: {e}")
                else:
                    logger.warning(f"Service account file not found: {service_account_info}")
            
            # If not a file path, try to parse as JSON content
            else:
                try:
                    logger.info("Attempting to parse GOOGLE_SERVICE_ACCOUNT_INFO as JSON content")
                    service_account_data = json.loads(service_account_info)
                    
                    # Validate required fields
                    required_fields = ['type', 'project_id', 'private_key', 'client_email']
                    missing_fields = [field for field in required_fields if field not in service_account_data]
                    
                    if missing_fields:
                        raise ValueError(f"Missing required fields: {missing_fields}")
                    
                    logger.info("Successfully parsed service account JSON from environment variable")
                    return bigquery.Client.from_service_account_info(service_account_data)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GOOGLE_SERVICE_ACCOUNT_INFO as JSON: {e}")
                    logger.error(f"Content length: {len(service_account_info)} characters")
                    logger.error(f"Content preview: {service_account_info[:50]}...")
        
        # Method 3: Try common file locations
        common_paths = [
            '/application/service-account.json',
            './service-account.json', 
            '../service-account.json',
            'service-account.json',
            '/app/service-account.json'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found service account file at common location: {path}")
                try:
                    return bigquery.Client.from_service_account_json(path)
                except Exception as e:
                    logger.warning(f"Failed to use service account file {path}: {e}")
                    continue
        
        # Final fallback: Use default credentials
        logger.info("Using default Google Cloud credentials")
        return bigquery.Client(project=PROJECT_ID)
        
    except Exception as e:
        logger.error(f"Failed to create BigQuery client: {e}")
        
        # Debug information
        cwd = os.getcwd()
        logger.error(f"Current working directory: {cwd}")
        
        try:
            files = [f for f in os.listdir(cwd) if f.endswith('.json')]
            logger.error(f"JSON files in current directory: {files}")
        except Exception:
            pass
        
        # Show environment variables for debugging
        google_env_vars = {k: v[:50] + '...' if len(v) > 50 else v 
                          for k, v in os.environ.items() 
                          if 'GOOGLE' in k or 'SERVICE' in k}
        logger.error(f"Google-related environment variables: {google_env_vars}")
        
        raise

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