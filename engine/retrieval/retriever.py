"""Lightweight, indexed local metadata retriever using SQLite"""

import sqlite3
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class MetadataRetriever:
    """Retrieves metadata from compiled SQLite catalog with deterministic ranking"""
    
    def __init__(self, db_path: str = ".telemetryiq/catalog.db"):
        self.db_path = Path(db_path)

    def is_available(self) -> bool:
        """Checks if compiled catalog database is available"""
        return self.db_path.exists()

    def load_metric(self, metric_id: str, product: Optional[str] = None) -> Optional[Dict]:
        """Loads a metric YAML dict from SQLite catalog"""
        if not self.is_available():
            return None
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if product:
                cursor.execute("""
                    SELECT raw_yaml FROM metrics 
                    WHERE metric_id = ? AND product = ?
                """, (metric_id, product))
            else:
                cursor.execute("""
                    SELECT raw_yaml FROM metrics 
                    WHERE metric_id = ?
                """, (metric_id,))
                
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return yaml.safe_load(row[0])
        except Exception:
            pass
        return None

    def search_metrics(self, keyword: str = "", product: Optional[str] = None) -> List[Dict]:
        """
        Searches metrics in SQLite using relational keyword matching and relevance ranking.
        
        Relevance Weights:
        - Exact ID Match: 10.0
        - Substring ID Match: 5.0
        - Substring Name Match: 3.0
        - Substring Description/Category Match: 1.0
        """
        if not self.is_available():
            return []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            kw = keyword.lower()
            kw_wild = f"%{kw}%"
            
            query = """
                SELECT raw_yaml,
                       (CASE 
                            WHEN LOWER(metric_id) = ? THEN 10.0
                            WHEN LOWER(metric_id) LIKE ? THEN 5.0
                            ELSE 0.0
                        END +
                        CASE 
                            WHEN LOWER(name) LIKE ? THEN 3.0
                            ELSE 0.0
                        END +
                        CASE 
                            WHEN LOWER(description) LIKE ? THEN 1.0
                            ELSE 0.0
                        END +
                        CASE 
                            WHEN LOWER(category) LIKE ? THEN 1.0
                            ELSE 0.0
                        END) as relevance_score
                FROM metrics
            """
            
            params = [kw, kw_wild, kw_wild, kw_wild, kw_wild]
            conditions = []
            
            if keyword:
                conditions.append("(LOWER(metric_id) LIKE ? OR LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?)")
                params.extend([kw_wild, kw_wild, kw_wild, kw_wild])
                
            if product:
                conditions.append("product = ?")
                params.append(product)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY relevance_score DESC, metric_id ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append(yaml.safe_load(row[0]))
            return results
        except Exception:
            return []

    def list_metrics(self, product: str) -> List[Dict]:
        """Lists all metrics under a given product in SQLite"""
        if not self.is_available():
            return []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT raw_yaml FROM metrics 
                WHERE product = ?
                ORDER BY metric_id ASC
            """, (product,))
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append(yaml.safe_load(row[0]))
            return results
        except Exception:
            return []

    def get_all_products(self) -> List[Dict]:
        """Retrieves all compiled products in SQLite"""
        if not self.is_available():
            return []
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT raw_yaml, product_id FROM products
                ORDER BY product_id ASC
            """)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                product_data = yaml.safe_load(row[0])
                # Count metrics in sqlite for dynamic counts
                cursor.execute("SELECT COUNT(*) FROM metrics WHERE product = ?", (row[1],))
                metric_count = cursor.fetchone()[0]
                
                # To maintain backward compatibility with list/products tables, map fields:
                product_data['product_name'] = row[1]
                product_data['full_name'] = product_data.get('name', '')
                product_data['metric_count'] = metric_count
                results.append(product_data)
                
            conn.close()
            return results
        except Exception:
            return []

# Global instance
_retriever = None

def get_metadata_retriever(db_path: str = ".telemetryiq/catalog.db") -> MetadataRetriever:
    """Get global metadata retriever"""
    global _retriever
    if _retriever is None:
        _retriever = MetadataRetriever(db_path)
    return _retriever
