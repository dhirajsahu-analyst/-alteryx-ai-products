# Contributing to Alteryx Metrics System

Thank you for contributing! This guide will help you add new metrics or improve existing ones.

## Quick Start

### 1. Create a New Metric

Create a YAML file in the appropriate product directory:

```
products/<product>/metrics/<metric_id>.yaml
```

Example: `products/ask_alteryx/metrics/copilot_daily_active_users.yaml`

### 2. Metric YAML Structure

```yaml
# Unique identifier (snake_case)
id: copilot_daily_active_users

# Human-readable name
name: Copilot Daily Active Users

# Brief description (1-2 sentences)
description: Number of unique users with Copilot activity on a given day.

# Product this metric belongs to
product: ask_alteryx  # ask_alteryx, alteryx-one, plans, trial, version_adoption, account_user

# Metric category (for grouping)
category: engagement  # engagement, funnel, adoption, retention, health, activation, deployment, revenue, forecasting

# Metric status
status: active  # active, deprecated, draft

# Update frequency
freshness: daily  # daily, weekly, monthly, real-time

# Data grain/granularity
grain: daily  # point_in_time, daily, weekly, monthly

# Business and technical definitions
definition:
  business: Active users on Copilot platform, measured by unique logins or chat activity per day.
  technical: Count of distinct USER_ID_RAW where CHAT_ID IS NOT NULL grouped by date.

# Source table/view
source: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT

# Complete SQL query (use with Snowflake)
sql_template: |
  SELECT 
    CAST(CONV_CREATED_DATE AS DATE) AS date,
    COUNT(DISTINCT USER_ID_RAW) AS daily_active_users
  FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
  WHERE LICENSE_TYPE = 'Purchase'
    AND USER_TYPE = 'aacp'
    AND USER_EMAIL IS NOT NULL
    AND CHAT_ID IS NOT NULL
  GROUP BY CAST(CONV_CREATED_DATE AS DATE)
  ORDER BY date DESC

# Tags for discovery and filtering
tags:
  - copilot
  - engagement
  - daily-active
  - users

# Owner/maintainer email
maintainer: insights@alteryx.com

# Last update date (YYYY-MM-DD)
last_updated: '2026-08-05'

# Semantic version
version: '1.0'
```

### 3. SQL Query Best Practices

When writing the `sql_template`:

✅ **DO:**
- Use full Snowflake schema paths: `DISCOVERY.METRIC_STORE.TABLE_NAME`
- Filter on `LICENSE_TYPE = 'Purchase'` for customer data
- Use appropriate date filters for the grain
- Document complex logic with comments
- Test the query in Snowflake first
- Use `COUNT(DISTINCT ...)` for unique counts
- Round percentages to 4 decimal places (0.0025 = 0.25%)

❌ **DON'T:**
- Hardcode dates (use CURRENT_DATE, DATEADD, etc.)
- Mix time zones without explicit conversion
- Join across multiple fact tables without clear logic
- Leave `SELECT *` in production queries
- Assume column existence without verification

### 4. Testing Your Metric

```bash
# 1. Validate YAML syntax
python -m cli.main validate --product ask_alteryx

# 2. Test metric retrieval
python -m cli.main describe <metric_id>
python -m cli.main get <metric_id>

# 3. Check output format
python -m cli.main get <metric_id> --format json
python -m cli.main get <metric_id> --format csv
```

### 5. Metric Naming Convention

Follow this pattern for consistent naming:

**Single metric:**
- `<product>_<dimension>_<measure>`
- Example: `copilot_active_users`, `trial_conversion_rate`

**Funnel metrics:**
- `<product>_<stage>_<metric>`
- Example: `alteryx_one_user_funnel_active`, `trial_conversion_rate`

**Rate/percentage metrics:**
- Include `_rate` or `_pct` suffix
- Example: `copilot_adoption_rate_pct`, `trial_churn_rate`

**Retention metrics:**
- Include retention window
- Example: `copilot_7_day_retention_rate`, `alteryx_one_30_60_day_retention`

### 6. Creating Composite Metrics

Some metrics are built from other metrics:

```yaml
# Example: Adoption Rate (composite)
id: copilot_adoption_rate_pct
name: Copilot Adoption Rate %
definition:
  business: Percentage of eligible users actively using Copilot.
  technical: (Active Users) / (Eligible Users) * 100
composition:
  numerator: copilot_active_users
  denominator: copilot_eligible_users_2025_2
```

### 7. Documentation

For each new metric, add a line to the product's README:

```markdown
| copilot_daily_active_users | Daily unique users with Copilot activity | engagement, daily-active |
```

### 8. Pull Request Checklist

Before submitting:

- [ ] YAML is valid (no syntax errors)
- [ ] SQL query tested in Snowflake
- [ ] Metric follows naming convention
- [ ] All required fields present (id, name, description, product, sql_template, tags)
- [ ] Tags are lowercase and hyphenated
- [ ] Documentation updated
- [ ] No hardcoded dates or credentials
- [ ] Percentage metrics rounded to 4 decimals
- [ ] Tested with: `python -m cli.main get <metric_id>`

### 9. Metric Quality Standards

For approval, metrics must:

- ✅ Have complete SQL template that executes without errors
- ✅ Return consistent results (deterministic)
- ✅ Have clear business definition
- ✅ Include relevant tags for discovery
- ✅ Follow naming conventions
- ✅ Document any special filters or assumptions
- ✅ Work with `--output` and `--format` options

## Metric Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **engagement** | User/account activity | Daily Active Users, Logins |
| **funnel** | Stage progression | Signup → Activation → Engagement → Conversion |
| **adoption** | Feature/product usage | % on Latest Version, Feature Adoption |
| **retention** | Cohort-based retention | 7-Day Retention Rate, 30-Day Churn |
| **health** | Account health | Health Score, Risk Score |
| **activation** | Getting started | Activated Users, First Login |
| **deployment** | Deployment activity | Deployed Apps, Execution Count |
| **revenue** | Financial metrics | MRR, ARR, CLV, Churn Revenue |
| **forecasting** | Predictive metrics | Pipeline Value, Expansion Potential |

## Common SQL Patterns

### Distinct Count
```sql
SELECT COUNT(DISTINCT USER_ID_RAW) AS users
FROM DISCOVERY.METRIC_STORE.TABLE_NAME
WHERE condition
```

### Rate/Percentage
```sql
WITH numerator AS (
  SELECT COUNT(*) AS n FROM table WHERE condition1
),
denominator AS (
  SELECT COUNT(*) AS d FROM table WHERE condition2
)
SELECT ROUND(ROUND(100.0 * n / NULLIF(d, 0), 2) / 100, 4) AS rate_pct
FROM numerator CROSS JOIN denominator
```

### Cohort Retention
```sql
WITH first_use AS (
  SELECT USER_ID, MIN(activity_date) AS first_date
  FROM table
  GROUP BY USER_ID
),
returns AS (
  SELECT fu.USER_ID
  FROM first_use fu
  JOIN table t ON t.USER_ID = fu.USER_ID
  WHERE t.activity_date BETWEEN DATEADD(day, 7, fu.first_date) 
                            AND DATEADD(day, 15, fu.first_date)
)
SELECT COUNT(*) FROM returns
```

## Feedback & Questions

- **Questions about metrics?** → insights@alteryx.com
- **Feature request?** → GitHub Issues
- **Found a bug?** → GitHub Issues with error message

---

**Thank you for contributing!** 🎉
