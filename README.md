# Discord Analytics Bot

A comprehensive Discord bot that collects analytics data from Discord servers and stores it in Google BigQuery for analysis and reporting.

## 🚀 Features

- **Member Analytics**: Track member joins, leaves, profile updates, and status changes
- **Message Analytics**: Count messages per user/channel and store detailed message data
- **Voice Activity**: Monitor time spent in voice channels with session tracking
- **Thread Analytics**: Track thread creation and participation
- **Presence Monitoring**: Log user online/offline activity patterns
- **Real-time Data Buffering**: Thread-safe data collection with periodic BigQuery uploads
- **Advanced Logging**: Structured logging with colored console output and file persistence
- **Docker Support**: Production-ready containerization with health checks

## 📁 Project Structure

```
discord-analytics-bot/
├── src/
│   ├── main.py                     # Application entry point
│   ├── bot.py                      # Main bot class with task management
│   ├── config/
│   │   ├── settings.py             # Environment configuration
│   │   ├── bigquery_config.py      # BigQuery schemas and client setup
│   │   └── logging_config.py       # Advanced logging configuration
│   ├── handlers/                   # Discord event handlers
│   │   ├── message_handler.py      # Message events with content filtering
│   │   ├── member_handler.py       # Member join/leave/update events
│   │   ├── voice_handler.py        # Voice channel activity tracking
│   │   ├── thread_handler.py       # Thread creation events
│   │   └── presence_handler.py     # User presence/status events
│   ├── services/
│   │   ├── bigquery_service.py     # BigQuery operations with merge/upsert
│   │   └── data_buffer.py          # Thread-safe data buffering
│   └── utils/
│       └── helpers.py              # Utility functions and decorators
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                     # Git ignore rules
├── .dockerignore                  # Docker ignore rules
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Multi-container setup
└── README.md                      # This file
```

## 🛠️ Prerequisites

- **Python 3.11+** (recommended for optimal performance)
- **Google Cloud Project** with BigQuery API enabled
- **Discord Bot Token** with appropriate permissions
- **Service Account** with BigQuery Data Editor permissions
- **Docker & Docker Compose** (for containerized deployment)

### Discord Bot Permissions

Your Discord bot needs these permissions:
- `Read Messages/View Channels`
- `Read Message History`
- `Connect` (for voice channel monitoring)
- `View Guild Members` (requires verification for large servers)

### Required Discord Intents

- `guilds`
- `members` (privileged)
- `presences` (privileged)
- `message_content` (privileged)

## 📋 Installation & Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd discord-analytics-bot
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Required - Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
TARGET_SERVER_ID=your_discord_server_id_here

# Required - BigQuery Configuration
BIGQUERY_PROJECT_ID=your_bigquery_project_id
BIGQUERY_DATASET_ID=discord_data

# Required - Google Cloud Authentication (choose one method)
# Method 1: Service Account File Path
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Method 2: Service Account JSON Content (for containers)
GOOGLE_SERVICE_ACCOUNT_INFO='{"type":"service_account","project_id":"..."}'

# Optional - Task Intervals (in minutes)
MEMBER_UPDATE_INTERVAL=60
MESSAGE_UPDATE_INTERVAL=60
VOICE_UPDATE_INTERVAL=60
THREAD_UPDATE_INTERVAL=720       # 12 hours
PRESENCE_UPDATE_INTERVAL=1440    # 24 hours

# Optional - Environment Separation
BIGQUERY_TABLE_PREFIX=           # e.g., "dev_" for development tables

# Optional - Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_COLORS=true                  # Enable colored console output
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Deployment Options

### Option 1: Local Development

```bash
cd src
python main.py
```

### Option 2: Docker Deployment (Recommended)

**Quick Start:**
```bash
# Ensure .env file is configured
docker-compose up --build -d
```

**Monitor Logs:**
```bash
# Real-time logs
docker-compose logs -f discord-analytics-bot

# Recent logs
docker-compose logs --tail=100 discord-analytics-bot
```

**Management Commands:**
```bash
# Stop the bot
docker-compose down

# Restart the bot
docker-compose restart discord-analytics-bot

# Rebuild after code changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check container status
docker-compose ps
```

**Log Files:**
Logs are automatically persisted in `./logs/`:
- `discord-bot.log` - All bot activities
- `error.log` - Error-level events only

## 📊 BigQuery Schema

The bot automatically creates and manages these tables:

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `dim_member` | Member information | `user_id`, `user_name`, `display_name`, `status`, `joined_at` |
| `message_count` | Daily message counts | `date`, `user_id`, `channel_id`, `message_count` |
| `messages` | Detailed message data | `message_id`, `user_id`, `channel_id`, `message_content` |
| `voice_channel` | Voice activity sessions | `date`, `user_id`, `channel_id`, `duration_seconds` |
| `thread` | Thread creation logs | `thread_id`, `user_id`, `thread_name`, `channel_id` |
| `daily_user_logins` | User presence logs | `logged_at`, `user_id`, `user_name` |

### Data Processing Features

