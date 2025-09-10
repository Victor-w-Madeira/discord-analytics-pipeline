# src/handlers/message_handler.py
import discord
import logging
from datetime import datetime, timezone
from config.settings import TARGET_SERVER_ID

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handler for Discord message events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
    
    async def on_message(self, message: discord.Message):
        """Handle message creation events."""
        # Filter by target server
        if not message.guild or message.guild.id != TARGET_SERVER_ID:
            return
        
        # Skip bot messages
        if message.author.bot:
            return
        
        try:
            await self._process_message_count(message)
            await self._process_message_details(message)
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
    
    async def _process_message_count(self, message: discord.Message):
        """Process message for counting purposes."""
        channel_id, _ = self._get_channel_info(message)
        
        message_data = {
            'date': message.created_at.date(),
            'user_id': str(message.author.id),
            'channel_id': channel_id
        }
        
        await self.data_buffer.add_message_count(message_data)
    
    async def _process_message_details(self, message: discord.Message):
        """Process detailed message information."""
        channel_id, thread_id = self._get_channel_info(message)
        
        message_data = {
            'message_id': str(message.id),
            'created_at': message.created_at,
            'user_id': str(message.author.id),
            'channel_id': channel_id,
            'thread_id': thread_id,
            'message_content': message.content
        }
        
        await self.data_buffer.add_message_detail(message_data)
    
    def _get_channel_info(self, message: discord.Message) -> tuple[str, str]:
        """Extract channel and thread information from message."""
        if message.channel.type.name in ["public_thread", "private_thread", "news_thread"]:
            return str(message.channel.parent_id), str(message.channel.id)
        else:
            return str(message.channel.id), ""