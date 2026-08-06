"""Production-Readiness Audit and TelemetryIQ Doctor Engine"""

import sqlite3
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple

class TelemetryIQDoctor:
    """Deterministic production-readiness auditor executing transparent, complete health checks"""
    
    def __init__(self, db_path: str = ".telemetryiq/catalog.db", products_dir: str = "products"):
        self.db_path = Path(db_path)
        self.products_dir = Path(products_dir)

    def is_available(self) -> bool:
        """Checks if compiled catalog database is available"""
        return self.db_path.exists()

    def run_audit(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Executes a complete production-readiness audit across products, metrics, and relationships
        
        Returns:
            (is_production_ready, audit_report)
        """
        report = {
            "readiness_score": 0.0,
            "summary": {
                "total_products": 0,
                "total_metrics": 0,
                "total_relationships": 0,
                "passed_checks": 0,
                "total_checks": 0
            },
            "critical_risks": [],
            "high_priority_remediations": [],
            "metric_coverage": {
                "business_definitions": 0.0,
                "owners": 0.0,
                "grains": 0.0,
                "sql_references": 0.0,
                "tags": 0.0
            },
            "product_maturity": {}
        }
        
        if not self.is_available():
            report["critical_risks"].append("SQLite Catalog database is not compiled. Run 'metrics build' first.")
            report["high_priority_remediations"].append("Execute 'metrics build' to compile and validate telemetry assets.")
            return False, report
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch products and metrics
            cursor.execute("SELECT product_id, name, raw_yaml FROM products")
            products_rows = cursor.fetchall()
            
            cursor.execute("SELECT metric_id, name, product, raw_yaml FROM metrics")
            metrics_rows = cursor.fetchall()
            
            cursor.execute("SELECT relationship_id, left_model, right_model, cardinality FROM relationships")
            relationships_rows = cursor.fetchall()
            
            report["summary"]["total_products"] = len(products_rows)
            report["summary"]["total_metrics"] = len(metrics_rows)
            report["summary"]["total_relationships"] = len(relationships_rows)
            
            # Initialize product metrics
            product_ids = [p[0] for p in products_rows]
            for p_id in product_ids:
                report["product_maturity"][p_id] = {
                    "metrics_count": 0,
                    "passed_metrics": 0,
                    "score": 0.0,
                    "missing_owners": False,
                    "missing_domains": False
                }
                
            total_checks = 0
            passed_checks = 0
            
            # 1. Product Audit
            for p_id, name, raw_yaml in products_rows:
                p_data = yaml.safe_load(raw_yaml)
                total_checks += 2
                
                # Check owners
                owners = p_data.get("owners", {})
                if not owners or not owners.get("business") or not owners.get("analytics") or not owners.get("engineering"):
                    report["product_maturity"][p_id]["missing_owners"] = True
                    report["high_priority_remediations"].append(f"Product [{p_id}]: Define complete owners (business, analytics, engineering) in product.yaml.")
                else:
                    passed_checks += 1
                    
                # Check domains
                if not p_data.get("domains"):
                    report["product_maturity"][p_id]["missing_domains"] = True
                    report["high_priority_remediations"].append(f"Product [{p_id}]: List supported business domains in product.yaml.")
                else:
                    passed_checks += 1
            
            # 2. Relationship Audit
            for rel_id, left, right, cardinality in relationships_rows:
                total_checks += 1
                if cardinality == "many_to_many":
                    report["critical_risks"].append(f"Relationship [{rel_id}] has unsafe many_to_many cardinality, posing major row-explosion risks.")
                    report["high_priority_remediations"].append(f"Relationship [{rel_id}]: Review cardinality or enforce pre-aggregation.")
                else:
                    passed_checks += 1
            
            # 3. Metric Audit
            metrics_with_biz_def = 0
            metrics_with_owner = 0
            metrics_with_grain = 0
            metrics_with_sql = 0
            metrics_with_tags = 0
            
            for m_id, m_name, product_id, raw_yaml in metrics_rows:
                m_data = yaml.safe_load(raw_yaml)
                report["product_maturity"][product_id]["metrics_count"] += 1
                
                metric_passed = True
                total_checks += 5 # 5 major quality dimensions per metric
                
                # A. Business Definition Check
                biz_def = m_data.get("definition", {}).get("business", "")
                if biz_def:
                    metrics_with_biz_def += 1
                    passed_checks += 1
                else:
                    metric_passed = False
                    report["high_priority_remediations"].append(f"Metric [{m_id}]: Add human-readable definition.business contract metadata.")
                    
                # B. Owner/Maintainer Check
                owner = m_data.get("maintainer") or m_data.get("owner")
                if owner:
                    metrics_with_owner += 1
                    passed_checks += 1
                else:
                    metric_passed = False
                    report["high_priority_remediations"].append(f"Metric [{m_id}]: Add owner/maintainer email to metric YAML.")
                    
                # C. Grain Check
                grain = m_data.get("grain")
                if grain:
                    metrics_with_grain += 1
                    passed_checks += 1
                else:
                    metric_passed = False
                    report["high_priority_remediations"].append(f"Metric [{m_id}]: Explicitly define telemetry grain (e.g. daily, monthly, point_in_time).")
                    
                # D. SQL reference Check
                sql = m_data.get("sql_template")
                if sql:
                    metrics_with_sql += 1
                    passed_checks += 1
                    
                    # E. Check for Unbounded queries (Query safety)
                    sql_upper = sql.upper()
                    if "LIMIT" not in sql_upper and "DATEADD" not in sql_upper and "BETWEEN" not in sql_upper and "PLAN_USAGE_AT" not in sql_upper:
                        report["critical_risks"].append(f"Metric [{m_id}] queries potentially unbounded Snowflake tables, violating credit-safety guardrails.")
                        report["high_priority_remediations"].append(f"Metric [{m_id}]: Enforce time-range limits or row limits in the sql_template.")
                else:
                    metric_passed = False
                    report["high_priority_remediations"].append(f"Metric [{m_id}]: Missing executable sql_template query.")
                    
                # F. Tags/Keywords Check
                tags = m_data.get("tags", [])
                if tags:
                    metrics_with_tags += 1
                    passed_checks += 1
                else:
                    metric_passed = False
                    
                if metric_passed:
                    report["product_maturity"][product_id]["passed_metrics"] += 1
            
            # Compute coverage percentages
            total_m = len(metrics_rows) if metrics_rows else 1
            report["metric_coverage"]["business_definitions"] = round((metrics_with_biz_def / total_m) * 100, 1)
            report["metric_coverage"]["owners"] = round((metrics_with_owner / total_m) * 100, 1)
            report["metric_coverage"]["grains"] = round((metrics_with_grain / total_m) * 100, 1)
            report["metric_coverage"]["sql_references"] = round((metrics_with_sql / total_m) * 100, 1)
            report["metric_coverage"]["tags"] = round((metrics_with_tags / total_m) * 100, 1)
            
            # Compute product scores
            for p_id in product_ids:
                pm = report["product_maturity"][p_id]
                m_count = pm["metrics_count"] if pm["metrics_count"] else 1
                # Base score on passed metrics percentage adjusted by product configuration completeness
                p_score = (pm["passed_metrics"] / m_count) * 100
                if pm["missing_owners"]:
                    p_score -= 10
                if pm["missing_domains"]:
                    p_score -= 10
                pm["score"] = round(max(0.0, p_score), 1)
                
            # Compute overall score
            report["summary"]["passed_checks"] = passed_checks
            report["summary"]["total_checks"] = total_checks
            
            overall_score = (passed_checks / total_checks) * 100 if total_checks else 100.0
            # De-escalate score based on critical risks
            overall_score -= len(report["critical_risks"]) * 5
            report["readiness_score"] = round(max(0.0, min(100.0, overall_score)), 1)
            
            conn.close()
            is_ready = report["readiness_score"] >= 80.0 and len(report["critical_risks"]) == 0
            return is_ready, report
            
        except Exception as e:
            report["critical_risks"].append(f"Audit run crashed: {e}")
            return False, report

# Global instance
_doctor = None

def get_telemetry_doctor(db_path: str = ".telemetryiq/catalog.db", products_dir: str = "products") -> TelemetryIQDoctor:
    """Get global doctor engine"""
    global _doctor
    if _doctor is None:
        _doctor = TelemetryIQDoctor(db_path, products_dir)
    return _doctor
