"""Semantic Graph layer governing cross-product model relationships and joins"""

import sqlite3
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SemanticGraph:
    """Governs models, entities, and relationship linkages, preventing untrusted or invalid joins"""
    
    def __init__(self, db_path: str = ".telemetryiq/catalog.db"):
        self.db_path = Path(db_path)
        self._relationships: List[Dict] = []
        self._load_relationships()

    def is_available(self) -> bool:
        """Checks if compiled catalog database is available"""
        return self.db_path.exists()

    def _load_relationships(self):
        """Loads relationships from compiled catalog"""
        if not self.is_available():
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT raw_yaml FROM relationships")
            rows = cursor.fetchall()
            conn.close()
            
            self._relationships = [yaml.safe_load(row[0]) for row in rows]
        except Exception:
            pass

    def get_relationship(self, model_a: str, model_b: str) -> Optional[Dict]:
        """
        Retrieves relationship contract between model_a and model_b if one exists
        """
        for rel in self._relationships:
            left = rel.get("left_model")
            right = rel.get("right_model")
            
            # Check both directions
            if (left == model_a and right == model_b) or (left == model_b and right == model_a):
                return rel
        return None

    def check_join_compatibility(self, model_a: str, model_b: str) -> Tuple[bool, Optional[str]]:
        """
        Validates whether two models can be joined safely according to semantic policies
        
        Returns:
            (is_compatible, detail_message)
        """
        if model_a == model_b:
            return True, "Models are identical, self-join is allowed."
            
        rel = self.get_relationship(model_a, model_b)
        if not rel:
            return False, f"No semantic relationship contract registered between [{model_a}] and [{model_b}]."
            
        if rel.get("cardinality") == "many_to_many":
            return False, f"Join blocked: Relationship between [{model_a}] and [{model_b}] has unsafe many-to-many cardinality."
            
        return True, f"Approved join via relationship [{rel.get('relationship_id')}] on left keys {rel.get('left_keys')} and right keys {rel.get('right_keys')}."

# Global instance
_graph = None

def get_semantic_graph(db_path: str = ".telemetryiq/catalog.db") -> SemanticGraph:
    """Get global semantic graph"""
    global _graph
    if _graph is None:
        _graph = SemanticGraph(db_path)
    return _graph
