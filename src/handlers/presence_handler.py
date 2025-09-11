import discord
import pandas as pd
import logging
import asyncio
from datetime import datetime, timezone
from config.settings import TARGET_SERVER_ID

logger = logging.getLogger(__name__)

class PresenceHandler:
    """Handler for Discord presence events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
        # Remoção do lock individual - DataBuffer já é thread-safe
        # self.presence_lock = asyncio.Lock()  # Não necessário
    
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """Handle presence status changes."""
        # Filter by target server
        if after.guild.id != TARGET_SERVER_ID:
            return
        
        try:
            # Detect transition from offline to online
            if before.status == discord.Status.offline and after.status == discord.Status.online:
                presence_data = {
                    'logged_at': pd.Timestamp.now(tz=timezone.utc),  # Mais explícito com timezone
                    'user_id': str(after.id),
                    'user_name': after.name
                }
                
                await self.data_buffer.add_presence_log(presence_data)
                logger.debug(f"User {after.name} ({after.id}) came online")
                
        except Exception as e:
            logger.error(f"Error processing presence update for {after.id}: {e}")
            # Opcional: Re-raise se quiser que falhas parem o bot
            # raise