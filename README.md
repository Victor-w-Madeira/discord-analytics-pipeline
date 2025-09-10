# Discord Analytics Bot

A modular Discord bot that collects analytics data from Discord servers and stores it in Google BigQuery.

## Features

- **Member Analytics**: Track member joins, leaves, and profile updates
- **Message Analytics**: Count messages and store message details
- **Voice Activity**: Track time spent in voice channels
- **Thread Analytics**: Monitor thread creation
- **Presence Logs**: Track user online/offline status

## Project Structure

```
discord-analytics-bot/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point
│   ├── bot.py                      # Main bot class
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py             # Environment configuration
│   │   └── bigquery_config.py      # BigQuery schemas and client
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── message_handler.py      # Message events
│   │   ├── member_handler.py       # Member events
│   │   ├── voice_handler.py        # Voice activity events
│   │   ├── thread_handler.py       # Thread events
│   │   └── presence_handler.py     # Presence events
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bigquery_service.py     # BigQuery operations
│   │   └── data_buffer.py          # Thread-safe data buffering
│   └── utils/
│       ├── __init__.py
│       └── helpers.py              # Utility functions
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
└── docker-compose.yml
```

## Setup

### Prerequisites

- Python 3.8+
- Google Cloud Project with BigQuery enabled
- Discord Bot Token
- Service Account with BigQuery permissions

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd discord-analytics-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the bot:
```bash
cd src
python main.py
```

### Docker Setup

1. Build and run with docker-compose:
```bash
docker-compose up -d
```

## Configuration

All configuration is handled through environment variables. See `.env.example` for all available options.

### Required Environment Variables

- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `TARGET_SERVER_ID`: Discord server ID to monitor
- `BIGQUERY_PROJECT_ID`: Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON file

### Google Cloud Authentication

You have two options for authentication:

1. **Service Account File** (recommended for local development):
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

2. **Service Account JSON** (for containerized environments):
```bash
export GOOGLE_SERVICE_ACCOUNT_INFO='{"type":"service_account","project_id":"..."}'
```

## Architecture

The bot is structured into several modules:

- **Handlers**: Process Discord events (messages, members, voice, etc.)
- **Services**: Handle data storage and BigQuery operations
- **Config**: Manage configuration and BigQuery schemas
- **Utils**: Utility functions and decorators

### Data Flow

1. **Discord Events** → **Handlers** → **Data Buffer**
2. **Periodic Tasks** → **BigQuery Service** → **BigQuery Tables**

### Thread Safety

All data operations use async locks to ensure thread safety when multiple events occur simultaneously.

## BigQuery Tables

The bot creates and manages the following tables:

- `dim_member`: Member information and status
- `message_count`: Daily message counts by user and channel
- `messages`: Detailed message data
- `voice_channel`: Voice activity duration
- `thread`: Thread creation data
- `daily_user_logins`: User presence logs

## Monitoring and Logging

The bot includes comprehensive logging:

- **INFO**: General operation status
- **DEBUG**: Detailed event processing
- **ERROR**: Error conditions with context
- **Execution timing**: Performance monitoring for BigQuery operations

## Deployment

### Local Development
```bash
cd src
python main.py
```

### Docker Deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables for Production
```bash
# Required
DISCORD_BOT_TOKEN=your_actual_token
TARGET_SERVER_ID=1116803230643527710
BIGQUERY_PROJECT_ID=langflow-data-project
GOOGLE_SERVICE_ACCOUNT_INFO='{"type":"service_account",...}'

# Optional (with defaults)
BIGQUERY_DATASET_ID=discord_data
MEMBER_UPDATE_INTERVAL=60
MESSAGE_UPDATE_INTERVAL=60
VOICE_UPDATE_INTERVAL=60
THREAD_UPDATE_INTERVAL=720
PRESENCE_UPDATE_INTERVAL=1440
```

## Error Handling

The bot includes robust error handling:

- **Graceful degradation**: Individual event failures don't stop the bot
- **Data recovery**: Failed uploads are retried on the next cycle
- **Logging**: All errors are logged with context for debugging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Notes

- Never commit `.env` files or service account keys
- Use environment variables for all sensitive configuration
- Regularly rotate Discord bot tokens and service account keys
- Review BigQuery permissions to ensure least privilege access

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify environment configuration
3. Ensure BigQuery permissions are correct
4. Open an issue with relevant logs and configuration (remove sensitive data)