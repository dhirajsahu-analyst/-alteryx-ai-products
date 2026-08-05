"""Snowflake connection and query execution"""

import os
from typing import Optional, Dict, Any, List
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.errors import DatabaseError, ProgrammingError
from engine.error_handler import SnowflakeError, AuthError

class SnowflakeConnector:
    """Manage Snowflake connections and execute queries"""
    
    def __init__(self, use_sso: bool = True):
        self.use_sso = use_sso
        self._connection = None
        self._authenticated = False
    
    def connect(self, account: Optional[str] = None, warehouse: Optional[str] = None,
                database: Optional[str] = None, schema: Optional[str] = None) -> None:
        """
        Connect to Snowflake with SSO
        
        Args:
            account: Snowflake account identifier (from env: SNOWFLAKE_ACCOUNT)
            warehouse: Warehouse name (from env: SNOWFLAKE_WAREHOUSE)
            database: Database name (from env: SNOWFLAKE_DATABASE)
            schema: Schema name (from env: SNOWFLAKE_SCHEMA)
        """
        
        try:
            # Get credentials from environment or arguments
            account = account or os.getenv("SNOWFLAKE_ACCOUNT", "ALTERYX-ALTERYX_EDW")
            warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
            database = database or os.getenv("SNOWFLAKE_DATABASE", "DISCOVERY_PRODUCT_MANAGEMENT")
            schema = schema or os.getenv("SNOWFLAKE_SCHEMA", "METRIC_STORE")
            
            if self.use_sso:
                # SSO Authentication
                self._connection = connect(
                    account=account,
                    user=os.getenv("SNOWFLAKE_USER"),
                    authenticator="externalbrowser",
                    warehouse=warehouse,
                    database=database,
                    schema=schema,
                )
            else:
                # Username/password (not recommended)
                self._connection = connect(
                    account=account,
                    user=os.getenv("SNOWFLAKE_USER"),
                    password=os.getenv("SNOWFLAKE_PASSWORD"),
                    warehouse=warehouse,
                    database=database,
                    schema=schema,
                )
            
            self._authenticated = True
            
        except DatabaseError as e:
            if "Free trial" in str(e) or "suspended" in str(e):
                raise SnowflakeError(
                    "WAREHOUSE_SUSPENDED",
                    "Snowflake warehouse is suspended. Add billing or check account status.",
                    e
                )
            else:
                raise SnowflakeError("DATABASE_ERROR", str(e), e)
        except Exception as e:
            if "auth" in str(e).lower():
                raise AuthError(f"SSO authentication failed. Please re-authenticate.")
            else:
                raise SnowflakeError("CONNECTION_ERROR", str(e), e)
    
    def execute_query(self, query: str, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a query in Snowflake
        
        Args:
            query: SQL query to execute
            filters: Optional filter values to substitute in query
        
        Returns:
            Results as pandas DataFrame
        """
        
        if not self._authenticated:
            raise AuthError("Not connected to Snowflake. Call connect() first.")
        
        try:
            # Substitute filter parameters if provided
            if filters:
                query = self._substitute_filters(query, filters)
            
            cursor = self._connection.cursor()
            cursor.execute(query)
            
            # Fetch results as DataFrame
            results = cursor.fetch_pandas_all()
            cursor.close()
            
            return results
            
        except ProgrammingError as e:
            if "does not exist" in str(e):
                raise SnowflakeError(
                    "TABLE_NOT_FOUND",
                    f"Referenced table not found in Snowflake: {str(e)}",
                    e
                )
            else:
                raise SnowflakeError("QUERY_ERROR", str(e), e)
        except DatabaseError as e:
            raise SnowflakeError("DATABASE_ERROR", str(e), e)
    
    def check_table_exists(self, table_name: str, schema: Optional[str] = None) -> bool:
        """Check if a table exists in Snowflake"""
        
        try:
            query = f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{table_name.upper()}'
            """
            
            if schema:
                query += f" AND TABLE_SCHEMA = '{schema.upper()}'"
            
            result = self.execute_query(query)
            return result.iloc[0, 0] > 0
            
        except Exception:
            return False
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if a column exists in a table"""
        
        try:
            query = f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name.upper()}' 
            AND COLUMN_NAME = '{column_name.upper()}'
            """
            
            result = self.execute_query(query)
            return result.iloc[0, 0] > 0
            
        except Exception:
            return False
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get list of columns in a table"""
        
        try:
            query = f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name.upper()}'
            ORDER BY ORDINAL_POSITION
            """
            
            result = self.execute_query(query)
            return result['COLUMN_NAME'].tolist()
            
        except Exception:
            return []
    
    def _substitute_filters(self, query: str, filters: Dict[str, Any]) -> str:
        """Substitute filter parameters into query template"""
        
        for key, value in filters.items():
            # Handle different value types
            if isinstance(value, str):
                placeholder = f"{{{{{key}}}}}"
                query = query.replace(placeholder, f"'{value}'")
            elif isinstance(value, (int, float)):
                placeholder = f"{{{{{key}}}}}"
                query = query.replace(placeholder, str(value))
            elif isinstance(value, bool):
                placeholder = f"{{{{{key}}}}}"
                query = query.replace(placeholder, str(value).upper())
        
        return query
    
    def close(self) -> None:
        """Close Snowflake connection"""
        
        if self._connection:
            self._connection.close()
            self._authenticated = False

# Global instance
_connector = None

def get_snowflake_connector(use_sso: bool = True) -> SnowflakeConnector:
    """Get or create global Snowflake connector"""
    global _connector
    if _connector is None:
        _connector = SnowflakeConnector(use_sso)
    return _connector
