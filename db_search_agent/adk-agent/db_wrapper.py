"""
Database wrapper that mimics MCPToolboxForDatabases interface.
Provides direct PostgreSQL connection using psycopg2.
"""
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus, unquote_plus
import psycopg2  # type: ignore[import-untyped]
from psycopg2 import OperationalError  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)


class DatabaseCredentialsConfig:
    """Placeholder for credentials config (not needed for direct connections)."""
    def __init__(self, credentials=None):
        self.credentials = credentials


class MCPToolboxForDatabases:
    """
    Database wrapper that provides MCP Toolbox-like interface for direct PostgreSQL access.
    This replaces the non-existent google.adk.tools.google_cloud.mcp_toolbox import.
    """
    
    def __init__(
        self,
        database_type: str,
        connection_string: str,
        credentials_config: Optional[DatabaseCredentialsConfig] = None
    ):
        """
        Initialize database connection.
        
        Args:
            database_type: Type of database (e.g., "postgresql")
            connection_string: PostgreSQL connection string
            credentials_config: Optional credentials config (not used for direct connections)
        """
        if database_type.lower() != "postgresql":
            raise ValueError(f"Unsupported database type: {database_type}. Only PostgreSQL is supported.")
        
        # Handle passwords with special characters (like @)
        # If connection string has @@, it means password contains @
        # We need to URL-encode the password part
        if '@@' in connection_string:
            # Split the connection string to extract password
            # Format: postgresql://user:password@@host:port/db
            # The first @ is part of password, second @ is separator
            parts = connection_string.split('://', 1)
            if len(parts) == 2:
                scheme = parts[0]
                rest = parts[1]
                # Find the last @ which is the separator before host
                last_at_index = rest.rfind('@')
                if last_at_index > 0:
                    user_pass = rest[:last_at_index]
                    host_db = rest[last_at_index + 1:]
                    if ':' in user_pass:
                        user, password = user_pass.split(':', 1)
                        # URL-encode the password (including the @ in it)
                        password_encoded = quote_plus(password)
                        # Reconstruct connection string
                        connection_string = f"{scheme}://{user}:{password_encoded}@{host_db}"
                        logger.info("URL-encoded password with special characters")
        
        self.connection_string = connection_string
        self._connection = None
        logger.info(f"Initialized MCPToolboxForDatabases for {database_type}")
    
    def _get_connection(self):
        """Get or create database connection."""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(self.connection_string)
            except OperationalError as e:
                # Provide more helpful error message
                logger.error(f"Failed to connect to database: {e}")
                logger.error(f"Connection string format: {self.connection_string.split('@')[0]}@***")
                raise
        return self._connection
    
    def execute_sql(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> 'SQLResult':
        """
        Execute SQL query and return results.
        
        Args:
            query: SQL query string (supports :param_name placeholders)
            parameters: Dictionary of parameters for the query
            
        Returns:
            SQLResult object with rows attribute
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Replace :param_name with %(param_name)s for psycopg2
            if parameters:
                # Convert :param to %(param)s format
                formatted_query = query
                for key in parameters.keys():
                    formatted_query = formatted_query.replace(f":{key}", f"%({key})s")
            else:
                formatted_query = query
                parameters = {}
            
            cursor.execute(formatted_query, parameters)
            
            # Fetch results
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
            else:
                columns = []
                rows = []
            
            conn.commit()
            cursor.close()
            
            logger.debug(f"Executed SQL query, returned {len(rows)} rows")
            
            return SQLResult(rows=rows, columns=columns)
            
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}", exc_info=True)
            if self._connection:
                self._connection.rollback()
            raise
    
    def close(self):
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SQLResult:
    """Result object that mimics MCP Toolbox SQL result."""
    
    def __init__(self, rows: List[tuple], columns: Optional[List[str]] = None):
        self.rows = rows
        self.columns = columns or []

