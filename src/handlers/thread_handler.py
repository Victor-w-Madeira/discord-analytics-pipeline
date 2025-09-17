import discord
from datetime import datetime
from config.logging_config import BotLogger

class ThreadHandler:
    """Handler for Discord thread events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
        self.logger = BotLogger(__name__)
    
    async def on_thread_create(self, thread: discord.Thread):
        """Handle thread creation events."""
        try:
            created_at = thread.created_at or datetime.utcnow()
            
            thread_data = {
                'created_at': created_at,
                'user_id': str(thread.owner_id),
                'thread_name': thread.name,
                'channel_id': str(thread.parent_id),
                'thread_id': str(thread.id)
            }
            
            await self.data_buffer.add_thread(thread_data)
            
            # Get parent channel name for better context
            parent_channel = thread.parent
            parent_name = parent_channel.name if parent_channel else "Unknown"
            
            self.logger.logger.info(f"🧵 New thread created: '{thread.name}' in #{parent_name}")
            
        except Exception as e:
            self.logger.error(f"process thread creation for '{thread.name}'", e, f"thread {thread.id}")