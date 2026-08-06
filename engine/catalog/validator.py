"""Deterministic schema validator for products and metrics"""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from jsonschema import Draft7Validator, ValidationError

class SchemaValidator:
    """Validate product, metric, and relationship configuration dictionary against JSON schemas"""
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.product_schema = self._load_schema("product.schema.json")
        self.metric_schema = self._load_schema("metric.schema.json")
        self.relationship_schema = self._load_schema("relationship.schema.json")
        
        self.product_validator = Draft7Validator(self.product_schema) if self.product_schema else None
        self.metric_validator = Draft7Validator(self.metric_schema) if self.metric_schema else None
        self.relationship_validator = Draft7Validator(self.relationship_schema) if self.relationship_schema else None

    def _load_schema(self, schema_name: str) -> Optional[Dict]:
        """Loads schema file safely"""
        schema_path = self.schemas_dir / schema_name
        if schema_path.exists():
            try:
                with open(schema_path, "r") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def validate_product(self, product_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate product manifest against product schema
        
        Returns:
            (is_valid, error_message)
        """
        if not self.product_validator:
            return True, None
            
        errors = sorted(self.product_validator.iter_errors(product_data), key=lambda e: e.path)
        if errors:
            msg = "; ".join([f"{'.'.join(map(str, e.path)) or 'root'}: {e.message}" for e in errors])
            return False, msg
        return True, None

    def validate_metric(self, metric_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate metric contract against metric schema
        
        Returns:
            (is_valid, error_message)
        """
        if not self.metric_validator:
            return True, None
            
        errors = sorted(self.metric_validator.iter_errors(metric_data), key=lambda e: e.path)
        if errors:
            msg = "; ".join([f"{'.'.join(map(str, e.path)) or 'root'}: {e.message}" for e in errors])
            return False, msg
        return True, None

    def validate_relationship(self, relationship_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate relationship contract against relationship schema
        
        Returns:
            (is_valid, error_message)
        """
        if not self.relationship_validator:
            return True, None
            
        errors = sorted(self.relationship_validator.iter_errors(relationship_data), key=lambda e: e.path)
        if errors:
            msg = "; ".join([f"{'.'.join(map(str, e.path)) or 'root'}: {e.message}" for e in errors])
            return False, msg
        return True, None

# Global instance
_validator = None

def get_schema_validator(schemas_dir: str = "schemas") -> SchemaValidator:
    """Get global schema validator"""
    global _validator
    if _validator is None:
        _validator = SchemaValidator(schemas_dir)
    return _validator
