import logging
import sys
from datetime import datetime
from typing import Dict, Any

class DiscordBotFormatter(logging.Formatter):
    """Custom formatter for Discord Analytics Bot logs."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    # Icons for different types of operations
    ICONS = {
        'bot': '🤖',
        'bigquery': '📊',
        'discord': '💬',
        'voice': '🎙️',
        'member': '👥',
        'thread': '🧵',
        'message': '💌',
        'presence': '🟢',
        'error': '❌',
        'warning': '⚠️',
        'success': '✅',
        'info': 'ℹ️',
        'timing': '⏱️'
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and icons."""
        # Get timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Determine category and icon
        category, icon = self._categorize_record(record)
        
        # Format level with color
        level_str = self._format_level(record.levelname)
        
        # Create the main message
        message = self._format_message(record, category)
        
        # Combine all parts
        if self.use_colors:
            return f"{self.COLORS.get(record.levelname, '')}{timestamp} {icon} [{level_str}] {message}{self.COLORS['RESET']}"
        else:
            return f"{timestamp} {icon} [{record.levelname}] {message}"
    
    def _categorize_record(self, record: logging.LogRecord) -> tuple[str, str]:
        """Categorize log record and return category and appropriate icon."""
        module_name = record.name.lower()
        message = record.getMessage().lower()
        
        # Error and warning handling
        if record.levelno >= logging.ERROR:
            return 'error', self.ICONS['error']
        elif record.levelno >= logging.WARNING:
            return 'warning', self.ICONS['warning']
        
        # Module-based categorization
        if 'bigquery' in module_name:
            return 'bigquery', self.ICONS['bigquery']
        elif 'voice' in module_name or 'voice' in message:
            return 'voice', self.ICONS['voice']
        elif 'member' in module_name or 'member' in message:
            return 'member', self.ICONS['member']
        elif 'thread' in module_name or 'thread' in message:
            return 'thread', self.ICONS['thread']
        elif 'message' in module_name or 'message' in message:
            return 'message', self.ICONS['message']
        elif 'presence' in module_name or 'presence' in message:
            return 'presence', self.ICONS['presence']
        elif 'bot' in module_name:
            return 'bot', self.ICONS['bot']
        
        # Content-based categorization
        if 'completed in' in message or 'duration' in message:
            return 'timing', self.ICONS['timing']
        elif 'successfully' in message or 'started' in message:
            return 'success', self.ICONS['success']
        elif 'connected' in message:
            return 'bot', self.ICONS['bot']
        
        return 'info', self.ICONS['info']
    
    def _format_level(self, level: str) -> str:
        """Format log level string."""
        level_map = {
            'DEBUG': 'DBG',
            'INFO': 'INF',
            'WARNING': 'WRN',
            'ERROR': 'ERR',
            'CRITICAL': 'CRT'
        }
        return level_map.get(level, level[:3])
    
    def _format_message(self, record: logging.LogRecord, category: str) -> str:
        """Format the main log message."""
        message = record.getMessage()
        
        # Special formatting for different types of messages
        if 'completed in' in message:
            return self._format_timing_message(message)
        elif 'successfully' in message.lower():
            return self._format_success_message(message)
        elif 'error' in message.lower() and record.levelno >= logging.ERROR:
            return self._format_error_message(message)
        elif category == 'bot' and ('connected' in message or 'started' in message):
            return self._format_bot_message(message)
        
        return message
    
    def _format_timing_message(self, message: str) -> str:
        """Format timing-related messages."""
        # Extract function name and duration
        parts = message.split(' completed in ')
        if len(parts) == 2:
            func_name = parts[0].replace('_', ' ').title()
            duration = parts[1]
            return f"{func_name} completed in {duration}"
        return message
    
    def _format_success_message(self, message: str) -> str:
        """Format success messages."""
        return message
    
    def _format_error_message(self, message: str) -> str:
        """Format error messages."""
        return f"ERROR: {message}"
    
    def _format_bot_message(self, message: str) -> str:
        """Format bot-related messages."""
        return message


def setup_logging(level: str = 'INFO', use_colors: bool = True) -> None:
    """Setup logging configuration for the Discord Analytics Bot."""
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create custom formatter
    formatter = DiscordBotFormatter(use_colors=use_colors)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    
    # Setup file handler (without colors)
    try:
        import os
        os.makedirs('logs', exist_ok=True)
        
        file_formatter = DiscordBotFormatter(use_colors=False)
        file_handler = logging.FileHandler('logs/discord-bot.log', encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(numeric_level)
        
        # Setup error file handler
        error_handler = logging.FileHandler('logs/error.log', encoding='utf-8')
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.ERROR)
        
        handlers = [console_handler, file_handler, error_handler]
    except Exception:
        handlers = [console_handler]
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Reduce noise from external libraries
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


# Convenience functions for different types of logging
class BotLogger:
    """Convenience logger methods for common bot operations."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def bot_ready(self, bot_name: str, guild_count: int):
        """Log when bot is ready."""
        self.logger.info(f"Bot '{bot_name}' is ready! Connected to {guild_count} server(s)")
    
    def guild_connected(self, guild_name: str, guild_id: int):
        """Log guild connection."""
        self.logger.info(f"Connected to server: {guild_name} (ID: {guild_id})")
    
    def task_started(self, task_name: str, interval: int):
        """Log when a periodic task starts."""
        self.logger.info(f"Started {task_name.replace('_', ' ')} with {interval} minute interval")
    
    def data_processed(self, operation: str, count: int, table: str = None):
        """Log data processing results."""
        if table:
            self.logger.info(f"Successfully processed {count} {operation} records → {table}")
        else:
            self.logger.info(f"Successfully processed {count} {operation} records")
    
    def no_data(self, operation: str):
        """Log when there's no data to process."""
        self.logger.debug(f"No {operation} data to process")
    
    def timing(self, operation: str, minutes: int, seconds: int):
        """Log operation timing."""
        if minutes > 0:
            self.logger.info(f"{operation.replace('_', ' ').title()} completed in {minutes}m {seconds}s")
        else:
            self.logger.info(f"{operation.replace('_', ' ').title()} completed in {seconds}s")
    
    def user_activity(self, activity_type: str, user_id: str, details: str = None):
        """Log user activity."""
        if details:
            self.logger.debug(f"User {user_id} {activity_type}: {details}")
        else:
            self.logger.debug(f"User {user_id} {activity_type}")
    
    def error(self, operation: str, error: Exception, context: str = None):
        """Log errors with context."""
        if context:
            self.logger.error(f"Failed to {operation} ({context}): {error}")
        else:
            self.logger.error(f"Failed to {operation}: {error}")