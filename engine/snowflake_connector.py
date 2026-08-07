"""Snowflake connection and query execution"""

import os
import re
import time
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
from snowflake.connector import connect
from snowflake.connector.errors import DatabaseError, ProgrammingError
from engine.error_handler import SnowflakeError, AuthError
from engine.audit_logger import AuditLogger

class SnowflakeConnector:
    """Manage Snowflake connections and execute queries"""
    
    def __init__(self, use_sso: bool = True):
        self.use_sso = use_sso
        self._connection = None
        self._authenticated = False
        self.audit_logger = AuditLogger()
        
    def validate_sql_safety(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that the query contains only read-only SELECT or WITH statements.
        Blocks write operations (INSERT, UPDATE, DELETE, etc.) and DDL.
        """
        # Remove SQL comments to prevent bypasses inside comments
        cleaned = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        cleaned = re.sub(r'--.*$', '', cleaned, flags=re.MULTILINE)
        
        # Remove quoted string literals to prevent false positives inside string literals
        cleaned = re.sub(r"'[^']*'", '', cleaned)
        cleaned = re.sub(r'"[^"]*"', '', cleaned)
        
        # Look for mutational/write/DDL keywords
        restricted_keywords = {
            "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "MERGE", 
            "TRUNCATE", "GRANT", "REVOKE", "COPY", "RENAME", "REPLACE"
        }
        
        # Extract all uppercase words as tokens
        tokens = set(re.findall(r'\b[A-Z_]+\b', cleaned.upper()))
        found = restricted_keywords.intersection(tokens)
        
        if found:
            return False, f"Disallowed mutational/DDL keyword(s) detected: {list(found)}"
            
        return True, None
    
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
            role = os.getenv("SNOWFLAKE_ROLE")
            
            if self.use_sso:
                # SSO Authentication
                conn_params = {
                    "account": account,
                    "user": os.getenv("SNOWFLAKE_USER"),
                    "authenticator": "externalbrowser",
                    "warehouse": warehouse,
                    "database": database,
                    "schema": schema,
                }
                if role:
                    conn_params["role"] = role
                self._connection = connect(**conn_params)
            else:
                # Username/password (not recommended)
                conn_params = {
                    "account": account,
                    "user": os.getenv("SNOWFLAKE_USER"),
                    "password": os.getenv("SNOWFLAKE_PASSWORD"),
                    "warehouse": warehouse,
                    "database": database,
                    "schema": schema,
                }
                if role:
                    conn_params["role"] = role
                self._connection = connect(**conn_params)
            
            self._authenticated = True
            
            # Enforce 30-second query execution timeout on the session
            try:
                cursor = self._connection.cursor()
                cursor.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 30")
                cursor.close()
            except Exception:
                pass
            
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
        Execute SQL query on Snowflake and return results as pandas DataFrame
        
        Args:
            query: SQL query template or raw string
            filters: Filter dictionary to replace placeholders
            
        Returns:
            Results as pandas DataFrame
        """
        
        if not self._authenticated:
            raise AuthError("Not connected to Snowflake. Call connect() first.")
        
        try:
            # 1. SQL Safety Check (Read-only enforcement)
            is_safe, err_msg = self.validate_sql_safety(query)
            if not is_safe:
                raise SnowflakeError("SECURITY_VIOLATION", f"SQL validation failed: {err_msg}")
            
            # Substitute filter parameters if provided
            if filters:
                query = self._substitute_filters(query, filters)
                
            # 2. EXPLAIN Compilation Validation (for SELECT / WITH statements)
            stmt_norm = re.sub(r'\s+', ' ', query.strip().upper())
            if stmt_norm.startswith("SELECT") or stmt_norm.startswith("WITH"):
                try:
                    cursor_explain = self._connection.cursor()
                    cursor_explain.execute(f"EXPLAIN {query}")
                    cursor_explain.close()
                except ProgrammingError as e:
                    if "insufficient privilege" in str(e).lower() or "not authorized" in str(e).lower():
                        pass  # Fall back to direct execution if EXPLAIN is restricted on this object
                    else:
                        raise SnowflakeError(
                            "COMPILATION_ERROR",
                            f"SQL failed compilation in Snowflake: {str(e)}",
                            e
                        )
            
            # 3. Safe Execution and Timing Trace
            start_time = time.time()
            cursor = self._connection.cursor()
            cursor.execute(query)
            
            # Fetch results as DataFrame
            results = cursor.fetch_pandas_all()
            cursor.close()
            
            duration_ms = int((time.time() - start_time) * 1000)
            rows_count = len(results)
            
            # 4. Enforce Row Limits (truncating to maximum 10000 rows)
            if rows_count > 10000:
                results = results.head(10000)
                
            # 5. Structured Audit Logging on Success
            user_id = os.getenv("USER", "anonymous")
            self.audit_logger.log(
                user_id=user_id,
                action="snowflake_query",
                query=query[:200] + ("..." if len(query) > 200 else ""),
                duration_ms=duration_ms,
                rows_returned=rows_count,
                status="SUCCESS"
            )
            
            return results
            
        except SnowflakeError:
            raise
        except ProgrammingError as e:
            user_id = os.getenv("USER", "anonymous")
            self.audit_logger.log(
                user_id=user_id,
                action="snowflake_query",
                query=query[:200] + ("..." if len(query) > 200 else ""),
                status="FAILED",
                error=str(e)
            )
            if "does not exist" in str(e):
                raise SnowflakeError(
                    "TABLE_NOT_FOUND",
                    f"Referenced table not found in Snowflake: {str(e)}",
                    e
                )
            else:
                raise SnowflakeError("QUERY_ERROR", str(e), e)
        except Exception as e:
            user_id = os.getenv("USER", "anonymous")
            self.audit_logger.log(
                user_id=user_id,
                action="snowflake_query",
                query=query[:200] + ("..." if len(query) > 200 else ""),
                status="ERROR",
                error=str(e)
            )
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
