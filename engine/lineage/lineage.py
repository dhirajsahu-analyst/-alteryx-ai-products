"""Multi-tier Lineage and Impact Analysis Engine for TelemetryIQ"""

import sqlite3
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

class LineageEngine:
    """Computes upstream lineage and downstream impact for metrics and tables"""
    
    def __init__(self, db_path: str = ".telemetryiq/catalog.db"):
        self.db_path = Path(db_path)

    def is_available(self) -> bool:
        """Checks if compiled catalog database is available"""
        return self.db_path.exists()

    def get_upstream_lineage(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Trace upstream sources and models contributing to a metric.
        
        Returns:
            Structured dictionary of upstream dependencies, or None if not found.
        """
        if not self.is_available():
            return None
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, product, raw_yaml FROM metrics WHERE metric_id = ?", (asset_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
                
            name, product, raw_yaml = row
            metric_data = yaml.safe_load(raw_yaml)
            
            # Find the source table
            source = metric_data.get("source", "")
            base_tables = []
            if isinstance(source, dict):
                base_tables = source.get("base_tables", [])
            elif isinstance(source, str) and source:
                base_tables = [source]
                
            # If the metric is composed from base metrics
            base_metrics = []
            can_build = metric_data.get("can_build_from", {})
            if "base_metrics" in can_build:
                base_metrics = can_build["base_metrics"]
                
            upstream = {
                "asset_id": asset_id,
                "name": name,
                "product": product,
                "type": "metric",
                "direct_sources": base_tables,
                "base_metrics": []
            }
            
            # Trace base metrics recursively
            for base_id in base_metrics:
                base_lineage = self.get_upstream_lineage(base_id)
                if base_lineage:
                    upstream["base_metrics"].append(base_lineage)
                    # Add base metrics' sources to direct sources
                    upstream["direct_sources"].extend(base_lineage.get("direct_sources", []))
            
            # De-duplicate direct sources
            upstream["direct_sources"] = sorted(list(set(upstream["direct_sources"])))
            
            # Lookup product database/schema metadata
            cursor.execute("SELECT raw_yaml FROM products WHERE product_id = ?", (product,))
            p_row = cursor.fetchone()
            if p_row:
                p_data = yaml.safe_load(p_row[0])
                upstream["database"] = p_data.get("freshness", {}).get("expected", "daily") # fallback dummy meta
                
            conn.close()
            return upstream
            
        except Exception:
            return None

    def get_downstream_impact(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze downstream impact if an asset (table or metric) is modified or broken.
        
        Returns:
            Structured dictionary of downstream targets and affected assets.
        """
        if not self.is_available():
            return None
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            impact = {
                "target_asset": asset_id,
                "affected_metrics": [],
                "affected_relationships": []
            }
            
            # 1. Search for metrics using this asset as a source table
            cursor.execute("SELECT metric_id, name, product, raw_yaml FROM metrics")
            all_metrics = cursor.fetchall()
            
            for m_id, name, product, raw_yaml in all_metrics:
                m_data = yaml.safe_load(raw_yaml)
                
                # Check if asset_id is the direct source table
                source = m_data.get("source", "")
                is_affected = False
                if isinstance(source, dict):
                    if asset_id in source.get("base_tables", []):
                        is_affected = True
                elif isinstance(source, str) and source == asset_id:
                    is_affected = True
                    
                # Check if asset_id is listed in base_metrics of a composition rule
                can_build = m_data.get("can_build_from", {})
                if "base_metrics" in can_build:
                    if asset_id in can_build["base_metrics"]:
                        is_affected = True
                        
                if is_affected:
                    impact["affected_metrics"].append({
                        "metric_id": m_id,
                        "name": name,
                        "product": product,
                        "status": m_data.get("status", "active")
                    })
            
            # 2. Search for relationships referencing this table
            cursor.execute("SELECT relationship_id, left_model, right_model FROM relationships")
            all_relationships = cursor.fetchall()
            
            for rel_id, left, right in all_relationships:
                if left == asset_id or right == asset_id:
                    impact["affected_relationships"].append({
                        "relationship_id": rel_id,
                        "left_model": left,
                        "right_model": right
                    })
                    
            conn.close()
            return impact
            
        except Exception:
            return None

# Global instance
_lineage_engine = None

def get_lineage_engine(db_path: str = ".telemetryiq/catalog.db") -> LineageEngine:
    """Get global lineage engine"""
    global _lineage_engine
    if _lineage_engine is None:
        _lineage_engine = LineageEngine(db_path)
    return _lineage_engine
