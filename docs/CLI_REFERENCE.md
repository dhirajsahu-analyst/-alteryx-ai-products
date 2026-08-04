# CLI Command Reference

Complete guide to all 9 metrics CLI commands.

## Quick Reference

```bash
metrics search [KEYWORD]              # Search for metrics
metrics list PRODUCT                  # List all metrics in product
metrics get METRIC_ID                 # Get metric data
metrics describe METRIC_ID            # Show metric details
metrics products                      # List all products
metrics validate                      # Validate metrics
metrics audit                         # View audit logs
metrics auth                          # Manage authentication
metrics --help                        # Show help
```

---

## Commands

### 1. `metrics search`

Search for metrics by keyword and product.

**Syntax:**
```bash
metrics search [KEYWORD] [OPTIONS]
```

**Arguments:**
- `KEYWORD` - Search term (optional)

**Options:**
- `--product, -p TEXT` - Filter by product
- `--limit, -l INTEGER` - Max results (default: 50)

**Examples:**
```bash
# Search all metrics for "adoption"
metrics search adoption

# Search in designer product for "version"
metrics search version --product designer

# Search ask_alteryx for "engagement"
metrics search engagement --product ask_alteryx

# Show 100 results
metrics search --limit 100
```

**Output:**
Table with metric ID, product, name, and status

---

### 2. `metrics list`

List all metrics in a specific product.

**Syntax:**
```bash
metrics list PRODUCT
```

**Arguments:**
- `PRODUCT` (required) - Product name

**Examples:**
```bash
# List all trial metrics
metrics list trial

# List all plans metrics
metrics list plans

# List all designer metrics
metrics list designer
```

**Output:**
Formatted table with metric ID, name, category, and status

---

### 3. `metrics get`

Retrieve metric data from Snowflake.

**Syntax:**
```bash
metrics get METRIC_ID [OPTIONS]
```

**Arguments:**
- `METRIC_ID` (required) - Metric identifier

**Options:**
- `--product, -p TEXT` - Product name (speeds up lookup)
- `--format, -f [table|json|csv]` - Output format (default: table)
- `--output, -o FILE` - Save to file
- `--filter KEY=VALUE` - Add filters (repeatable)

**Examples:**
```bash
# Get metric, display as table
metrics get trial.trial_signups_total

# Get metric, save to CSV
metrics get plans.plans_creation_and_active_users \
  --output plans.csv --format csv

# Get with filters
metrics get trial.trial_signups_total \
  --filter start_date=2026-01-01

# Export to JSON
metrics get designer.designer_2025_adoption_rate \
  --output adoption.json --format json
```

**Output:**
Data in specified format (table, JSON, or CSV)

---

### 4. `metrics describe`

Show detailed information about a metric.

**Syntax:**
```bash
metrics describe METRIC_ID [OPTIONS]
```

**Arguments:**
- `METRIC_ID` (required) - Metric identifier

**Options:**
- `--product, -p TEXT` - Product name (optional)

**Examples:**
```bash
# Describe a metric
metrics describe trial.trial_signups_total

# With product specified
metrics describe alteryx_one_active_users --product alteryx-one
```

**Output:**
- Metric name and description
- Product, status, category
- Business and technical definitions
- Source database, schema, base tables
- Aggregation level, freshness
- Maintainer and last updated

---

### 5. `metrics products`

List all available products and their metrics count.

**Syntax:**
```bash
metrics products
```

**Examples:**
```bash
metrics products
```

**Output:**
Table with product name, full name, metric count, and status

---

### 6. `metrics validate`

Validate metric definitions and Snowflake availability.

**Syntax:**
```bash
metrics validate [OPTIONS]
```

**Options:**
- `--product, -p TEXT` - Validate specific product only

**Examples:**
```bash
# Validate all metrics
metrics validate

# Validate specific product
metrics validate --product designer

# Validate trial product
metrics validate --product trial
```

**Output:**
- Per-metric validation status
- Summary: valid count, invalid count
- Issues and error messages

---

### 7. `metrics audit`

View audit logs of all metric operations.

**Syntax:**
```bash
metrics audit [OPTIONS]
```

**Options:**
- `--user, -u TEXT` - Filter by user
- `--action, -a TEXT` - Filter by action (get_metric, search, etc)
- `--limit, -l INTEGER` - Number of entries (default: 50)

**Examples:**
```bash
# View your recent activity
metrics audit --user $(whoami)

# View all failed operations
metrics audit --action get_metric --user you --limit 100

# View all searches
metrics audit --action search_metric

# View last 100 entries
metrics audit --limit 100
```

**Output:**
Table with timestamp, user, action, metric, and status

---

### 8. `metrics auth`

Manage Snowflake authentication.

**Syntax:**
```bash
metrics auth [OPTIONS]
```

**Options:**
- `--relogin` - Force re-authentication

**Examples:**
```bash
# Re-authenticate with Snowflake
metrics auth --relogin
```

**Output:**
Authentication status and confirmation

---

### 9. `metrics --help`

Show help for all commands.

**Syntax:**
```bash
metrics --help
metrics [COMMAND] --help
```

**Examples:**
```bash
# Show all commands
metrics --help

# Show help for specific command
metrics get --help
metrics search --help
```

---

## Common Workflows

### Workflow 1: Find and Export Metric

```bash
# 1. Search for metric
metrics search adoption --product designer

# 2. Get details
metrics describe designer.designer_2025_adoption_rate

# 3. Export to CSV
metrics get designer.designer_2025_adoption_rate \
  --output adoption_report.csv --format csv
```

### Workflow 2: Check Metrics in Product

```bash
# 1. List all metrics
metrics list plans

# 2. Get specific metric
metrics get plans.plans_creation_and_active_users

# 3. Save to file
metrics get plans.plans_creation_and_active_users \
  --output /tmp/plans_data.json --format json
```

### Workflow 3: Audit Your Activity

```bash
# View all your recent queries
metrics audit --user $(whoami) --limit 50

# See failed queries
metrics audit --user $(whoami) --action get_metric
```

### Workflow 4: Validate Metrics

```bash
# Check all metrics
metrics validate

# Check specific product
metrics validate --product trial

# See results
metrics audit --action validate
```

---

## Error Messages & Solutions

### "Metric not found"
```bash
# Try searching
metrics search --keyword "your_metric_name"

# List all in product
metrics list designer
```

### "Snowflake connection failed"
```bash
# Re-authenticate
metrics auth --relogin

# Check status
metrics products
```

### "Could not compose metric"
Metric is not available. Check alternatives:
```bash
# Search similar
metrics search [similar_keyword]

# Contact: insights@alteryx.com
```

---

## Tips & Tricks

**Save output to file:**
```bash
metrics get metric_id --output file.csv --format csv
```

**Search multiple keywords (one at a time):**
```bash
metrics search adoption
metrics search version
```

**Check if metrics are available:**
```bash
metrics validate --product designer
```

**Track your usage:**
```bash
metrics audit --user $(whoami)
```

---

## Environment Variables

These can be set in `.env` file:

```bash
SNOWFLAKE_ACCOUNT=ALTERYX-ALTERYX_EDW
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=DISCOVERY_PRODUCT_MANAGEMENT
SNOWFLAKE_SCHEMA=METRIC_STORE
USER=your_email@alteryx.com
```

---

## Support

For issues or questions:
- 📧 Email: insights@alteryx.com
- 📋 GitHub Issues: https://github.com/alteryx/metrics-system/issues
- 💬 Slack: #metrics-support
