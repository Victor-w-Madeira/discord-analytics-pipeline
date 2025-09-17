import discord
import asyncio
import logging
from discord.ext import commands, tasks

from config.settings import (
    MEMBER_UPDATE_INTERVAL,
    MESSAGE_UPDATE_INTERVAL,
    VOICE_UPDATE_INTERVAL,
    THREAD_UPDATE_INTERVAL,
    PRESENCE_UPDATE_INTERVAL
)
from handlers import (
    MessageHandler, 
    MemberHandler, 
    VoiceHandler, 
    ThreadHandler, 
    PresenceHandler
)
from services.bigquery_service import BigQueryService
from services.data_buffer import DataBuffer

logger = logging.getLogger(__name__)

class DiscordAnalyticsBot(commands.Bot):
    """Main Discord bot class for analytics collection."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        intents.guilds = True
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize services
        self.bigquery_service = BigQueryService()
        self.data_buffer = DataBuffer()
        
        # Initialize handlers
        self.message_handler = MessageHandler(self.data_buffer)
        self.member_handler = MemberHandler(self.data_buffer)
        self.voice_handler = VoiceHandler(self.data_buffer)
        self.thread_handler = ThreadHandler(self.data_buffer)
        self.presence_handler = PresenceHandler(self.data_buffer)
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup all event handlers."""
        self.add_listener(self.on_ready)
        self.add_listener(self.message_handler.on_message)
        self.add_listener(self.member_handler.on_member_join)
        self.add_listener(self.member_handler.on_member_remove)
        self.add_listener(self.member_handler.on_user_update)
        self.add_listener(self.voice_handler.on_voice_state_update)
        self.add_listener(self.thread_handler.on_thread_create)
        self.add_listener(self.presence_handler.on_presence_update)
    
    async def on_ready(self):
        """Event triggered when bot is ready."""
        logger.info(f'Bot connected as {self.user}')
        
        for guild in self.guilds:
            logger.info(f'Connected to server: {guild.name} (ID: {guild.id})')
        
        # Log the configured intervals
        logger.info(f"Task intervals configured:")
        logger.info(f"  - Members: {MEMBER_UPDATE_INTERVAL} minutes")
        logger.info(f"  - Messages: {MESSAGE_UPDATE_INTERVAL} minutes")
        logger.info(f"  - Voice: {VOICE_UPDATE_INTERVAL} minutes")
        logger.info(f"  - Threads: {THREAD_UPDATE_INTERVAL} minutes")
        logger.info(f"  - Presence: {PRESENCE_UPDATE_INTERVAL} minutes")
        
        # Start periodic tasks
        await self._start_periodic_tasks()
    
    async def _start_periodic_tasks(self):
        """Start all periodic update tasks with staggered delays."""
        logger.info("Starting periodic tasks...")
        
        # Start log cycle first
        self.log_update_cycle.change_interval(minutes=60)
        self.log_update_cycle.start()
        logger.info("Started log_update_cycle")
        
        # Wait 1 minute then start member updates
        await asyncio.sleep(60)
        self.update_members.change_interval(minutes=MEMBER_UPDATE_INTERVAL)
        self.update_members.start()
        logger.info(f"Started update_members with interval {MEMBER_UPDATE_INTERVAL} minutes")
        
        # Wait 5 minutes then start message updates
        await asyncio.sleep(300)  
        self.update_messages.change_interval(minutes=MESSAGE_UPDATE_INTERVAL)
        self.update_messages.start()
        logger.info(f"Started update_messages with interval {MESSAGE_UPDATE_INTERVAL} minutes")
        
        # Wait 5 minutes then start voice updates
        await asyncio.sleep(300)
        self.update_voice_activity.change_interval(minutes=VOICE_UPDATE_INTERVAL)
        self.update_voice_activity.start()
        logger.info(f"Started update_voice_activity with interval {VOICE_UPDATE_INTERVAL} minutes")
        
        # Wait 5 minutes then start thread updates
        await asyncio.sleep(300)
        self.update_threads.change_interval(minutes=THREAD_UPDATE_INTERVAL)
        self.update_threads.start()
        logger.info(f"Started update_threads with interval {THREAD_UPDATE_INTERVAL} minutes")
        
        # Wait 5 minutes then start presence updates
        await asyncio.sleep(300)
        self.update_presence_logs.change_interval(minutes=PRESENCE_UPDATE_INTERVAL)
        self.update_presence_logs.start()
        logger.info(f"Started update_presence_logs with interval {PRESENCE_UPDATE_INTERVAL} minutes")
        
        logger.info("All periodic tasks started successfully")
    
    @tasks.loop()
    async def log_update_cycle(self):
        """Log periodic update cycle."""
        logger.info("Periodic update cycle started")
    
    @tasks.loop()
    async def update_members(self):
        """Update member data in BigQuery."""
        try:
            await self.bigquery_service.update_members(
                self.data_buffer.get_members_data(),
                self.data_buffer.get_member_updates()
            )
            self.data_buffer.clear_members_data()
        except Exception as e:
            logger.error(f"Error in update_members: {e}")
    
    @tasks.loop()
    async def update_messages(self):
        """Update message data in BigQuery."""
        try:
            await self.bigquery_service.update_message_counts(
                self.data_buffer.get_message_counts()
            )
            await self.bigquery_service.update_message_details(
                self.data_buffer.get_message_details()
            )
            self.data_buffer.clear_message_data()
        except Exception as e:
            logger.error(f"Error in update_messages: {e}")
    
    @tasks.loop()
    async def update_voice_activity(self):
        """Update voice activity data in BigQuery."""
        try:
            await self.bigquery_service.update_voice_activity(
                self.data_buffer.get_voice_data()
            )
            self.data_buffer.clear_voice_data()
        except Exception as e:
            logger.error(f"Error in update_voice_activity: {e}")
    
    @tasks.loop()
    async def update_threads(self):
        """Update thread data in BigQuery."""
        try:
            await self.bigquery_service.update_threads(
                self.data_buffer.get_thread_data()
            )
            self.data_buffer.clear_thread_data()
        except Exception as e:
            logger.error(f"Error in update_threads: {e}")
    
    @tasks.loop()
    async def update_presence_logs(self):
        """Update presence logs in BigQuery."""
        try:
            await self.bigquery_service.update_presence_logs(
                self.data_buffer.get_presence_data()
            )
            self.data_buffer.clear_presence_data()
        except Exception as e:
            logger.error(f"Error in update_presence_logs: {e}")