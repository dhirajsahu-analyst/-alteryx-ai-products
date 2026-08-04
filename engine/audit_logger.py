"""Audit logging for all metric operations"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import os

class AuditLogger:
    """Log all metric operations for compliance and debugging"""
    
    def __init__(self, log_dir: str = ".metrics_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup JSON logger
        self.json_log_file = self.log_dir / "audit_log.jsonl"
        
        # Setup Python logger for console
        self.logger = logging.getLogger("metrics_audit")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_dir / "metrics.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log(self, user_id: str, action: str, **kwargs) -> None:
        """Log an operation to audit trail"""
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "action": action,
            **kwargs
        }
        
        # Write to JSONL file
        with open(self.json_log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Also log to console/file via logger
        self.logger.info(f"[{action}] User: {user_id}, Details: {kwargs}")
    
    def get_logs(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """Retrieve audit logs with optional filtering"""
        
        if not self.json_log_file.exists():
            return []
        
        logs = []
        with open(self.json_log_file, "r") as f:
            for line in f:
                log_entry = json.loads(line)
                
                # Apply filters
                if filters:
                    match = True
                    for key, value in filters.items():
                        if log_entry.get(key) != value:
                            match = False
                            break
                    if match:
                        logs.append(log_entry)
                else:
                    logs.append(log_entry)
        
        return logs

# Global instance
_audit_logger = None

def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
