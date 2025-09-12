import os
import sys
from dotenv import load_dotenv

load_dotenv()

def validate_required_env_vars():
    """Validate that all required environment variables are set."""
    required_vars = {
        'DISCORD_BOT_TOKEN': 'Discord bot token is required',
        'TARGET_SERVER_ID': 'Target Discord server ID is required',
        'BIGQUERY_PROJECT_ID': 'BigQuery project ID is required'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        print("\n".join(missing_vars))
        print("\n💡 Please check your .env file or environment configuration.")
        sys.exit(1)

# Validate before loading
validate_required_env_vars()

# Bot Configuration
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_SERVER_ID = int(os.getenv('TARGET_SERVER_ID'))

# BigQuery Configuration  
PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID')
DATASET_ID = os.getenv('BIGQUERY_DATASET_ID', 'discord_data')

# Service Account Configuration
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Task Intervals (in minutes/hours)
MEMBER_UPDATE_INTERVAL = int(os.getenv('MEMBER_UPDATE_INTERVAL', '60'))
MESSAGE_UPDATE_INTERVAL = int(os.getenv('MESSAGE_UPDATE_INTERVAL', '60'))
VOICE_UPDATE_INTERVAL = int(os.getenv('VOICE_UPDATE_INTERVAL', '60'))
THREAD_UPDATE_INTERVAL = int(os.getenv('THREAD_UPDATE_INTERVAL', '720'))  # 12 hours
PRESENCE_UPDATE_INTERVAL = int(os.getenv('PRESENCE_UPDATE_INTERVAL', '1440'))  # 24 hours

# Table prefix for environment separation (Optional)
TABLE_PREFIX = os.getenv('BIGQUERY_TABLE_PREFIX', '')

# Default table names
DEFAULT_TABLES = {
    'members': 'dim_member',
    'message_counts': 'message_count', 
    'message_details': 'messages',
    'voice_activity': 'voice_channel',
    'threads': 'thread',
    'presence_logs': 'daily_user_logins'
}

def get_table_name(table_key: str) -> str:
    """Get table name with optional environment prefix."""
    base_name = DEFAULT_TABLES[table_key]
    return f"{TABLE_PREFIX}{base_name}" if TABLE_PREFIX else base_name