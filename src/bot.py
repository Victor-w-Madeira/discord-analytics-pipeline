import discord
import asyncio
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
from config.logging_config import BotLogger

class DiscordAnalyticsBot(commands.Bot):
    """Main Discord bot class for analytics collection."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.presences = True
        intents.guilds = True
        intents.message_content = True
        
        super().__init__(command_prefix='!', intents=intents)
        
        # Initialize logger
        self.logger = BotLogger(__name__)
        
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
    
    def _calculate_task_delays(self):
        """Calculate appropriate delays between tasks based on intervals."""
        # Encontra o menor intervalo entre todas as tarefas
        intervals = [
            MEMBER_UPDATE_INTERVAL,
            MESSAGE_UPDATE_INTERVAL,
            VOICE_UPDATE_INTERVAL,
            THREAD_UPDATE_INTERVAL,
            PRESENCE_UPDATE_INTERVAL
        ]
        min_interval = min(intervals)
        
        # Calcula delay apropriado baseado no menor intervalo
        if min_interval <= 5:  # Para testes (≤ 5 minutos)
            base_delay = 10  # 10 segundos entre tarefas
        elif min_interval <= 15:  # Intervalos médios (≤ 15 minutos)  
            base_delay = 30  # 30 segundos entre tarefas
        else:  # Produção (≥ 16 minutos) - inclui o padrão de 60 min
            base_delay = 300  # 5 minutos entre tarefas
            
        self.logger.logger.info(f"📊 Calculated task delay: {base_delay}s (based on min interval: {min_interval}min)")
        return base_delay
    
    async def on_ready(self):
        """Event triggered when bot is ready."""
        self.logger.bot_ready(self.user.name, len(self.guilds))
        
        for guild in self.guilds:
            self.logger.guild_connected(guild.name, guild.id)
        
        # Log the configured intervals
        self.logger.logger.info("⚙️ Task Configuration:")
        intervals = [
            ("Members", MEMBER_UPDATE_INTERVAL),
            ("Messages", MESSAGE_UPDATE_INTERVAL), 
            ("Voice Activity", VOICE_UPDATE_INTERVAL),
            ("Threads", THREAD_UPDATE_INTERVAL),
            ("Presence Logs", PRESENCE_UPDATE_INTERVAL)
        ]
        
        for name, interval in intervals:
            self.logger.logger.info(f"   • {name}: {interval} minutes")
        
        # Start periodic tasks
        await self._start_periodic_tasks()
    
    async def _start_periodic_tasks(self):
        """Start all periodic update tasks with intelligent delays."""
        self.logger.logger.info("🔄 Starting periodic tasks...")
        
        # Calculate appropriate delay between tasks
        task_delay = self._calculate_task_delays()
        
        # Start heartbeat log cycle (sempre 1 hora, independente dos outros intervalos)
        heartbeat_interval = max(60, min(MEMBER_UPDATE_INTERVAL, MESSAGE_UPDATE_INTERVAL) * 10)
        self.log_update_cycle.change_interval(minutes=heartbeat_interval)
        self.log_update_cycle.start()
        self.logger.logger.debug(f"Started heartbeat log cycle ({heartbeat_interval} min interval)")
        
        # Define tasks with their respective intervals and calculated delays
        tasks = [
            ("update_members", MEMBER_UPDATE_INTERVAL, task_delay * 0),      # Inicia imediatamente
            ("update_messages", MESSAGE_UPDATE_INTERVAL, task_delay * 1),    # 1 delay
            ("update_voice_activity", VOICE_UPDATE_INTERVAL, task_delay * 2), # 2 delays
            ("update_threads", THREAD_UPDATE_INTERVAL, task_delay * 3),      # 3 delays
            ("update_presence_logs", PRESENCE_UPDATE_INTERVAL, task_delay * 4) # 4 delays
        ]
        
        # Log the schedule
        self.logger.logger.info("📅 Task Schedule:")
        for task_name, interval, delay in tasks:
            friendly_name = task_name.replace('update_', '').replace('_', ' ').title()
            delay_str = f"{int(delay)}s" if delay < 60 else f"{int(delay/60)}m"
            self.logger.logger.info(f"   • {friendly_name}: starts in {delay_str}, then every {interval}min")
        
        # Start tasks with calculated delays
        for task_name, interval, delay in tasks:
            if delay > 0:
                self.logger.logger.debug(f"⏳ Waiting {int(delay)}s before starting {task_name}")
                await asyncio.sleep(delay)
            
            task = getattr(self, task_name)
            task.change_interval(minutes=interval)
            task.start()
            
            friendly_name = task_name.replace('update_', '').replace('_', ' ').title()
            self.logger.logger.info(f"✅ Started {friendly_name} (every {interval}min)")
        
        self.logger.logger.info("🎯 All periodic tasks started successfully")
    
    @tasks.loop()
    async def log_update_cycle(self):
        """Log periodic heartbeat."""
        # Mostra informações mais úteis no heartbeat
        total_tasks = 5
        active_tasks = sum(1 for task in [
            self.update_members.is_running(),
            self.update_messages.is_running(),
            self.update_voice_activity.is_running(),
            self.update_threads.is_running(),
            self.update_presence_logs.is_running()
        ] if task)
        
        self.logger.logger.info(f"💓 System Health: {active_tasks}/{total_tasks} tasks running")
    
    @tasks.loop()
    async def update_members(self):
        """Update member data in BigQuery."""
        self.logger.logger.info("👥 Starting member data update process...")
        
        try:
            members_data = self.data_buffer.get_members_data()
            updates_data = self.data_buffer.get_member_updates()
            
            if not members_data.empty or not updates_data.empty:
                await self.bigquery_service.update_members(members_data, updates_data)
                self.data_buffer.clear_members_data()
            else:
                self.logger.logger.info("👥 Member update process completed - No data to load")
                
        except Exception as e:
            self.logger.error("update members task", e)
    
    @tasks.loop()
    async def update_messages(self):
        """Update message data in BigQuery."""
        self.logger.logger.info("💌 Starting message data update process...")
        
        try:
            counts_data = self.data_buffer.get_message_counts()
            details_data = self.data_buffer.get_message_details()
            
            if not counts_data.empty or not details_data.empty:
                if not counts_data.empty:
                    await self.bigquery_service.update_message_counts(counts_data)
                if not details_data.empty:
                    await self.bigquery_service.update_message_details(details_data)
                self.data_buffer.clear_message_data()
            else:
                self.logger.logger.info("💌 Message update process completed - No data to load")
                
        except Exception as e:
            self.logger.error("update messages task", e)
    
    @tasks.loop()
    async def update_voice_activity(self):
        """Update voice activity data in BigQuery."""
        self.logger.logger.info("🎙️ Starting voice activity update process...")
        
        try:
            voice_data = self.data_buffer.get_voice_data()
            
            if not voice_data.empty:
                await self.bigquery_service.update_voice_activity(voice_data)
                self.data_buffer.clear_voice_data()
            else:
                self.logger.logger.info("🎙️ Voice activity update process completed - No data to load")
                
        except Exception as e:
            self.logger.error("update voice activity task", e)
    
    @tasks.loop()
    async def update_threads(self):
        """Update thread data in BigQuery."""
        self.logger.logger.info("🧵 Starting thread data update process...")
        
        try:
            thread_data = self.data_buffer.get_thread_data()
            
            if not thread_data.empty:
                await self.bigquery_service.update_threads(thread_data)
                self.data_buffer.clear_thread_data()
            else:
                self.logger.logger.info("🧵 Thread update process completed - No data to load")
                
        except Exception as e:
            self.logger.error("update threads task", e)
    
    @tasks.loop()
    async def update_presence_logs(self):
        """Update presence logs in BigQuery."""
        self.logger.logger.info("🟢 Starting presence logs update process...")
        
        try:
            presence_data = self.data_buffer.get_presence_data()
            
            if not presence_data.empty:
                await self.bigquery_service.update_presence_logs(presence_data)
                self.data_buffer.clear_presence_data()
            else:
                self.logger.logger.info("🟢 Presence logs update process completed - No data to load")
                
        except Exception as e:
            self.logger.error("update presence logs task", e)