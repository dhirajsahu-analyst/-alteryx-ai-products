#!/usr/bin/env python3
"""
Example: Using metrics system as Python library
"""

from engine.metric_engine import MetricsEngine
import pandas as pd

def main():
    # Initialize engine
    engine = MetricsEngine()
    
    print("=" * 80)
    print("EXAMPLE 1: Get metric data")
    print("=" * 80)
    
    try:
        # Get trial signups metric
        result = engine.get_metric(
            'trial_signups_total',
            product='trial',
            user_id='demo_user'
        )
        
        print(f"\nRetrieved {len(result)} rows")
        print(result.head())
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Search for metrics")
    print("=" * 80)
    
    # Search for metrics
    results = engine.search_metrics(
        keyword='adoption',
        product='designer',
        user_id='demo_user'
    )
    
    print(f"\nFound {len(results)} metrics:")
    for metric in results:
        print(f"  - {metric['id']}: {metric['name']}")
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Get metric information")
    print("=" * 80)
    
    # Get metric details
    metric_info = engine.get_metric_info(
        'designer_2025_adoption_rate',
        product='designer',
        user_id='demo_user'
    )
    
    print(f"\nMetric: {metric_info['name']}")
    print(f"Product: {metric_info['product']}")
    print(f"Description: {metric_info['description']}")
    print(f"Status: {metric_info['status']}")
    
    print("\n" + "=" * 80)
    print("EXAMPLE 4: List all metrics in product")
    print("=" * 80)
    
    # List all metrics
    metrics = engine.list_metrics('trial', user_id='demo_user')
    
    print(f"\nTRIAL product has {len(metrics)} metrics:")
    for metric in metrics[:5]:
        print(f"  - {metric['id']}")
    if len(metrics) > 5:
        print(f"  ... and {len(metrics) - 5} more")
    
    print("\n" + "=" * 80)
    print("EXAMPLE 5: View audit logs")
    print("=" * 80)
    
    # Get audit logs
    logs = engine.audit_logger.get_logs(filters={'user_id': 'demo_user'})
    
    print(f"\nFound {len(logs)} audit log entries for demo_user:")
    for log in logs[-3:]:
        print(f"  {log['timestamp']}: {log['action']} - {log['metric_id']}")
    
    # Clean up
    engine.close()

if __name__ == '__main__':
    main()
