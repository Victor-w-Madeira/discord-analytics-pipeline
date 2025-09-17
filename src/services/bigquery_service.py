import pandas as pd
from google.cloud import bigquery
from config.bigquery_config import get_bigquery_client, SCHEMAS
from config.settings import PROJECT_ID, DATASET_ID, get_table_name
from config.logging_config import BotLogger
from utils.helpers import log_execution_time, format_count

class BigQueryService:
    """Service for handling BigQuery operations."""
    
    def __init__(self):
        self.client = get_bigquery_client()
        self.project_id = PROJECT_ID
        self.dataset_id = DATASET_ID
        self.logger = BotLogger(__name__)
    
    def _get_table_id(self, table_key: str) -> str:
        """Get full table ID with optional prefix."""
        table_name = get_table_name(table_key)
        return f"{self.project_id}.{self.dataset_id}.{table_name}"
    
    @log_execution_time
    async def update_members(self, members_df: pd.DataFrame, updates_df: pd.DataFrame):
        """Update member data in BigQuery."""
        if not members_df.empty:
            await self._upsert_members(members_df)
        
        if not updates_df.empty:
            await self._update_member_fields(updates_df)
        
        if members_df.empty and updates_df.empty:
            self.logger.no_data("member")
    
    async def _upsert_members(self, members_df: pd.DataFrame):
        """Upsert member data using MERGE statement with safe parameters."""
        table_id = self._get_table_id('members')
        
        try:
            members_df = self._prepare_member_data_safe(members_df)
            
            # Process each member with parameterized MERGE query
            for _, row in members_df.iterrows():
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("user_id", "STRING", str(row['user_id'])),
                        bigquery.ScalarQueryParameter("user_name", "STRING", str(row['user_name'])),
                        bigquery.ScalarQueryParameter("display_name", "STRING", str(row['display_name'])),
                        bigquery.ScalarQueryParameter("is_bot", "BOOL", bool(row['is_bot'])),
                        bigquery.ScalarQueryParameter("is_booster", "BOOL", bool(row['is_booster'])),
                        bigquery.ScalarQueryParameter("role", "STRING", str(row['role'])),
                        bigquery.ScalarQueryParameter("joined_at", "TIMESTAMP", row['joined_at']),
                        bigquery.ScalarQueryParameter("status", "STRING", str(row['status'])),
                        bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", row['updated_at']),
                    ]
                )
                
                merge_query = self._build_safe_member_merge_query(table_id)
                query_job = self.client.query(merge_query, job_config=job_config)
                query_job.result()
            
            self.logger.data_processed("member", len(members_df), get_table_name('members'))
            
        except Exception as e:
            self.logger.error("upsert members", e)
            raise
    
    async def _update_member_fields(self, updates_df: pd.DataFrame):
        """Update specific member fields using safe parameters."""
        table_id = self._get_table_id('members')
        
        try:
            processed_count = 0
            for _, row in updates_df.iterrows():
                # Validate column (security whitelist)
                allowed_columns = ['user_name', 'display_name', 'status', 'role', 'is_booster']
                if row['column'] not in allowed_columns:
                    self.logger.logger.warning(f"⚠️ Skipped update to non-whitelisted column: {row['column']}")
                    continue
                
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("new_value", "STRING", str(row['new_value'])),
                        bigquery.ScalarQueryParameter("updated_at", "TIMESTAMP", row['updated_at']),
                        bigquery.ScalarQueryParameter("user_id", "STRING", str(row['user_id'])),
                    ]
                )
                
                # Column name can't be parameterized, but was validated above
                update_query = f"""
                UPDATE `{table_id}`
                SET {row['column']} = @new_value,
                    updated_at = @updated_at
                WHERE user_id = @user_id
                """
                
                query_job = self.client.query(update_query, job_config=job_config)
                query_job.result()
                processed_count += 1
            
            if processed_count > 0:
                self.logger.data_processed("member update", processed_count, get_table_name('members'))
            
        except Exception as e:
            self.logger.error("update member fields", e)
            raise
    
    @log_execution_time
    async def update_message_counts(self, message_df: pd.DataFrame):
        """Update message counts using merge operation."""
        if message_df.empty:
            self.logger.no_data("message count")
            return
        
        await self._merge_aggregated_data(message_df, 'message_counts', 'message_count')
    
    @log_execution_time
    async def update_message_details(self, message_df: pd.DataFrame):
        """Update message details by appending to table."""
        if message_df.empty:
            self.logger.no_data("message detail")
            return
        
        table_id = self._get_table_id('message_details')
        
        try:
            # Ensure timestamp format
            message_df['created_at'] = pd.to_datetime(message_df['created_at'])
            
            job_config = bigquery.LoadJobConfig(
                schema=SCHEMAS['message_details'],
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            job = self.client.load_table_from_dataframe(
                message_df, table_id, job_config=job_config
            )
            job.result()
            
            self.logger.data_processed("message", len(message_df), get_table_name('message_details'))
            
        except Exception as e:
            self.logger.error("update message details", e)
            raise
    
    @log_execution_time
    async def update_voice_activity(self, voice_df: pd.DataFrame):
        """Update voice activity using merge operation."""
        if voice_df.empty:
            self.logger.no_data("voice activity")
            return
        
        await self._merge_aggregated_data(voice_df, 'voice_activity', 'duration_seconds')
    
    @log_execution_time
    async def update_threads(self, thread_df: pd.DataFrame):
        """Update thread data by appending to table."""
        if thread_df.empty:
            self.logger.no_data("thread")
            return
        
        table_id = self._get_table_id('threads')
        
        try:
            job_config = bigquery.LoadJobConfig(
                schema=SCHEMAS['threads'],
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            job = self.client.load_table_from_dataframe(
                thread_df, table_id, job_config=job_config
            )
            job.result()
            
            self.logger.data_processed("thread", len(thread_df), get_table_name('threads'))
            
        except Exception as e:
            self.logger.error("update threads", e)
            raise
    
    @log_execution_time
    async def update_presence_logs(self, presence_df: pd.DataFrame):
        """Update presence logs by appending unique entries."""
        if presence_df.empty:
            self.logger.no_data("presence")
            return
        
        # Remove duplicates by user_id
        original_count = len(presence_df)
        presence_df = presence_df.drop_duplicates(subset=['user_id'])
        
        if len(presence_df) < original_count:
            self.logger.logger.debug(f"Removed {original_count - len(presence_df)} duplicate presence records")
        
        table_id = self._get_table_id('presence_logs')
        
        try:
            job_config = bigquery.LoadJobConfig(
                schema=SCHEMAS['presence_logs'],
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            job = self.client.load_table_from_dataframe(
                presence_df, table_id, job_config=job_config
            )
            job.result()
            
            self.logger.data_processed("presence log", len(presence_df), get_table_name('presence_logs'))
            
        except Exception as e:
            self.logger.error("update presence logs", e)
            raise
    
    async def _merge_aggregated_data(self, df: pd.DataFrame, table_key: str, aggregate_column: str):
        """Generic method for merging aggregated data."""
        table_id = self._get_table_id(table_key)
        temp_table_id = f"{table_id}_temp"
        
        try:
            # Load to temporary table
            job = self.client.load_table_from_dataframe(df, temp_table_id)
            job.result()
            
            # Merge with main table
            merge_query = f"""
            MERGE `{table_id}` T
            USING `{temp_table_id}` Temp
            ON T.date = Temp.date AND T.user_id = Temp.user_id AND T.channel_id = Temp.channel_id
            WHEN MATCHED THEN
                UPDATE SET T.{aggregate_column} = T.{aggregate_column} + Temp.{aggregate_column}
            WHEN NOT MATCHED THEN
                INSERT (date, user_id, channel_id, {aggregate_column})
                VALUES (Temp.date, Temp.user_id, Temp.channel_id, Temp.{aggregate_column})
            """
            
            self.client.query(merge_query).result()
            
            # Clean up temporary table
            self.client.delete_table(temp_table_id, not_found_ok=True)
            
            self.logger.data_processed(table_key.replace('_', ' '), len(df), get_table_name(table_key))
            
        except Exception as e:
            self.logger.error(f"merge {table_key} data", e)
            # Clean up temporary table on error
            self.client.delete_table(temp_table_id, not_found_ok=True)
            raise
    
    def _prepare_member_data_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare member data without manual escaping."""
        df = df.copy()
        
        # Convert timestamps
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['joined_at'] = pd.to_datetime(df['joined_at'])        
        return df
    
    def _build_safe_member_merge_query(self, table_id: str) -> str:
        """Build safe MERGE query using parameters."""
        return f"""
        MERGE `{table_id}` T
        USING (SELECT
                @user_id AS user_id,
                @user_name AS user_name,
                @display_name AS display_name,
                @is_bot AS is_bot,
                @is_booster AS is_booster,
                @role AS role,
                @joined_at AS joined_at,
                @status AS status,
                @updated_at AS updated_at
            ) S
        ON T.user_id = S.user_id
        WHEN MATCHED THEN
            UPDATE SET
                T.user_name = S.user_name,
                T.display_name = S.display_name,
                T.is_bot = S.is_bot,
                T.is_booster = S.is_booster,
                T.role = S.role,
                T.joined_at = S.joined_at,
                T.status = S.status,
                T.updated_at = S.updated_at
        WHEN NOT MATCHED THEN
            INSERT (user_id, user_name, display_name, is_bot, is_booster, role, joined_at, status, updated_at)
            VALUES (S.user_id, S.user_name, S.display_name, S.is_bot, S.is_booster, S.role, S.joined_at, S.status, S.updated_at);
        """