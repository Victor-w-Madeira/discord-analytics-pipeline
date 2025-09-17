import discord
from datetime import datetime, timezone
from config.settings import TARGET_SERVER_ID
from config.logging_config import BotLogger

class PresenceHandler:
    """Handler for Discord presence events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
        self.logger = BotLogger(__name__)
    
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        """Handle presence status changes."""
        # Filter by target server
        if after.guild.id != TARGET_SERVER_ID:
            return
        
        try:
            # Detect transition from offline to online
            if before.status == discord.Status.offline and after.status == discord.Status.online:
                presence_data = {
                    'logged_at': datetime.now(timezone.utc),  
                    'user_id': str(after.id),
                    'user_name': after.name
                }
                
                await self.data_buffer.add_presence_log(presence_data)
                
                self.logger.user_activity("came online", str(after.id))
            
            # Log other significant status changes (debug level)
            elif before.status != after.status:
                self.logger.user_activity(
                    f"status changed", 
                    str(after.id), 
                    f"from {before.status} to {after.status}"
                )
                
        except Exception as e:
            self.logger.error(f"process presence update for {after.display_name}", e, f"user {after.id}")