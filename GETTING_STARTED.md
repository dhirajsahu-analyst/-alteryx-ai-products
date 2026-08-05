# 🚀 Getting Started with Alteryx Metrics System

Complete step-by-step guide to install, configure, and use the metrics system.

## Prerequisites

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Git** - [Download here](https://git-scm.com/)
- **Alteryx email** with Snowflake access
- **Internet connection** for SSO login

## Installation (5 Minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/dhirajsahu-analyst/-alteryx-ai-products.git
cd -alteryx-ai-products
```

### Step 2: Setup Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv venv

# Activate it
source venv/bin/activate  
# On Windows: venv\Scripts\activate

# Verify activation (prompt should show (venv))
which python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install system in development mode
pip install -e .

# Verify (no errors should appear)
python -m cli.main version
```

### Step 4: Configure Snowflake

```bash
# Copy configuration template
cp .env.example .env

# Edit with your email
nano .env
# or use your favorite editor
```

**Required changes:**
```bash
SNOWFLAKE_USER=YOUR_EMAIL@ALTERYX.COM    # ← Change this
USER=YOUR_EMAIL@ALTERYX.COM              # ← Change this

# Leave these as-is:
SNOWFLAKE_ACCOUNT=ALTERYX-ALTERYX_EDW
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=DISCOVERY_PRODUCT_MANAGEMENT
SNOWFLAKE_SCHEMA=METRIC_STORE
```

Save and exit (Ctrl+X in nano, then Y, then Enter)

### Step 5: Test Connection

```bash
# List all products (will open browser for SSO login on first run)
python -m cli.main products
```

**Expected output:**
```
Available products:
  • ask_alteryx (28 metrics)
  • alteryx-one (23 metrics)
  • plans (16 metrics)
  • trial (14 metrics)
  • version_adoption (16 metrics)
  • account_user (16 metrics)
```

✅ **Success!** You're ready to query metrics.

## Your First Queries (2 Minutes)

### Query 1: List Metrics in a Product

```bash
python -m cli.main list ask_alteryx
```

**Output:**
```
Metrics in ask_alteryx (28 total):

 ID                              | Name
 ────────────────────────────────────────────────────────────────
 copilot_onboarded_users         | Copilot Onboarded Users
 copilot_active_users            | Copilot Active Users
 copilot_engaged_users           | Copilot Engaged Users
 copilot_7_15_day_retention_rate | Copilot 7-15 Day Retention %
 ...
```

### Query 2: Get Your First Metric

```bash
python -m cli.main get ask_alteryx.copilot_active_users
```

**Output:**
```
Executing: ask_alteryx.copilot_active_users

┌──────────────────────────────────────────┐
│ ACTIVE_USERS                             │
├──────────────────────────────────────────┤
│ 2847                                     │
└──────────────────────────────────────────┘

✓ Query completed in 2.34 seconds
✓ Audit logged with ID: AUD_2026080510150001
```

### Query 3: Search for Metrics

```bash
python -m cli.main search --keyword "retention"
```

**Output:**
```
Found 6 metrics matching "retention":

 ask_alteryx.copilot_7_15_day_retention_rate
   - Copilot 7-15 Day Retention Rate %
   - Tags: copilot, retention, cohort-analysis

 ask_alteryx.copilot_30_60_day_retention_rate
   - Copilot 30-60 Day Retention Rate %
   - Tags: copilot, retention, cohort-analysis

 alteryx-one.retention_7_days
   - Alteryx One 7-Day Retention
   - Tags: alteryx-one, retention, cohort
 ...
```

### Query 4: Export to CSV

```bash
python -m cli.main get trial.trial_signups_total \
  --output trial_data.csv \
  --format csv
```

**Output:**
```
✓ Results saved to trial_data.csv (127 rows)
```

### Query 5: View Metric Details

```bash
python -m cli.main describe ask_alteryx.copilot_adoption_rate_pct
```

**Output:**
```
Metric: Copilot Adoption Rate %
ID: ask_alteryx.copilot_adoption_rate_pct
Product: ask_alteryx

Description:
  Percentage of eligible users actively using Copilot

Definition (Business):
  Adoption metric showing what % of eligible users are using Copilot

Definition (Technical):
  (Active Users) / (Eligible Users) * 100, filtered by 2025 pricing

Source: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT

Tags: copilot, adoption, rate-metric
Last Updated: 2026-08-05
Maintainer: insights@alteryx.com
```

## Common Operations

### Export to Different Formats

```bash
# CSV (default)
python -m cli.main get trial.conversion_rate_pct \
  --format csv --output results.csv

# JSON
python -m cli.main get plans.mrr \
  --format json --output mrr.json

# Parquet (binary, efficient for large datasets)
python -m cli.main get alteryx-one.user_funnel_active \
  --format parquet --output data.parquet
```

### Search for Metrics

```bash
# Search all products
python -m cli.main search --keyword "adoption"

# Search specific product
python -m cli.main search --product alteryx-one --keyword "retention"

# Search by tag
python -m cli.main search --tag "engagement"
```

### Validate Metrics

```bash
# Check all metrics work
python -m cli.main validate

# Validate specific product
python -m cli.main validate --product alteryx-one

# Show validation errors
python -m cli.main validate --verbose
```

## Using as Python Library

```python
from engine.metric_engine import MetricsEngine

# Initialize
engine = MetricsEngine()

# Get metric
result = engine.get_metric('trial_signups_total', product='trial')
print(f"Total signups: {result['SIGNUPS'].sum()}")

# Search metrics
metrics = engine.search_metrics('adoption', product='ask_alteryx')
for m in metrics:
    print(f"{m['id']}: {m['name']}")

# List all in product
all_metrics = engine.list_metrics('plans')
print(f"Found {len(all_metrics)} metrics in plans")
```

## Real-World Examples

### Example: Monitor Copilot Adoption

```bash
# Daily active users
python -m cli.main get ask_alteryx.copilot_active_users

# Adoption percentage
python -m cli.main get ask_alteryx.copilot_adoption_rate_pct

# Export retention data
python -m cli.main get ask_alteryx.copilot_7_15_day_retention_rate_pct \
  --format csv --output copilot_retention.csv
```

### Example: Trial Conversion Funnel

```bash
# Signups → Activation → Engagement → Conversion
python -m cli.main get trial.monthly_signups
python -m cli.main get trial.activation_rate_pct
python -m cli.main get trial.engagement_rate_pct
python -m cli.main get trial.conversion_rate_pct
```

### Example: Track Subscription Health

```bash
# Check active subscriptions
python -m cli.main get plans.total_active_subscriptions

# Monitor churn
python -m cli.main get plans.churn_rate

# View MRR
python -m cli.main get plans.monthly_recurring_revenue

# Enterprise plan focus
python -m cli.main get plans.mrr_by_plan_tier_enterprise
```

## Troubleshooting

### Browser Auth Doesn't Open

**Problem:** Browser authentication window doesn't appear

**Solution:**
```bash
# Clear cached credentials
rm ~/.snowsql/config

# Try again (browser should open)
python -m cli.main products
```

### "Metric Not Found" Error

**Problem:** Can't find a specific metric

**Solution:**
```bash
# Search for similar metrics
python -m cli.main search --keyword "activation"

# List all in product
python -m cli.main list alteryx-one

# Check all products
python -m cli.main products
```

### "Query Timeout" Error

**Problem:** Query takes too long to execute

**Solution:**
```bash
# Some metrics have date filters available
python -m cli.main describe trial.monthly_signups

# Check if filters are supported
python -m cli.main get trial.monthly_signups --help
```

### Import Errors After Installation

**Problem:** `ModuleNotFoundError: No module named 'cli'`

**Solution:**
```bash
# Reinstall in development mode
pip install -e .

# Verify installation
python -m cli.main version
```

## Next Steps

✅ **Read CLI Reference** → [docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md)

✅ **Explore Examples** → [examples/](./examples/)

✅ **Add New Metrics** → [CONTRIBUTING.md](./CONTRIBUTING.md)

✅ **System Design** → [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)

✅ **FAQ** → [docs/FAQ.md](./docs/FAQ.md)

## Getting Help

| Question | Where to Find Answer |
|----------|----------------------|
| How do I search metrics? | [docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md) |
| What metrics are available? | Run: `python -m cli.main products` |
| How do I export data? | See "Export to Different Formats" above |
| How do I add a metric? | [CONTRIBUTING.md](./CONTRIBUTING.md) |
| Authentication issues? | See "Troubleshooting" section above |

**Still need help?** → insights@alteryx.com

---

**Congratulations!** 🎉 You've successfully set up the Alteryx Metrics System.

**Next:** Try `python -m cli.main get ask_alteryx.copilot_active_users`
