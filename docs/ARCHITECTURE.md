# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Interface                            │
│  (get, search, list, describe, validate, audit commands)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MetricsEngine                                │
│  - Orchestrates metric resolution                              │
│  - Handles query execution flow                                │
│  - Manages error handling                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│MetricLoader  │  │MetricComposer│  │Snowflake     │
│              │  │              │  │Connector     │
│• Load YAML   │  │• Compose     │  │              │
│• Search      │  │• Suggest     │  │• Connect     │
│• List        │  │• Alternatives│  │• Execute     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        ▼                ▼                ▼
    ┌────────────────────────────────────┐
    │       File System / Snowflake       │
    │  - YAML metric definitions         │
    │  - Snowflake metric data           │
    └────────────────────────────────────┘
```

## Flow: User Query → Result

```
1. USER QUERY
   ↓
2. CLI COMMAND (get, search, describe, etc)
   ↓
3. METRICS ENGINE
   ├─ Load metric definition from YAML
   │  └─ Uses: MetricLoader
   │
   ├─ Try direct query execution
   │  └─ Uses: SnowflakeConnector
   │  └─ If fails → Try composition
   │
   ├─ Try metric composition
   │  └─ Uses: MetricComposer
   │  └─ Can compose from:
   │     • Base metrics (join rules)
   │     • SQL templates (can_build_from)
   │     • Stored procedures
   │  └─ If fails → Suggest alternatives
   │
   ├─ Handle errors
   │  └─ Uses: ErrorFormatter
   │  └─ Shows user-friendly message
   │  └─ Suggests alternatives or solutions
   │
   ├─ Log operation
   │  └─ Uses: AuditLogger
   │  └─ Records: user, action, metric, status, timestamp
   │
   └─ Return result
      └─ Format: Table/JSON/CSV
      └─ Save to file or display

4. OUTPUT TO USER
```

## Key Components

### 1. MetricLoader
**Responsibility**: Load and discover metrics

```python
loader = MetricLoader()
loader.load_metric(metric_id, product)  # Single metric
loader.search_metrics(keyword, product)  # Search
loader.list_metrics(product)             # List all
```

### 2. SnowflakeConnector
**Responsibility**: Manage Snowflake connections and queries

```python
connector = SnowflakeConnector(use_sso=True)
connector.connect()                          # SSO auth
connector.execute_query(query, filters)      # Run query
connector.check_table_exists(table)          # Validate
```

### 3. MetricComposer
**Responsibility**: Build metrics from foundations

```python
composer = MetricComposer()
can_compose, reason = composer.can_compose_metric(metric_id, metric_def)
result = composer.compose_metric(metric_id, metric_def, filters)
alternatives = composer.suggest_alternatives(metric_id)
```

### 4. MetricsEngine
**Responsibility**: Orchestrate everything

```python
engine = MetricsEngine()
result = engine.get_metric(metric_id, product, filters, user_id)
```

### 5. AuditLogger
**Responsibility**: Log all operations

```python
logger = AuditLogger()
logger.log(user_id, action, metric_id, status, ...)
logs = logger.get_logs(filters={...})
```

## YAML Metric Definition Structure

```yaml
# Metric identification
id: trial_signups_total
name: Trial Signups (Total)
description: Total number of trial registrations
product: trial

# Metadata
status: validated
category: volume
tags: [trial, volume, funnel]

# Definitions
definition:
  business: |
    Top-of-funnel metric tracking trial program awareness and interest
  technical: |
    Aggregated from TRIAL_FUNNEL_METRICS_OVERALL_VIEW

# Source information
source:
  database: DISCOVERY_PRODUCT_MANAGEMENT
  schema: METRIC_STORE
  base_tables:
    - TRIAL_FUNNEL_METRICS_OVERALL

# Main query
sql_template: |
  SELECT
    DATE,
    TOTAL_TRIAL_REGISTRATION,
    QL,
    SAL
  FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.TRIAL_FUNNEL_METRICS_OVERALL_VIEW

# Query variations
queries:
  - name: base
    description: Full metric query
    query: |
      SELECT ... FROM ...
  
  - name: daily
    description: Daily snapshot
    query: |
      SELECT ... WHERE DATE = ?
  
  - name: monthly
    description: Monthly aggregation
    query: |
      SELECT DATE_TRUNC('month', DATE) AS month, ... GROUP BY month

# Composition rules (optional)
can_build_from:
  base_metrics:
    - trial_ql_conversion
    - trial_sql_conversion
  join_rule:
    join_on: [date, account_id]
    join_type: inner
  # OR use SQL template
  sql_template: |
    SELECT ... FROM base_metrics ...

# Aggregation info
aggregation_level: monthly
grain: monthly
freshness: daily

# Dependencies
filters: []
depends_on: [trial_funnel_stages_monthly]
related_metrics: [trial_ql_conversion, trial_sql_conversion]

# Metadata
maintainer: product-team@alteryx.com
last_updated: '2026-08-04'
version: '1.0'
