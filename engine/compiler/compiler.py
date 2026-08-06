"""Deterministic repository compiler for TelemetryIQ"""

import os
import sys
import json
import sqlite3
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from engine.catalog.validator import get_schema_validator

class CatalogCompiler:
    """Discovers, validates, and compiles telemetry products and metrics into local SQLite database"""
    
    def __init__(self, products_dir: str = "products", output_dir: str = ".telemetryiq"):
        self.products_dir = Path(products_dir)
        self.output_dir = Path(output_dir)
        self.validator = get_schema_validator()
        self.db_path = self.output_dir / "catalog.db"

    def compile(self) -> Tuple[bool, Dict]:
        """
        Runs the compilation pipeline
        
        Returns:
            (is_successful, build_summary)
        """
        # 1. Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Reset or initialize sqlite database
        if self.db_path.exists():
            self.db_path.unlink()
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute("""
            CREATE TABLE products (
                product_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT,
                version TEXT,
                owners_business TEXT,
                owners_analytics TEXT,
                owners_engineering TEXT,
                domains TEXT,
                raw_yaml TEXT
            )
        """)
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE metrics (
                metric_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                product TEXT NOT NULL,
                category TEXT,
                status TEXT,
                grain TEXT,
                sql_template TEXT,
                raw_yaml TEXT,
                FOREIGN KEY (product) REFERENCES products(product_id)
            )
        """)
        
        # Create relationships table
        cursor.execute("""
            CREATE TABLE relationships (
                relationship_id TEXT PRIMARY KEY,
                left_model TEXT NOT NULL,
                right_model TEXT NOT NULL,
                left_keys TEXT NOT NULL,
                right_keys TEXT NOT NULL,
                cardinality TEXT,
                approved_join_type TEXT,
                raw_yaml TEXT
            )
        """)
        
        conn.commit()
        
        summary = {
            "products_discovered": 0,
            "products_compiled": 0,
            "metrics_discovered": 0,
            "metrics_compiled": 0,
            "relationships_discovered": 0,
            "relationships_compiled": 0,
            "errors": [],
            "warnings": []
        }
        
        # 3. Discover products
        if not self.products_dir.exists():
            summary["errors"].append(f"Products directory '{self.products_dir}' does not exist.")
            conn.close()
            return False, summary
            
        for product_dir in sorted(self.products_dir.iterdir()):
            if not product_dir.is_dir():
                continue
                
            summary["products_discovered"] += 1
            product_id = product_dir.name
            
            # Look for product.yaml or fallback to product_context.yaml
            product_file = product_dir / "product.yaml"
            is_legacy = False
            if not product_file.exists():
                product_file = product_dir / "product_context.yaml"
                is_legacy = True
                
            if not product_file.exists():
                summary["warnings"].append(f"Product [{product_id}]: No product.yaml or product_context.yaml found.")
                # We can still synthesize a minimal product metadata to allow compilation
                product_data = {
                    "product_id": product_id.replace("-", "_"),
                    "name": product_id.replace("_", " ").title(),
                    "description": f"Synthesized manifest for {product_id}",
                    "status": "active",
                    "version": "1.0.0",
                    "owners": {
                        "business": "unknown@alteryx.com",
                        "analytics": "unknown@alteryx.com",
                        "engineering": "unknown@alteryx.com"
                    },
                    "domains": []
                }
            else:
                try:
                    with open(product_file, "r") as f:
                        product_data = yaml.safe_load(f)
                except Exception as e:
                    summary["errors"].append(f"Product [{product_id}]: Failed to parse YAML: {e}")
                    continue
            
            if not product_data or not isinstance(product_data, dict):
                summary["errors"].append(f"Product [{product_id}]: Empty or invalid YAML manifest.")
                continue
                
            # Normalize product_id to ensure snake_case compatibility
            p_id = product_data.get("product_id", product_id).replace("-", "_")
            product_data["product_id"] = p_id
            
            # Validate product manifest
            is_valid, err_msg = self.validator.validate_product(product_data)
            if not is_valid:
                summary["warnings"].append(f"Product [{p_id}] validation warning: {err_msg}")
            
            # Serialize fields for database
            owners = product_data.get("owners", {})
            owners_biz = owners.get("business", "unknown@alteryx.com")
            owners_anal = owners.get("analytics", "unknown@alteryx.com")
            owners_eng = owners.get("engineering", "unknown@alteryx.com")
            domains_str = json.dumps(product_data.get("domains", []))
            raw_yaml = yaml.dump(product_data)
            
            # Insert into database
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO products (
                        product_id, name, description, status, version, 
                        owners_business, owners_analytics, owners_engineering, domains, raw_yaml
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p_id,
                    product_data.get("name", p_id),
                    product_data.get("description", ""),
                    product_data.get("status", "active"),
                    product_data.get("version", "1.0.0"),
                    owners_biz,
                    owners_anal,
                    owners_eng,
                    domains_str,
                    raw_yaml
                ))
                summary["products_compiled"] += 1
            except sqlite3.Error as e:
                summary["errors"].append(f"Product [{p_id}]: Database insert failed: {e}")
                continue
                
            # 4. Discover metrics for this product
            metrics_dir = product_dir / "metrics"
            if not metrics_dir.exists() or not metrics_dir.is_dir():
                continue
                
            for metric_file in sorted(metrics_dir.glob("*.yaml")):
                summary["metrics_discovered"] += 1
                metric_id = metric_file.stem
                
                try:
                    with open(metric_file, "r") as f:
                        metric_data = yaml.safe_load(f)
                except Exception as e:
                    summary["errors"].append(f"Metric [{p_id}:{metric_id}]: Failed to parse YAML: {e}")
                    continue
                    
                if not metric_data or not isinstance(metric_data, dict):
                    summary["errors"].append(f"Metric [{p_id}:{metric_id}]: Empty or invalid YAML definition.")
                    continue
                    
                # Normalize metric ID fields
                m_id = metric_data.get("id", metric_id)
                metric_data["id"] = m_id
                metric_data["product"] = p_id  # Enforce matching parent product ID
                
                # Validate metric definition
                is_valid, err_msg = self.validator.validate_metric(metric_data)
                if not is_valid:
                    summary["warnings"].append(f"Metric [{p_id}:{m_id}] validation warning: {err_msg}")
                    
                # Insert into database
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO metrics (
                            metric_id, name, description, product, category, status, grain, sql_template, raw_yaml
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        m_id,
                        metric_data.get("name", m_id),
                        metric_data.get("description", ""),
                        p_id,
                        metric_data.get("category", ""),
                        metric_data.get("status", "active"),
                        metric_data.get("grain", "daily"),
                        metric_data.get("sql_template", ""),
                        yaml.dump(metric_data)
                    ))
                    summary["metrics_compiled"] += 1
                except sqlite3.Error as e:
                    summary["errors"].append(f"Metric [{p_id}:{m_id}]: Database insert failed: {e}")
        
        # 5. Discover and compile relationships
        shared_rel_dir = Path("shared/relationships")
        rel_files = []
        if shared_rel_dir.exists():
            rel_files.extend(list(shared_rel_dir.glob("*.yaml")))
            
        if self.products_dir.exists():
            for product_dir in self.products_dir.iterdir():
                if product_dir.is_dir():
                    p_rel_dir = product_dir / "relationships"
                    if p_rel_dir.exists():
                        rel_files.extend(list(p_rel_dir.glob("*.yaml")))
                        
        for rel_file in sorted(rel_files):
            summary["relationships_discovered"] += 1
            try:
                with open(rel_file, "r") as f:
                    rel_data = yaml.safe_load(f)
            except Exception as e:
                summary["errors"].append(f"Relationship [{rel_file.name}]: Failed to parse YAML: {e}")
                continue
                
            if not rel_data or not isinstance(rel_data, dict):
                summary["errors"].append(f"Relationship [{rel_file.name}]: Empty or invalid YAML definition.")
                continue
                
            rel_id = rel_data.get("relationship_id")
            if not rel_id:
                summary["errors"].append(f"Relationship [{rel_file.name}]: Missing relationship_id.")
                continue
                
            is_valid, err_msg = self.validator.validate_relationship(rel_data)
            if not is_valid:
                summary["warnings"].append(f"Relationship [{rel_id}] validation warning: {err_msg}")
                
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO relationships (
                        relationship_id, left_model, right_model, left_keys, right_keys, cardinality, approved_join_type, raw_yaml
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rel_id,
                    rel_data.get("left_model"),
                    rel_data.get("right_model"),
                    json.dumps(rel_data.get("left_keys", [])),
                    json.dumps(rel_data.get("right_keys", [])),
                    rel_data.get("cardinality"),
                    rel_data.get("approved_join_type"),
                    yaml.dump(rel_data)
                ))
                summary["relationships_compiled"] += 1
            except sqlite3.Error as e:
                summary["errors"].append(f"Relationship [{rel_id}]: Database insert failed: {e}")
        
        conn.commit()
        conn.close()
        
        # Save a build_manifest.json
        manifest_path = self.output_dir / "build_manifest.json"
        try:
            with open(manifest_path, "w") as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            summary["errors"].append(f"Failed to save build manifest: {e}")
            
        is_successful = len(summary["errors"]) == 0
        return is_successful, summary

# Global instance
_compiler = None

def get_catalog_compiler(products_dir: str = "products", output_dir: str = ".telemetryiq") -> CatalogCompiler:
    """Get global catalog compiler"""
    global _compiler
    if _compiler is None:
        _compiler = CatalogCompiler(products_dir, output_dir)
    return _compiler
