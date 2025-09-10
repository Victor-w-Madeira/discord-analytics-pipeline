import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_SERVER_ID = int(os.getenv('TARGET_SERVER_ID', '1116803230643527710'))

# BigQuery Configuration
PROJECT_ID = os.getenv('BIGQUERY_PROJECT_ID', 'langflow-data-project')
DATASET_ID = os.getenv('BIGQUERY_DATASET_ID', 'discord_data')

# Service Account Configuration
SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Task Intervals (in minutes/hours)
MEMBER_UPDATE_INTERVAL = int(os.getenv('MEMBER_UPDATE_INTERVAL', '60'))
MESSAGE_UPDATE_INTERVAL = int(os.getenv('MESSAGE_UPDATE_INTERVAL', '60'))
VOICE_UPDATE_INTERVAL = int(os.getenv('VOICE_UPDATE_INTERVAL', '60'))
THREAD_UPDATE_INTERVAL = int(os.getenv('THREAD_UPDATE_INTERVAL', '720'))  # 12 hours
PRESENCE_UPDATE_INTERVAL = int(os.getenv('PRESENCE_UPDATE_INTERVAL', '1440'))  # 24 hours