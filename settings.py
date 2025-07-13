#src/dq_engine/config/settings.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_path: str = "data/dq_engine.db"
    
    # Web server
    host: str = "localhost"
    port: int = 8000
    
    # Profiling
    default_sample_size: int = 10000
    max_sample_size: int = 100000
    
    # Application
    app_name: str = "Data Quality Engine"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "DQ_"

settings = Settings()

# Ensure data directory exists
Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)

# src/dq_engine/database/connection.py
import duckdb
from pathlib import Path
from typing import Optional
import logging
from ..config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.database_path
        self.conn = None
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get database connection"""
        if self.conn is None:
            self.conn = duckdb.connect(self.db_path)
            self._initialize_schema()
        return self.conn
    
    def _initialize_schema(self):
        """Initialize database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS data_sources (
            id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            type VARCHAR NOT NULL,
            config JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profile_runs (
            id VARCHAR PRIMARY KEY,
            data_source_id VARCHAR REFERENCES data_sources(id),
            run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR DEFAULT 'running',
            error_message TEXT,
            row_count INTEGER,
            column_count INTEGER
        );

        CREATE TABLE IF NOT EXISTS column_profiles (
            id VARCHAR PRIMARY KEY,
            profile_run_id VARCHAR REFERENCES profile_runs(id),
            column_name VARCHAR NOT NULL,
            data_type VARCHAR,
            null_count INTEGER,
            null_percentage FLOAT,
            distinct_count INTEGER,
            distinct_percentage FLOAT,
            min_value VARCHAR,
            max_value VARCHAR,
            avg_value FLOAT,
            std_dev FLOAT,
            profile_data JSON
        );

        CREATE TABLE IF NOT EXISTS quality_scores (
            id VARCHAR PRIMARY KEY,
            profile_run_id VARCHAR REFERENCES profile_runs(id),
            dimension VARCHAR NOT NULL,
            score FLOAT NOT NULL,
            weight FLOAT DEFAULT 1.0,
            details JSON
        );

        CREATE TABLE IF NOT EXISTS quality_rules (
            id VARCHAR PRIMARY KEY,
            data_source_id VARCHAR REFERENCES data_sources(id),
            column_name VARCHAR,
            rule_type VARCHAR NOT NULL,
            rule_config JSON NOT NULL,
            threshold FLOAT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.conn.execute(schema_sql)
            logger.info("Database schema initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

# Global database manager instance
db_manager = DatabaseManager()
