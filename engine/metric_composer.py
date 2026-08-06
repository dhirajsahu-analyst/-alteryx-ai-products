"""Build metrics from foundational queries and composition rules"""

from typing import Optional, Dict, List, Tuple
from engine.metric_loader import get_metric_loader
from engine.snowflake_connector import get_snowflake_connector
from engine.error_handler import CompositionError
from engine.semantic_graph.graph import get_semantic_graph
import pandas as pd

class MetricComposer:
    """Intelligently compose metrics from base metrics and rules"""
    
    def __init__(self):
        self.loader = get_metric_loader()
        self.connector = get_snowflake_connector()
        self.composition_rules = self.loader.load_composition_rules()
        self.graph = get_semantic_graph()
    
    def can_compose_metric(self, metric_id: str, metric_def: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if a metric can be composed from available foundations
        
        Returns:
            (can_compose, composition_rule_or_error)
        """
        
        # Check if metric has composition rules defined
        if 'can_build_from' not in metric_def:
            return False, "No composition rules defined"
        
        composition_rule = metric_def['can_build_from']
        
        # Check if all base metrics are available
        if 'base_metrics' in composition_rule:
            for base_id in composition_rule['base_metrics']:
                base_metric = self.loader.load_metric(base_id)
                if not base_metric:
                    return False, f"Base metric '{base_id}' not found"
        
        # Check if all base tables are available
        if 'base_tables' in composition_rule:
            for table in composition_rule['base_tables']:
                if not self.connector.check_table_exists(table):
                    return False, f"Base table '{table}' not found in Snowflake"
        
        return True, None
    
    def compose_metric(self, metric_id: str, metric_def: Dict,
                      filters: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """
        Attempt to compose a metric from foundational components
        
        Returns:
            DataFrame with composed metric data, or None if composition fails
        """
        
        if 'can_build_from' not in metric_def:
            return None
        
        composition_rule = metric_def['can_build_from']
        attempted = []
        
        # Try to compose from base metrics
        if 'base_metrics' in composition_rule:
            try:
                result = self._compose_from_base_metrics(
                    composition_rule['base_metrics'],
                    composition_rule.get('join_rule', {}),
                    filters
                )
                if result is not None:
                    return result
                attempted.append("Composition from base metrics")
            except Exception as e:
                attempted.append(f"Composition from base metrics: {str(e)}")
        
        # Try to compose from SQL template
        if 'sql_template' in composition_rule:
            try:
                query = composition_rule['sql_template']
                result = self.connector.execute_query(query, filters)
                return result
            except Exception as e:
                attempted.append(f"Composition from SQL template: {str(e)}")
        
        # Try to compose from procedure/view
        if 'procedure' in composition_rule:
            try:
                result = self._call_procedure(
                    composition_rule['procedure'],
                    composition_rule.get('procedure_params', {}),
                    filters
                )
                if result is not None:
                    return result
                attempted.append("Composition via procedure")
            except Exception as e:
                attempted.append(f"Composition via procedure: {str(e)}")
        
        # All composition attempts failed
        return None
    
    def suggest_alternatives(self, metric_id: str, product: Optional[str] = None) -> List[Dict]:
        """Suggest alternative metrics"""
        
        target_metric = self.loader.load_metric(metric_id, product)
        if not target_metric:
            return []
        
        # Find metrics with similar keywords
        target_keywords = set(target_metric.get('tags', []))
        target_keywords.update(target_metric.get('name', '').lower().split())
        
        alternatives = []
        for metric in self.loader.search_metrics(product=product):
            if metric.get('id') == metric_id:
                continue
            
            metric_keywords = set(metric.get('tags', []))
            metric_keywords.update(metric.get('name', '').lower().split())
            
            # Calculate similarity
            similarity = len(target_keywords & metric_keywords) / max(len(target_keywords), len(metric_keywords))
            
            if similarity > 0.3:
                alternatives.append({
                    'id': metric.get('id'),
                    'name': metric.get('name'),
                    'similarity': similarity,
                    'available': True
                })
        
        # Sort by similarity
        alternatives = sorted(alternatives, key=lambda x: x['similarity'], reverse=True)
        
        return alternatives[:3]
    
    def _compose_from_base_metrics(self, base_metric_ids: List[str],
                                   join_rule: Dict, filters: Optional[Dict]) -> Optional[pd.DataFrame]:
        """Compose metric by joining base metrics after verifying semantic join compatibility"""
        
        if not base_metric_ids:
            return None
            
        def get_metric_source_model(m_def: Dict, m_id: str) -> str:
            source = m_def.get('source', '')
            if isinstance(source, dict):
                base_tables = source.get('base_tables', [])
                if base_tables:
                    return base_tables[0]
            elif isinstance(source, str) and source:
                return source
            return m_def.get('source_model', m_id)
        
        # Load first base metric definition to trace its model
        first_id = base_metric_ids[0]
        first_def = self.loader.load_metric(first_id)
        if not first_def:
            raise ValueError(f"Base metric '{first_id}' not found")
        model_a = get_metric_source_model(first_def, first_id)
        
        # Load all base metrics
        dataframes = {}
        for base_id in base_metric_ids:
            metric_def = self.loader.load_metric(base_id)
            if not metric_def:
                raise ValueError(f"Base metric '{base_id}' not found")
            
            # Execute base metric query
            query = metric_def.get('sql_template')
            if not query:
                raise ValueError(f"Base metric '{base_id}' has no SQL template")
            
            df = self.connector.execute_query(query, filters)
            dataframes[base_id] = df
        
        if not dataframes:
            return None
        
        # Start with first dataframe
        result = list(dataframes.values())[0]
        
        # Join remaining dataframes
        if 'join_on' in join_rule:
            for base_id in base_metric_ids[1:]:
                # Check semantic join compatibility
                other_def = self.loader.load_metric(base_id)
                model_b = get_metric_source_model(other_def, base_id)
                
                is_compatible, err_msg = self.graph.check_join_compatibility(model_a, model_b)
                if not is_compatible:
                    raise CompositionError(
                        base_id,
                        [f"Semantic Graph join check between {model_a} and {model_b}"],
                        f"Join blocked by semantic governance: {err_msg}"
                    )
                
                join_columns = join_rule['join_on']
                join_type = join_rule.get('join_type', 'inner')
                
                other_df = dataframes[base_id]
                
                if join_type == 'left':
                    result = result.merge(other_df, on=join_columns, how='left')
                elif join_type == 'inner':
                    result = result.merge(other_df, on=join_columns, how='inner')
                elif join_type == 'outer':
                    result = result.merge(other_df, on=join_columns, how='outer')
        
        return result
    
    def _call_procedure(self, procedure_name: str, params: Dict,
                       filters: Optional[Dict]) -> Optional[pd.DataFrame]:
        """Call a stored procedure to compose metric"""
        
        # Build procedure call
        param_list = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in params.values()])
        query = f"CALL {procedure_name}({param_list})"
        
        try:
            result = self.connector.execute_query(query, filters)
            return result
        except Exception:
            return None
