
import discord
import logging
from datetime import datetime, timezone
from config.settings import TARGET_SERVER_ID

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handler for Discord voice state events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
        self.voice_entry_times = {}
    
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state updates."""
        # Filter by target server
        if not member.guild or member.guild.id != TARGET_SERVER_ID:
            return
        
        try:
            user_id = str(member.id)
            
            # User joins a voice channel
            if before.channel is None and after.channel is not None:
                await self._handle_voice_join(user_id, after.channel)
            
            # User leaves a voice channel
            elif before.channel is not None and after.channel is None:
                await self._handle_voice_leave(user_id, before.channel)
            
            # User switches voice channels
            elif before.channel != after.channel and before.channel is not None and after.channel is not None:
                await self._handle_voice_leave(user_id, before.channel)
                await self._handle_voice_join(user_id, after.channel)
                
        except Exception as e:
            logger.error(f"Error processing voice state update for {member.id}: {e}")
    
    async def _handle_voice_join(self, user_id: str, channel: discord.VoiceChannel):
        """Handle user joining voice channel."""
        entry_time = datetime.now(timezone.utc)
        self.voice_entry_times[user_id] = (str(channel.id), entry_time)
        logger.debug(f"User {user_id} joined voice channel {channel.name}")
    
    async def _handle_voice_leave(self, user_id: str, channel: discord.VoiceChannel):
        """Handle user leaving voice channel."""
        if user_id not in self.voice_entry_times:
            return
        
        channel_id, entry_time = self.voice_entry_times.pop(user_id)
        exit_time = datetime.now(timezone.utc)
        duration = int((exit_time - entry_time).total_seconds())
        
        voice_data = {
            'date': entry_time.date(),
            'user_id': user_id,
            'channel_id': channel_id,
            'duration_seconds': duration
        }
        
        await self.data_buffer.add_voice_activity(voice_data)
        logger.debug(f"User {user_id} left voice channel after {duration} seconds")