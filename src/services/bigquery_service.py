import logging
import pandas as pd
from google.cloud import bigquery
from config.bigquery_config import get_bigquery_client, SCHEMAS
from config.settings import PROJECT_ID, DATASET_ID
from utils.helpers import log_execution_time

logger = logging.getLogger(__name__)

class BigQueryService:
    """Service for handling BigQuery operations."""
    
    def __init__(self):
        self.client = get_bigquery_client()
        self.project_id = PROJECT_ID
        self.dataset_id = DATASET_ID
    
    def _get_table_id(self, table_name: str) -> str:
        """Get full table ID."""
        return f"{self.project_id}.{self.dataset_id}.{table_name}"
    
    @log_execution_time
    async def update_members(self, members_df: pd.DataFrame, updates_df: pd.DataFrame):
        """Update member data in BigQuery."""
        if not members_df.empty:
            await self._upsert_members(members_df)
        
        if not updates_df.empty:
            await self._update_member_fields(updates_df)
    
    async def _upsert_members(self, members_df: pd.DataFrame):
        """Upsert member data using MERGE statement."""
        table_id = self._get_table_id('dim_member')
        
        try:
            # Prepare data
            members_df = self._prepare_member_data(members_df)
            
            # Process each member with MERGE query
            for _, row in members_df.iterrows():
                merge_query = self._build_member_merge_query(table_id, row)
                self.client.query(merge_query).result()
            
            logger.info(f"Successfully updated {len(members_df)} members")
            
        except Exception as e:
            logger.error(f"Error updating members: {e}")
            raise
    
    async def _update_member_fields(self, updates_df: pd.DataFrame):
        """Update specific member fields."""
        table_id = self._get_table_id('dim_member')
        
        try:
            for _, row in updates_df.iterrows():
                update_query = f"""
                UPDATE `{table_id}`
                SET {row['column']} = '{row['new_value']}',
                    updated_at = TIMESTAMP('{row['updated_at']}')
                WHERE user_id = '{row['user_id']}'
                """
                self.client.query(update_query).result()
            
            logger.info(f"Successfully updated {len(updates_df)} member fields")
            
        except Exception as e:
            logger.error(f"Error updating member fields: {e}")
            raise
    
    @log_execution_time
    async def update_message_counts(self, message_df: pd.DataFrame):
        """Update message counts using merge operation."""
        if message_df.empty:
            logger.info("No message count data to update")
            return
        
        await self._merge_aggregated_data(message_df, 'message_count', 'message_count')
    
    @log_execution_time
    async def update_message_details(self, message_df: pd.DataFrame):
        """Update message details by appending to table."""
        if message_df.empty:
            logger.info("No message detail data to update")
            return
        
        table_id = self._get_table_id('messages')
        
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
            
            logger.info(f"Successfully added {len(message_df)} message details")
            
        except Exception as e:
            logger.error(f"Error updating message details: {e}")
            raise
    
    @log_execution_time
    async def update_voice_activity(self, voice_df: pd.DataFrame):
        """Update voice activity using merge operation."""
        if voice_df.empty:
            logger.info("No voice activity data to update")
            return
        
        await self._merge_aggregated_data(voice_df, 'voice_channel', 'duration_seconds')
    
    @log_execution_time
    async def update_threads(self, thread_df: pd.DataFrame):
        """Update thread data by appending to table."""
        if thread_df.empty:
            logger.info("No thread data to update")
            return
        
        table_id = self._get_table_id('thread')
        
        try:
            job_config = bigquery.LoadJobConfig(
                schema=SCHEMAS['threads'],
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            job = self.client.load_table_from_dataframe(
                thread_df, table_id, job_config=job_config
            )
            job.result()
            
            logger.info(f"Successfully added {len(thread_df)} threads")
            
        except Exception as e:
            logger.error(f"Error updating threads: {e}")
            raise
    
    @log_execution_time
    async def update_presence_logs(self, presence_df: pd.DataFrame):
        """Update presence logs by appending unique entries."""
        if presence_df.empty:
            logger.info("No presence data to update")
            return
        
        # Remove duplicates by user_id
        presence_df = presence_df.drop_duplicates(subset=['user_id'])
        
        table_id = self._get_table_id('daily_user_logins')
        
        try:
            job_config = bigquery.LoadJobConfig(
                schema=SCHEMAS['presence_logs'],
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            job = self.client.load_table_from_dataframe(
                presence_df, table_id, job_config=job_config
            )
            job.result()
            
            logger.info(f"Successfully added {len(presence_df)} presence logs")
            
        except Exception as e:
            logger.error(f"Error updating presence logs: {e}")
            raise
    
    async def _merge_aggregated_data(self, df: pd.DataFrame, table_name: str, aggregate_column: str):
        """Generic method for merging aggregated data."""
        table_id = self._get_table_id(table_name)
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
            
            logger.info(f"Successfully merged {len(df)} records to {table_name}")
            
        except Exception as e:
            logger.error(f"Error merging data to {table_name}: {e}")
            # Clean up temporary table on error
            self.client.delete_table(temp_table_id, not_found_ok=True)
            raise
    
    def _prepare_member_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare member data for BigQuery insertion."""
        df = df.copy()
        
        # Convert timestamps
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['joined_at'] = pd.to_datetime(df['joined_at'])
        
        # Escape quotes in string fields
        string_columns = ['user_name', 'display_name', 'role']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].str.replace("'", "\\'")
        
        return df
    
    def _build_member_merge_query(self, table_id: str, row: pd.Series) -> str:
        """Build MERGE query for member data."""
        return f"""
        MERGE `{table_id}` T
        USING (SELECT
                '{row['user_id']}' AS user_id,
                '{row['user_name']}' AS user_name,
                '{row['display_name']}' AS display_name,
                CAST({row['is_bot']} AS BOOLEAN) AS is_bot,
                CAST({row['is_booster']} AS BOOLEAN) AS is_booster,
                '{row['role']}' AS role,
                TIMESTAMP('{row['joined_at']}') AS joined_at,
                '{row['status']}' AS status,
                TIMESTAMP('{row['updated_at']}') AS updated_at
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