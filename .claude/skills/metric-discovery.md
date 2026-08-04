---
name: metric-discovery
type: skill
description: Discover, analyze, and generate metrics from METRIC_STORE views across all products
when_to_use: Use when you need to analyze view structure, extract columns, identify potential metrics, or refresh the complete metric catalog for a product or all products
---

# Metric Discovery & Generation Skill

**Purpose:** Automated discovery and generation of production-ready metrics from Snowflake semantic views in DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE

## What This Skill Does

1. **View Discovery** - Identifies all views with "_VIEW" suffix in METRIC_STORE
2. **Column Analysis** - Extracts column definitions (name, type, comments)
3. **Metric Identification** - Derives potential metrics from view structure
4. **YAML Generation** - Creates production-ready metric YAML files
5. **Git Integration** - Commits metrics with comprehensive messaging

## Usage Patterns

### Pattern 1: Discover Metrics for Single Product
```
/metric-discovery discover --product=ask_alteryx
```

### Pattern 2: Analyze Specific Views
```
/metric-discovery analyze --views=COPILOT_USERS_ACTIVITY_FUNNEL_VIEW,COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW
```

### Pattern 3: Refresh All Products
```
/metric-discovery refresh --all
```

### Pattern 4: Generate & Commit Metrics
```
/metric-discovery generate --product=alteryx_one --commit --message="Phase 5: Alteryx One metrics"
```

## Input Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `--product` | string | Product ID (ask_alteryx, alteryx_one, version_adoption, designer, account_user, trial) | ask_alteryx |
| `--views` | CSV string | Specific view names to analyze | COPILOT_7_15_RETENTION_RATE_VIEW |
| `--all` | boolean | Process all products | --all |
| `--commit` | boolean | Automatically commit to Git | --commit |
| `--message` | string | Custom commit message | "Add new metrics" |
| `--output-format` | string | YAML or JSON | yaml |
| `--verbose` | boolean | Detailed logging | --verbose |

## Output

### Default (Console)
```
✓ Found 8 views for ask_alteryx
├─ COPILOT_7_15_RETENTION_RATE_VIEW (3 columns → 3 metrics)
├─ COPILOT_30_60_RETENTION_RATE_VIEW (3 columns → 3 metrics)
├─ COPILOT_USERS_ADOPTION_RATE_VIEW (3 columns → 5 metrics)
├─ COPILOT_USERS_ACTIVITY_FUNNEL_VIEW (4 columns → 8 metrics)
├─ COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW (4 columns → 8 metrics)
├─ COPILOT_ELIGIBLE_ACCOUNT_FUNNEL_VIEW (5 columns → 6 metrics)
├─ COPILOT_ELIGBLE_USERS_VIEW (4 columns → 5 metrics)
└─ COPILOT_WORKFLOW_DETAILS_VIEW (2 columns → 4 metrics)

✅ Identified 42 metrics across 8 views
📊 Generated 35 YAML files (7 already exist)
🔄 Ready to commit: 35 new metrics

Commands:
- Review: /metric-discovery show --product=ask_alteryx
- Commit: /metric-discovery generate --product=ask_alteryx --commit
```

### Generated Artifacts
- YAML metric files in `products/{product}/metrics/`
- View metadata JSON
- Metric dependency graph
- SQL templates with null-safe operations

## Metric YAML Structure

Each generated metric includes:

```yaml
id: copilot_user_engagement_rate
name: "Copilot User Engagement Rate"
description: "Percentage of onboarded Copilot users who have achieved engaged status"
status: validated
category: engagement
product: ask_alteryx

definition:
  business: "Measures what percentage of users have become actively engaged"
  technical: "ENGAGED_USERS / ONBOARDED_USERS * 100"

source:
  database: DISCOVERY_PRODUCT_MANAGEMENT
  schema: METRIC_STORE
  view: COPILOT_USERS_ACTIVITY_FUNNEL_VIEW
  columns:
    - name: ENGAGED_USERS
      type: NUMBER
      description: "Count of engaged users"

sql_template: |
  SELECT
    ROUND(ENGAGED_USERS / NULLIF(ONBOARDED_USERS, 0) * 100, 2) as engagement_rate_pct
  FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW
  WHERE ONBOARDED_USERS > 0

expected_range:
  min: 0
  max: 100
  unit: percentage

grain: overall
freshness: daily
maintainer: analytics@alteryx.com

depends_on:
  - copilot_onboarded_users
  - copilot_active_users

related_metrics:
  - copilot_account_engagement_rate
  - copilot_highly_engaged_users

tags:
  - engagement
  - copilot
  - user-health
  - funnel-metric

last_updated: "2026-08-03"
version: "1.0"
```

