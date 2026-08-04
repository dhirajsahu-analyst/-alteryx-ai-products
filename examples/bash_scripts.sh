#!/bin/bash
# Common CLI patterns and scripts

# Get all products
echo "=== Listing all products ==="
metrics products

# Search for metrics
echo "=== Search for adoption metrics ==="
metrics search --keyword "adoption"

# List specific product
echo "=== List all designer metrics ==="
metrics list designer

# Get a metric
echo "=== Get trial signups data ==="
metrics get trial.trial_signups_total --format table

# Export to CSV
echo "=== Export to CSV ==="
metrics get plans.plans_creation_and_active_users \
  --output /tmp/plans_metrics.csv \
  --format csv

# Validate metrics
echo "=== Validate all metrics ==="
metrics validate

# Check audit logs
echo "=== View your recent activity ==="
metrics audit --user $(whoami) --limit 20

# Complex search
echo "=== Search for volume metrics ==="
metrics search --keyword "volume" --product account_user
