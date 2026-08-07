"""Automated dataset generator compiling telemetry metrics from Snowflake for TelemetryIQ Dashboard"""

import os
import json
import time
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from engine.metric_engine import MetricsEngine
from engine.compiler.compiler import get_catalog_compiler

def main():
    print("🚀 Initiating TelemetryIQ Dashboard Dataset Refresh...")
    
    # 1. Compile catalog to ensure database is perfectly synchronized
    compiler = get_catalog_compiler()
    success, build_summary = compiler.compile()
    if not success:
        print("✗ Catalog compilation failed. Exiting.", file=sys.stderr)
        sys.exit(1)
        
    print(f"✓ Catalog compiled successfully. {build_summary['metrics_compiled']} metrics cached.")
    
    # Create output directory for dashboard if not exists
    output_dir = Path("docs/dashboard")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    engine = MetricsEngine()
    
    # Define a set of highly optimized, certified metrics to query from Snowflake
    # This covers all 7 product domains with real, live data from pre-aggregated views
    target_metrics = {
        "alteryx_one": [
            "alteryx_one_monthly_active_users",
            "alteryx_one_deployment_rate",
            "alteryx_one_workspace_creation_rate"
        ],
        "plans": [
            "plans_engagement_engagement_score",
            "plans_engagement_rate"
        ],
        "ask_alteryx": [
            "copilot_total_accounts",
            "copilot_adoption_percentage",
            "copilot_workflow_adoption_pct"
        ],
        "trial": [
            "trial_conversion_rate",
            "trial_funnel_signups",
            "trial_user_engagement"
        ],
        "designer": [
            "designer_engagement_daily_active_users",
            "designer_usage_patterns_error_rate",
            "designer_health_performance_issues"
        ],
        "version_adoption": [
            "version_adoption_compliance_rate",
            "version_adoption_adoption_adoption_rate"
        ],
        "account_user": [
            "account_user_engagement_rate",
            "account_user_funnel_active"
        ]
    }
    
    dataset = {
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "metrics_data": {},
        "products": []
    }
    
    # Load products metadata for display names and descriptions
    products = engine.get_products()
    dataset["products"] = products
    
    # Loop over product domains and execute queries safely
    for p in products:
        p_id = p["product_id"]
        dataset["metrics_data"][p_id] = {}
        
        # Get list of target metrics for this product
        m_list = target_metrics.get(p_id, [])
        
        for m_id in m_list:
            print(f"Querying [{p_id}:{m_id}] from Snowflake...")
            try:
                # Retrieve metric definition
                m_def = engine.get_metric_info(m_id, p_id)
                if not m_def:
                    continue
                    
                # Execute Snowflake query with 30s timeout safety
                df = engine.get_metric(m_id, p_id)
                
                # Convert pandas DataFrame to standard JSON records
                records = df.to_dict(orient="records")
                
                dataset["metrics_data"][p_id][m_id] = {
                    "metric_id": m_id,
                    "name": m_def.get("name", m_id),
                    "description": m_def.get("description", ""),
                    "grain": m_def.get("grain", "monthly"),
                    "status": m_def.get("status", "active"),
                    "data": records,
                    "columns": list(df.columns) if not df.empty else [],
                    "error": None
                }
                print(f"  ✓ [{m_id}] returned {len(records)} rows successfully.")
                
            except Exception as e:
                # Gracefully catch Snowflake errors / timeouts
                print(f"  ✗ [{m_id}] query failed: {e}", file=sys.stderr)
                # Load metadata to still show the card in UI
                m_def = engine.get_metric_info(m_id, p_id) or {}
                dataset["metrics_data"][p_id][m_id] = {
                    "metric_id": m_id,
                    "name": m_def.get("name", m_id),
                    "description": m_def.get("description", ""),
                    "grain": m_def.get("grain", "monthly"),
                    "status": "dormant",
                    "data": [],
                    "columns": [],
                    "error": str(e)
                }
                
    # Save compilation payload
    output_path = output_dir / "dashboard_data.json"
    with open(output_path, "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"\n✓ Dashboard dataset compilation complete. Saved to: {output_path}")

if __name__ == "__main__":
    main()
