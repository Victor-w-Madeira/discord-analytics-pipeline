import pandas as pd
import asyncio
from typing import Dict, Any

class DataBuffer:
    """Thread-safe data buffer for storing Discord events before BigQuery upload."""
    
    def __init__(self):
        self._lock = asyncio.Lock()
        self._init_buffers()
    
    def _init_buffers(self):
        """Initialize all data buffers."""
        self.members_buffer = pd.DataFrame(columns=[
            'user_id', 'user_name', 'display_name', 'is_bot', 
            'is_booster', 'role', 'joined_at', 'status', 'updated_at'
        ])
        
        self.member_updates_buffer = pd.DataFrame(columns=[
            'user_id', 'column', 'new_value', 'updated_at'
        ])
        
        self.message_counts_buffer = pd.DataFrame(columns=[
            'date', 'user_id', 'channel_id', 'message_count'
        ])
        
        self.message_details_buffer = pd.DataFrame(columns=[
            'message_id', 'created_at', 'user_id', 'channel_id', 
            'thread_id', 'message_content'
        ])
        
        self.voice_buffer = pd.DataFrame(columns=[
            'date', 'user_id', 'channel_id', 'duration_seconds'
        ])
        
        self.thread_buffer = pd.DataFrame(columns=[
            'created_at', 'user_id', 'thread_name', 'channel_id', 'thread_id'
        ])
        
        self.presence_buffer = pd.DataFrame(columns=[
            'logged_at', 'user_id', 'user_name'
        ])
    
    async def add_member(self, member_data: Dict[str, Any]):
        """Add member data to buffer."""
        async with self._lock:
            new_data = pd.DataFrame([member_data])
            self.members_buffer = pd.concat([self.members_buffer, new_data], ignore_index=True)
    
    async def add_member_update(self, update_data: Dict[str, Any]):
        """Add member update to buffer."""
        async with self._lock:
            new_data = pd.DataFrame([update_data])
            self.member_updates_buffer = pd.concat([self.member_updates_buffer, new_data], ignore_index=True)
    
    async def add_message_count(self, message_data: Dict[str, Any]):
        """Add or update message count in buffer."""
        async with self._lock:
            date = message_data['date']
            user_id = message_data['user_id']
            channel_id = message_data['channel_id']
            
            # Check if record exists
            mask = (
                (self.message_counts_buffer['date'] == date) &
                (self.message_counts_buffer['user_id'] == user_id) &
                (self.message_counts_buffer['channel_id'] == channel_id)
            )
            
            if mask.any():
                self.message_counts_buffer.loc[mask, 'message_count'] += 1
            else:
                new_data = pd.DataFrame([{**message_data, 'message_count': 1}])
                self.message_counts_buffer = pd.concat([self.message_counts_buffer, new_data], ignore_index=True)
    
    async def add_message_detail(self, message_data: Dict[str, Any]):
        """Add message detail to buffer."""
        async with self._lock:
            new_data = pd.DataFrame([message_data])
            self.message_details_buffer = pd.concat([self.message_details_buffer, new_data], ignore_index=True)
    
    async def add_voice_activity(self, voice_data: Dict[str, Any]):
        """Add or update voice activity in buffer."""
        async with self._lock:
            date = voice_data['date']
            user_id = voice_data['user_id']
            channel_id = voice_data['channel_id']
            duration = voice_data['duration_seconds']
            
            # Check if record exists
            mask = (
                (self.voice_buffer['date'] == date) &
                (self.voice_buffer['user_id'] == user_id) &
                (self.voice_buffer['channel_id'] == channel_id)
            )
            
            if mask.any():
                self.voice_buffer.loc[mask, 'duration_seconds'] += duration
            else:
                new_data = pd.DataFrame([voice_data])
                self.voice_buffer = pd.concat([self.voice_buffer, new_data], ignore_index=True)
    
    async def add_thread(self, thread_data: Dict[str, Any]):
        """Add thread data to buffer."""
        async with self._lock:
            new_data = pd.DataFrame([thread_data])
            self.thread_buffer = pd.concat([self.thread_buffer, new_data], ignore_index=True)
    
    async def add_presence_log(self, presence_data: Dict[str, Any]):
        """Add presence log to buffer."""
        async with self._lock:
            new_data = pd.DataFrame([presence_data])
            self.presence_buffer = pd.concat([self.presence_buffer, new_data], ignore_index=True)
    
    # Getter methods
    def get_members_data(self) -> pd.DataFrame:
        return self.members_buffer.copy()
    
    def get_member_updates(self) -> pd.DataFrame:
        return self.member_updates_buffer.copy()
    
    def get_message_counts(self) -> pd.DataFrame:
        return self.message_counts_buffer.copy()
    
    def get_message_details(self) -> pd.DataFrame:
        return self.message_details_buffer.copy()
    
    def get_voice_data(self) -> pd.DataFrame:
        return self.voice_buffer.copy()
    
    def get_thread_data(self) -> pd.DataFrame:
        return self.thread_buffer.copy()
    
    def get_presence_data(self) -> pd.DataFrame:
        return self.presence_buffer.copy()
    
    # Clear methods
    def clear_members_data(self):
        self.members_buffer = pd.DataFrame(columns=self.members_buffer.columns)
        self.member_updates_buffer = pd.DataFrame(columns=self.member_updates_buffer.columns)
    
    def clear_message_data(self):
        self.message_counts_buffer = pd.DataFrame(columns=self.message_counts_buffer.columns)
        self.message_details_buffer = pd.DataFrame(columns=self.message_details_buffer.columns)
    
    def clear_voice_data(self):
        self.voice_buffer = pd.DataFrame(columns=self.voice_buffer.columns)
    
    def clear_thread_data(self):
        self.thread_buffer = pd.DataFrame(columns=self.thread_buffer.columns)
    
    def clear_presence_data(self):
        self.presence_buffer = pd.DataFrame(columns=self.presence_buffer.columns)