## Implementation Details

### View Analysis Algorithm
1. Connect to Snowflake DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE
2. Query INFORMATION_SCHEMA.TABLES for views with "_VIEW" suffix
3. For each view, execute DESCRIBE VIEW to extract columns
4. Analyze column names, types, and patterns to identify metrics
5. Group metrics by category (Adoption, Engagement, Retention, Usage, Market Size, Funnel, Volume)

### Metric Derivation Rules
- **COUNT columns** → Volume metrics (count) + Adoption rates (%)
- **Percentage/Rate columns** → Direct mapping (no calculation)
- **Funnel stages** (Onboarded, Active, Engaged) → Conversion rate metrics
- **Retention windows** (7-15d, 30-60d) → Retention + Decay metrics
- **Dimension columns** (by Role, Edition, Segment) → Segmented variants

### SQL Template Generation
- All aggregate functions use NULLIF for null-safe division
- ROUND to 2 decimal places for percentages
- LIMIT 100 for result safety
- Include timestamp for audit trail
- WHERE clause ensures valid numerator/denominator

## Product Mappings

| Product | Views | Est. Metrics | Status |
|---------|-------|--------------|--------|
| ask_alteryx | 8 | 35+ | ✅ Complete |
| alteryx_one | 17 | 40+ | Ready |
| version_adoption | 8 | 15+ | Ready |
| designer | 8 | 10+ | Ready |
| account_user | 5 | 12+ | Ready |
| trial | 3 | 15+ | Ready |

## Examples

### Discover Copilot Metrics
```bash
/metric-discovery discover --product=ask_alteryx --verbose
```

### Generate All Metrics Across All Products
```bash
/metric-discovery refresh --all --commit --message="Complete Phase 5: All 127+ metrics"
```

### Analyze Specific View to Identify Metrics
```bash
/metric-discovery analyze --views=ALTERYX_ONE_ACTIVATION_FUNNEL_VIEW
```

### Generate Metrics for Alteryx One and Commit
```bash
/metric-discovery generate --product=alteryx_one --commit --message="Add 40+ Alteryx One metrics"
```

## Integration with CLI System

The generated metrics integrate seamlessly with the Product-Insights-AI system:

1. **Routing** - Product router maps questions to product
2. **Resolution** - Metric resolver finds best-matching metrics
3. **SQL Generation** - Uses metric SQL template from YAML
4. **Validation** - Checks SQL against validator rules
5. **Execution** - Runs SQL against Snowflake
6. **Response** - Returns data + metadata + SQL for transparency

## Performance Considerations

- **First Run (All Products):** ~5-10 minutes
  - Connects to Snowflake once
  - Analyzes 51 views
  - Generates 127+ metric YAMLs
  - Creates git commit

- **Single Product Run:** ~1-2 minutes
  - Direct to specific product views
  - Subset analysis and generation

- **Incremental Refresh:** ~30-60 seconds
  - Only new/changed views
  - Updates existing metrics
  - Single commit with delta message

## Caching & Efficiency

1. **View Metadata Cache** - Snowflake view structure cached for 24h
2. **Metric Index** - In-memory index of all metrics (depends_on, related)
3. **Git Staging** - Batch commits reduce overhead
4. **Incremental Updates** - Only regenerates changed metrics

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection failed" | Verify Snowflake credentials in ~/.config/alteryx/ |
| "View not found" | Confirm view exists: `SHOW VIEWS IN METRIC_STORE` |
| "No columns detected" | Check view DDL: `GET_DDL('VIEW', 'VIEW_NAME')` |
| "Git commit failed" | Verify branch protection and permissions |
| "Metrics already exist" | Use `--force` to overwrite existing metrics |

## Related Tools

- **Product-Insights-AI CLI** - Query metrics using natural language
- **GitHub Repository** - Version control for all metrics
- **Snowflake** - Semantic view definitions
- **YAML Format** - Metric configuration language

## Support

For issues, questions, or suggestions:
- Create an issue in the Product-Insights-AI repository
- Review METRICS_AVAILABLE_BY_PRODUCT.md for metric documentation
- Check VIEW_COLUMN_STRUCTURE.md for view specifications
