import discord
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ThreadHandler:
    """Handler for Discord thread events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
    
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
            logger.info(f"Thread created: {thread.name} ({thread.id})")
            
        except Exception as e:
            logger.error(f"Error processing thread creation for {thread.id}: {e}")