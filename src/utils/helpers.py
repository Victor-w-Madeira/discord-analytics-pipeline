import time
from functools import wraps
from config.logging_config import BotLogger

def log_execution_time(func):
    """Decorator to log execution time of functions with improved formatting."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get logger from the class instance if available
        if args and hasattr(args[0], '__class__'):
            logger = BotLogger(f"{args[0].__class__.__module__}.{args[0].__class__.__name__}")
        else:
            logger = BotLogger(func.__module__)
        
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            # Use the improved timing method
            logger.timing(func.__name__, minutes, seconds)
            
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            
            logger.error(f"{func.__name__} (failed after {minutes}m {seconds}s)", e)
            raise
    return wrapper

def format_roles(roles: list) -> str:
    """Format Discord roles list to string."""
    return ", ".join([role.name for role in roles if role.name != "@everyone"])

def format_duration(seconds: int) -> str:
    """Format duration in seconds to a human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"

def format_count(count: int, singular: str, plural: str = None) -> str:
    """Format count with proper singular/plural form."""
    if plural is None:
        plural = f"{singular}s"
    
    if count == 1:
        return f"{count} {singular}"
    return f"{count} {plural}"