- **Smart Merging**: Automatically handles duplicate data with MERGE operations
- **Content Filtering**: Filters out empty/null messages and bot content
- **Timestamp Handling**: Consistent UTC timezone across all tables
- **Batch Processing**: Configurable intervals for optimal BigQuery usage
- **Error Recovery**: Failed uploads are retried on the next cycle

## ⚙️ Configuration

### Task Intervals

Configure how often data is uploaded to BigQuery:

- **Short intervals (1-15 min)**: Good for development and testing
- **Medium intervals (30-60 min)**: Balanced for most production use cases
- **Long intervals (12-24 hours)**: Optimized for cost-sensitive deployments

### Table Prefixes

Use `BIGQUERY_TABLE_PREFIX` for environment separation:
- Development: `BIGQUERY_TABLE_PREFIX=dev_`
- Staging: `BIGQUERY_TABLE_PREFIX=staging_`
- Production: `BIGQUERY_TABLE_PREFIX=` (empty)

This creates tables like `dev_dim_member`, `staging_message_count`, etc.

## 🔍 Monitoring & Logging

### Log Levels

- **DEBUG**: Detailed event processing and user activities
- **INFO**: General operations, task completions, data uploads
- **WARNING**: Non-critical issues, skipped events
- **ERROR**: Failed operations, BigQuery errors, connection issues

### Log Features

- **Colored Console Output**: Visual categorization with emoji icons
- **Structured Logging**: Consistent format across all components
- **Performance Tracking**: Execution time logging for BigQuery operations
- **File Persistence**: Automatic log rotation with size limits

### Health Monitoring

Built-in health checks monitor:
- Discord connection status
- BigQuery operation success rates
- Data buffer sizes
- Task execution intervals

## 🏗️ Architecture

### Data Flow

```
Discord Events → Event Handlers → Data Buffer → Periodic Tasks → BigQuery
```

1. **Event Collection**: Discord events are captured by specialized handlers
2. **Data Buffering**: Events are stored in thread-safe in-memory buffers
3. **Batch Processing**: Configurable intervals trigger BigQuery uploads
4. **Data Storage**: Smart merging prevents duplicates and handles updates

### Key Components

- **Event Handlers**: Process specific Discord events (messages, members, voice, etc.)
- **Data Buffer**: Thread-safe storage for events before BigQuery upload
- **BigQuery Service**: Handles database operations with error recovery
- **Task Scheduler**: Manages periodic data uploads with intelligent delays

## 🔐 Security Best Practices

### Environment Variables
- **Never commit** `.env` files or service account keys to version control
- Use **strong, unique** Discord bot tokens
- **Regularly rotate** authentication credentials
- **Review BigQuery permissions** to ensure least privilege access

### Data Privacy
- **Message content** is stored - ensure compliance with your organization's data policy
- Consider **data retention policies** for BigQuery tables
- **Audit access** to BigQuery datasets regularly

### Container Security
- Bot runs as **non-root user** in container
- **Resource limits** prevent excessive memory/CPU usage
- **Health checks** ensure container reliability

## 🛠️ Development

### Adding New Event Types

1. Create handler in `src/handlers/`
2. Add buffer methods in `src/services/data_buffer.py`
3. Implement BigQuery operations in `src/services/bigquery_service.py`
4. Update schemas in `src/config/bigquery_config.py`
5. Register handler in `src/bot.py`

### Debugging

```bash
# Enable debug logging
LOG_LEVEL=DEBUG

# Run locally for development
cd src
python main.py
```

## 📈 Performance Optimization

### BigQuery Costs
- Adjust **task intervals** based on your usage patterns
- Use **table prefixes** for environment separation
- Monitor **query costs** in BigQuery console
- Consider **partitioning** large tables by date

### Memory Management
- **Data buffers** are cleared after each upload cycle
- **Automatic cleanup** of temporary tables
- **Resource limits** in Docker configuration

## 🐛 Troubleshooting

### Common Issues

**Bot won't start:**
- Verify Discord bot token and server ID
- Check BigQuery project ID and authentication
- Ensure all required permissions are granted

**No data in BigQuery:**
- Verify table creation permissions
- Check BigQuery logs for error details
- Confirm dataset exists and is accessible

**High memory usage:**
- Reduce task intervals for more frequent data uploads
- Check for large voice channel sessions
- Monitor buffer sizes in logs

**Authentication errors:**
- Validate service account JSON format
- Ensure service account has BigQuery Data Editor role
- Check file path for `GOOGLE_APPLICATION_CREDENTIALS`

### Getting Support

1. **Check logs** for specific error messages
2. **Verify configuration** against `.env.example`
3. **Test BigQuery permissions** with a simple query
4. **Enable DEBUG logging** for detailed troubleshooting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow commit message conventions (see project guidelines)
4. Add tests for new functionality
5. Submit a pull request

## 🔄 Version History

- **v1.0**: Initial release with core analytics features
- **v1.1**: Added Docker support and advanced logging
- **v1.2**: Enhanced error handling and data filtering
- **Current**: Production-ready with comprehensive monitoring