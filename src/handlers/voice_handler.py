import discord
from datetime import datetime, timezone
from config.settings import TARGET_SERVER_ID
from config.logging_config import BotLogger
from utils.helpers import format_duration

class VoiceHandler:
    """Handler for Discord voice state events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
        self.voice_entry_times = {}
        self.logger = BotLogger(__name__)
    
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state updates."""
        # Filter by target server
        if not member.guild or member.guild.id != TARGET_SERVER_ID:
            return
        
        try:
            user_id = str(member.id)
            
            # User joins a voice channel
            if before.channel is None and after.channel is not None:
                await self._handle_voice_join(user_id, member.display_name, after.channel)
            
            # User leaves a voice channel
            elif before.channel is not None and after.channel is None:
                await self._handle_voice_leave(user_id, member.display_name, before.channel)
            
            # User switches voice channels
            elif before.channel != after.channel and before.channel is not None and after.channel is not None:
                await self._handle_voice_leave(user_id, member.display_name, before.channel)
                await self._handle_voice_join(user_id, member.display_name, after.channel)
                
                # Log channel switch
                self.logger.user_activity(
                    "switched voice channels", 
                    user_id, 
                    f"from '{before.channel.name}' to '{after.channel.name}'"
                )
                
        except Exception as e:
            self.logger.error(f"process voice state update for {member.display_name}", e, f"user {member.id}")
    
    async def _handle_voice_join(self, user_id: str, display_name: str, channel: discord.VoiceChannel):
        """Handle user joining voice channel."""
        entry_time = datetime.now(timezone.utc)
        self.voice_entry_times[user_id] = (str(channel.id), entry_time)
        
        self.logger.user_activity("joined voice channel", user_id, f"'{channel.name}'")
    
    async def _handle_voice_leave(self, user_id: str, display_name: str, channel: discord.VoiceChannel):
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
        
        # Log with human-readable duration
        duration_str = format_duration(duration)
        self.logger.user_activity(
            "left voice channel", 
            user_id, 
            f"'{channel.name}' after {duration_str}"
        )