"""Load and parse metric definitions from YAML files"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import os
from engine.catalog.validator import get_schema_validator
from engine.retrieval.retriever import get_metadata_retriever

class MetricLoader:
    """Load metric definitions from YAML files"""
    
    def __init__(self, products_dir: str = "products"):
        self.products_dir = Path(products_dir)
        self._cache = {}
        self.validator = get_schema_validator()
        self.retriever = get_metadata_retriever()
    
    def load_metric(self, metric_id: str, product: Optional[str] = None) -> Optional[Dict]:
        """
        Load a metric definition from YAML
        
        Args:
            metric_id: Metric identifier
            product: Optional product name (speeds up search)
        
        Returns:
            Metric definition dict or None if not found
        """
        
        # Check SQLite compiled catalog first
        if self.retriever.is_available():
            return self.retriever.load_metric(metric_id, product)
            
        # Check cache first
        cache_key = f"{product}:{metric_id}" if product else metric_id
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # If product specified, search directly
        if product:
            metric_file = self.products_dir / product / "metrics" / f"{metric_id}.yaml"
            if metric_file.exists():
                metric_def = self._load_yaml(metric_file)
                self._cache[cache_key] = metric_def
                return metric_def
        else:
            # Search all products
            for product_dir in self.products_dir.iterdir():
                if not product_dir.is_dir():
                    continue
                
                metric_file = product_dir / "metrics" / f"{metric_id}.yaml"
                if metric_file.exists():
                    metric_def = self._load_yaml(metric_file)
                    self._cache[cache_key] = metric_def
                    return metric_def
        
        return None
    
    def search_metrics(self, keyword: str = "", product: Optional[str] = None) -> List[Dict]:
        """Search metrics by keyword and/or product"""
        
        # Check SQLite compiled catalog first
        if self.retriever.is_available():
            return self.retriever.search_metrics(keyword, product)
            
        results = []
        products_to_search = []
        
        if product:
            product_dir = self.products_dir / product
            if product_dir.exists():
                products_to_search = [product_dir]
        else:
            products_to_search = [d for d in self.products_dir.iterdir() if d.is_dir()]
        
        for product_dir in products_to_search:
            metrics_dir = product_dir / "metrics"
            if not metrics_dir.exists():
                continue
            
            for metric_file in metrics_dir.glob("*.yaml"):
                metric_def = self._load_yaml(metric_file)
                
                # Filter by keyword
                if keyword:
                    name = metric_def.get('name', '').lower()
                    description = metric_def.get('description', '').lower()
                    if keyword.lower() not in name and keyword.lower() not in description:
                        continue
                
                results.append(metric_def)
        
        return results
    
    def list_metrics(self, product: str) -> List[Dict]:
        """List all metrics in a product"""
        
        # Check SQLite compiled catalog first
        if self.retriever.is_available():
            return self.retriever.list_metrics(product)
            
        product_dir = self.products_dir / product
        metrics_dir = product_dir / "metrics"
        
        if not metrics_dir.exists():
            return []
        
        metrics = []
        for metric_file in sorted(metrics_dir.glob("*.yaml")):
            metric_def = self._load_yaml(metric_file)
            metrics.append(metric_def)
        
        return metrics
    
    def get_all_products(self) -> List[Dict]:
        """Get metadata for all products"""
        
        # Check SQLite compiled catalog first
        if self.retriever.is_available():
            return self.retriever.get_all_products()
            
        products = []
        for product_dir in self.products_dir.iterdir():
            if not product_dir.is_dir():
                continue
            
            context_file = product_dir / "product_context.yaml"
            if context_file.exists():
                context = self._load_yaml(context_file)
                metric_count = len(list((product_dir / "metrics").glob("*.yaml")))
                context['metric_count'] = metric_count
                products.append(context)
        
        return products
    
    def load_composition_rules(self) -> Dict:
        """Load metric composition rules from YAML definitions"""
        
        rules = {}
        
        for product_dir in self.products_dir.iterdir():
            if not product_dir.is_dir():
                continue
            
            metrics_dir = product_dir / "metrics"
            if not metrics_dir.exists():
                continue
            
            for metric_file in metrics_dir.glob("*.yaml"):
                metric_def = self._load_yaml(metric_file)
                metric_id = metric_def.get('id')
                
                # Extract composition rules if present
                if 'can_build_from' in metric_def:
                    rules[metric_id] = metric_def['can_build_from']
        
        return rules
    
    def _load_yaml(self, file_path: Path) -> Dict:
        """Load and parse YAML file"""
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            
        if data and isinstance(data, dict):
            # Validate as metric if it contains sql_template
            if 'sql_template' in data:
                is_valid, err_msg = self.validator.validate_metric(data)
                if not is_valid:
                    import sys
                    print(f"SCHEMA WARNING [{file_path.name}]: {err_msg}", file=sys.stderr)
            # Validate as product if it contains product_id
            elif 'product_id' in data:
                is_valid, err_msg = self.validator.validate_product(data)
                if not is_valid:
                    import sys
                    print(f"SCHEMA WARNING [{file_path.name}]: {err_msg}", file=sys.stderr)
        
        return data if data else {}

# Global instance
_loader = None

def get_metric_loader(products_dir: str = "products") -> MetricLoader:
    """Get or create global metric loader"""
    global _loader
    if _loader is None:
        _loader = MetricLoader(products_dir)
    return _loader
