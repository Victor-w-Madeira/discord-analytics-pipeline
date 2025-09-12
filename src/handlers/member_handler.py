import discord
import logging
from datetime import datetime, timezone
from config.settings import TARGET_SERVER_ID
from utils.helpers import format_roles

logger = logging.getLogger(__name__)

class MemberHandler:
    """Handler for Discord member events."""
    
    def __init__(self, data_buffer):
        self.data_buffer = data_buffer
    
    async def on_member_join(self, member: discord.Member):
        """Handle member join events."""
        if member.guild.id != TARGET_SERVER_ID:
            return
        
        try:
            member_data = {
                'user_id': str(member.id),
                'user_name': member.name,
                'display_name': member.display_name or member.name,
                'is_bot': member.bot,
                'is_booster': member.premium_since is not None,
                'role': format_roles(member.roles),
                'joined_at': member.joined_at or datetime.now(timezone.utc),
                'status': str(member.status),
                'updated_at': datetime.now(timezone.utc)
            }
            
            await self.data_buffer.add_member(member_data)
            logger.info(f"Member joined: {member.name} ({member.id})")
            
        except Exception as e:
            logger.error(f"Error processing member join for {member.id}: {e}")
    
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave events."""
        if member.guild.id != TARGET_SERVER_ID:
            return
        
        try:
            # Update member status to offline/left
            update_data = {
                'user_id': str(member.id),
                'column': 'status',
                'new_value': 'left',
                'updated_at': datetime.now(timezone.utc)
            }
            
            await self.data_buffer.add_member_update(update_data)
            logger.info(f"Member left: {member.name} ({member.id})")
            
        except Exception as e:
            logger.error(f"Error processing member leave for {member.id}: {e}")
    
    async def on_user_update(self, before: discord.User, after: discord.User):
        """Handle user profile updates."""
        try:
            if before.name != after.name:
                update_data = {
                    'user_id': str(after.id),
                    'column': 'user_name',
                    'new_value': after.name,
                    'updated_at': datetime.now(timezone.utc)
                }
                await self.data_buffer.add_member_update(update_data)
            
        except Exception as e:
            logger.error(f"Error processing user update for {after.id}: {e}")