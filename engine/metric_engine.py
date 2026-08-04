"""Main metrics engine - orchestrates all metric operations"""

from typing import Optional, Dict, Any, List
import pandas as pd
from engine.metric_loader import get_metric_loader
from engine.snowflake_connector import get_snowflake_connector
from engine.metric_composer import MetricComposer
from engine.audit_logger import get_audit_logger
from engine.error_handler import (
    MetricNotFoundError, CompositionError, SnowflakeError,
    ErrorFormatter, AuthError
)
import os

class MetricsEngine:
    """
    Main engine for metric resolution and execution
    
    Flow:
    1. Load metric definition from YAML
    2. Check if metric exists in Snowflake
    3. If yes → Execute query
    4. If no → Try to compose from foundations
    5. If can't compose → Suggest alternatives
    6. Log operation
    7. Return result or error
    """
    
    def __init__(self, products_dir: str = "products"):
        self.loader = get_metric_loader(products_dir)
        self.connector = get_snowflake_connector(use_sso=True)
        self.composer = MetricComposer()
        self.audit_logger = get_audit_logger()
        
        # Try to auto-connect to Snowflake
        try:
            self.connector.connect()
        except Exception:
            # Connection will be attempted when actually needed
            pass
    
    def get_metric(self, metric_id: str, product: Optional[str] = None,
                  filters: Optional[Dict[str, Any]] = None,
                  user_id: str = "anonymous") -> pd.DataFrame:
        """
        Get metric data with smart resolution
        
        Args:
            metric_id: Metric identifier
            product: Optional product name (speeds up lookup)
            filters: Optional filter parameters
            user_id: User making the request (for audit logging)
        
        Returns:
            DataFrame with metric results
        
        Raises:
            MetricNotFoundError: Metric not found and can't be composed
            CompositionError: Couldn't build metric from foundations
            SnowflakeError: Snowflake connection/query failed
        """
        
        try:
            # Step 1: Load metric definition
            metric_def = self.loader.load_metric(metric_id, product)
            if not metric_def:
                # Suggest alternatives
                alternatives = self.composer.suggest_alternatives(metric_id, product)
                error = MetricNotFoundError(metric_id, [a['id'] for a in alternatives])
                
                # Log failed lookup
                self.audit_logger.log(
                    user_id=user_id,
                    action="get_metric",
                    metric_id=metric_id,
                    product=product,
                    status="NOT_FOUND",
                    error="Metric not found in repository",
                    suggestions=[a['id'] for a in alternatives]
                )
                
                raise error
            
            # Get actual product name
            actual_product = metric_def.get('product', product)
            
            # Step 2: Ensure Snowflake connection
            if not self.connector._authenticated:
                self.connector.connect()
            
            # Step 3: Try to execute metric query directly
            try:
                query = metric_def.get('sql_template')
                if query:
                    result = self.connector.execute_query(query, filters)
                    
                    # Log successful execution
                    self.audit_logger.log(
                        user_id=user_id,
                        action="get_metric",
                        metric_id=metric_id,
                        product=actual_product,
                        status="SUCCESS",
                        rows_returned=len(result),
                        source="direct_query"
                    )
                    
                    return result
            
            except SnowflakeError as e:
                # If query fails, try composition
                if "does not exist" in str(e.message):
                    pass  # Try composition below
                else:
                    raise
            
            # Step 4: Try to compose metric
            can_compose, reason = self.composer.can_compose_metric(metric_id, metric_def)
            
            if can_compose:
                result = self.composer.compose_metric(metric_id, metric_def, filters)
                
                if result is not None:
                    # Log successful composition
                    self.audit_logger.log(
                        user_id=user_id,
                        action="get_metric",
                        metric_id=metric_id,
                        product=actual_product,
                        status="SUCCESS",
                        rows_returned=len(result),
                        source="composed"
                    )
                    
                    return result
                
                # Composition returned None
                error = CompositionError(
                    metric_id,
                    ["Base metric query execution", "SQL template execution"],
                    "Query execution failed"
                )
                raise error
            
            # Step 5: Can't compose - suggest alternatives
            alternatives = self.composer.suggest_alternatives(metric_id, actual_product)
            
            # Log failed resolution
            self.audit_logger.log(
                user_id=user_id,
                action="get_metric",
                metric_id=metric_id,
                product=actual_product,
                status="UNAVAILABLE",
                error="Metric cannot be composed from available foundations",
                suggestions=[a['id'] for a in alternatives],
                reason=reason
            )
            
            error = CompositionError(
                metric_id,
                ["Direct query", "Metric composition"],
                f"Metric not available: {reason}"
            )
            raise error
        
        except (MetricNotFoundError, CompositionError, SnowflakeError, AuthError):
            raise
        except Exception as e:
            # Unexpected error
            self.audit_logger.log(
                user_id=user_id,
                action="get_metric",
                metric_id=metric_id,
                status="ERROR",
                error=str(e)
            )
            raise SnowflakeError("UNKNOWN_ERROR", str(e), e)
    
    def search_metrics(self, keyword: str = "", product: Optional[str] = None,
                      user_id: str = "anonymous") -> List[Dict]:
        """Search for metrics by keyword and product"""
        
        results = self.loader.search_metrics(keyword, product)
        
        self.audit_logger.log(
            user_id=user_id,
            action="search_metric",
            query=keyword,
            product=product,
            results_count=len(results),
            status="SUCCESS"
        )
        
        return results
    
    def list_metrics(self, product: str, user_id: str = "anonymous") -> List[Dict]:
        """List all metrics in a product"""
        
        metrics = self.loader.list_metrics(product)
        
        self.audit_logger.log(
            user_id=user_id,
            action="list_metrics",
            product=product,
            count=len(metrics),
            status="SUCCESS"
        )
        
        return metrics
    
    def get_metric_info(self, metric_id: str, product: Optional[str] = None,
                       user_id: str = "anonymous") -> Dict:
        """Get detailed information about a metric"""
        
        metric_def = self.loader.load_metric(metric_id, product)
        if not metric_def:
            raise MetricNotFoundError(metric_id)
        
        self.audit_logger.log(
            user_id=user_id,
            action="describe_metric",
            metric_id=metric_id,
            status="SUCCESS"
        )
        
        return metric_def
    
    def get_products(self) -> List[Dict]:
        """Get all available products and their metrics"""
        return self.loader.get_all_products()
    
    def close(self):
        """Close all connections"""
        self.connector.close()
