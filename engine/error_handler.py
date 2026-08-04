"""Error handling and user-friendly error messages"""

from typing import List, Optional, Dict
from enum import Enum

class ErrorCode(Enum):
    METRIC_NOT_FOUND = "METRIC_NOT_FOUND"
    COMPOSITION_FAILED = "COMPOSITION_FAILED"
    SNOWFLAKE_ERROR = "SNOWFLAKE_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    INVALID_FILTER = "INVALID_FILTER"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"

class MetricError(Exception):
    """Base exception for metric operations"""
    
    def __init__(self, error_code: ErrorCode, message: str, details: Optional[Dict] = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        return f"[{self.error_code.value}] {self.message}"

class MetricNotFoundError(MetricError):
    """Metric definition not found"""
    
    def __init__(self, metric_id: str, suggestions: Optional[List[str]] = None):
        self.metric_id = metric_id
        self.suggestions = suggestions or []
        
        message = f"Metric '{metric_id}' not found in repository"
        details = {"metric_id": metric_id, "suggestions": suggestions}
        
        super().__init__(ErrorCode.METRIC_NOT_FOUND, message, details)

class CompositionError(MetricError):
    """Could not compose metric from foundations"""
    
    def __init__(self, metric_id: str, attempted_compositions: List[str], reason: str):
        self.metric_id = metric_id
        self.attempted_compositions = attempted_compositions
        self.reason = reason
        
        message = f"Could not build '{metric_id}' from available foundations: {reason}"
        details = {
            "metric_id": metric_id,
            "attempted": attempted_compositions,
            "reason": reason
        }
        
        super().__init__(ErrorCode.COMPOSITION_FAILED, message, details)

class SnowflakeError(MetricError):
    """Snowflake connection or query error"""
    
    def __init__(self, error_type: str, message: str, snowflake_error: Optional[Exception] = None):
        self.snowflake_error = snowflake_error
        
        details = {
            "error_type": error_type,
            "original_error": str(snowflake_error) if snowflake_error else None
        }
        
        super().__init__(ErrorCode.SNOWFLAKE_ERROR, message, details)

class AuthError(MetricError):
    """Authentication/Authorization error"""
    
    def __init__(self, reason: str):
        message = f"Authentication failed: {reason}"
        details = {"reason": reason}
        super().__init__(ErrorCode.AUTH_ERROR, message, details)

# Error message formatter
class ErrorFormatter:
    """Format errors into user-friendly messages"""
    
    @staticmethod
    def format_not_found_error(error: MetricNotFoundError, alternatives: Optional[List[Dict]] = None) -> str:
        """Format metric not found error with suggestions"""
        
        message = f"""
╭─ ERROR: Metric not found ──────────────────────────────────────────┐
│                                                                    │
│ Metric '{error.metric_id}' not found in repository               │
│                                                                    │
"""
        
        if alternatives:
            message += "│ Available alternatives:                                        │\n"
            for alt in alternatives[:3]:
                status = "✓ Available" if alt.get('available') else "◆ Composable"
                message += f"│   • {alt['id']:40} {status:15} │\n"
            message += "│                                                                    │\n"
        
        message += """│ What to do:                                                    │
│   → Search similar: metrics search --keyword "your_keyword"      │
│   → List all: metrics list --product {product}                   │
│   → Contact: insights@alteryx.com                                │
│                                                                    │
╰────────────────────────────────────────────────────────────────────╯
"""
        return message
    
    @staticmethod
    def format_composition_error(error: CompositionError) -> str:
        """Format composition error with diagnostics"""
        
        message = f"""
╭─ ERROR: Could not build metric ───────────────────────────────────┐
│                                                                    │
│ Metric: {error.metric_id}                                          │
│ Reason: {error.reason}                                             │
│                                                                    │
│ Attempted compositions:                                            │
"""
        
        for attempt in error.attempted_compositions:
            message += f"│   ✗ {attempt}\n"
        
        message += """│                                                                    │
│ What to do:                                                    │
│   1. Check if base tables exist: metrics validate --product X  │
│   2. Try alternative metric: metrics search --product X         │
│   3. Request new metric: insights@alteryx.com                  │
│                                                                    │
╰────────────────────────────────────────────────────────────────────╯
"""
        return message
    
    @staticmethod
    def format_snowflake_error(error: SnowflakeError) -> str:
        """Format Snowflake error with solutions"""
        
        solutions = {
            "AUTH_FAILED": "Re-authenticate: metrics auth --relogin",
            "WAREHOUSE_NOT_FOUND": "Check Snowflake warehouse: https://alteryx.snowflakecomputing.com",
            "PERMISSION_DENIED": "Contact Snowflake admin: snowflake-admin@alteryx.com",
            "TABLE_NOT_FOUND": "Metric definition references unavailable table. Contact insights@alteryx.com",
        }
        
        solution = solutions.get(error.details.get("error_type"), "Check Snowflake connection")
        
        message = f"""
╭─ ERROR: Snowflake connection failed ───────────────────────────────┐
│                                                                    │
│ Error: {error.message}                                             │
│                                                                    │
│ Solution:                                                          │
│   → {solution}                                                     │
│                                                                    │
╰────────────────────────────────────────────────────────────────────╯
"""
        return message
