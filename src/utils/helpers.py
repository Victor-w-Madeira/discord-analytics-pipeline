import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_execution_time(func):
    """Decorator to log execution time of functions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            minutes, seconds = divmod(duration, 60)
            logger.info(f"{func.__name__} completed in {int(minutes)}:{int(seconds):02d}")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            minutes, seconds = divmod(duration, 60)
            logger.error(f"{func.__name__} failed after {int(minutes)}:{int(seconds):02d} - {e}")
            raise
    return wrapper

def sanitize_string(text: str) -> str:
    """Sanitize string for BigQuery insertion."""
    if not text:
        return ""
    return text.replace("'", "\\'").replace('"', '\\"')

def format_roles(roles: list) -> str:
    """Format Discord roles list to string."""
    return ", ".join([role.name for role in roles if role.name != "@everyone"])