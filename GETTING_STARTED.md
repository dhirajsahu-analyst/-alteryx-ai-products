# 🚀 Getting Started with Alteryx Metrics System

## Installation

### Prerequisites
- Python 3.9+
- Snowflake account with SSO access
- Git

### Quick Setup (5 minutes)

1. **Clone the repository**
```bash
git clone https://github.com/alteryx/metrics-system.git
cd metrics-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
# Copy the example config
cp .env.example .env

# Edit .env with your details
# SNOWFLAKE_ACCOUNT=ALTERYX-ALTERYX_EDW
# SNOWFLAKE_WAREHOUSE=COMPUTE_WH
# SNOWFLAKE_DATABASE=DISCOVERY_PRODUCT_MANAGEMENT
# SNOWFLAKE_SCHEMA=METRIC_STORE
```

4. **Install as CLI tool**
```bash
pip install -e .
```

5. **Verify installation**
```bash
metrics --help
```

## Your First Metric Query

### 1. Search for metrics
```bash
metrics search --product plans --keyword "creation"
```

Output:
```
Found 3 metrics matching "creation":
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Metric ID               ┃ Product ┃ Name                   ┃ Status  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ plans_creation_and_...  │ plans   │ Plans Creation and...  │ active  │
│ plan_created_date_...   │ plans   │ Plan Created Date...   │ active  │
└─────────────────────────┴─────────┴────────────────────────┴─────────┘
```

### 2. View metric details
```bash
metrics describe plans.plans_creation_and_active_users
```

Output:
```
Metric: Plans Creation and Active Users
ID: plans_creation_and_active_users

Basic Information:
  Product: plans
  Status: validated
  Category: product_metric
  Description: Tracks plans creation and active user counts

Definition:
  Business: Number of plans created and active users engaging with plans
  Technical: Aggregated from PLANS_DAILY_USERS_AV and PLANS_MONTHLY_ACCOUNT_AV

Source:
  Database: DISCOVERY_PRODUCT_MANAGEMENT
  Schema: METRIC_STORE
  Base Tables:
    • USERS_BASE
    • PLANS_FACT
    • PLANS_GRANULAR
```

### 3. Get metric data
```bash
# Simple query
metrics get plans.plans_creation_and_active_users

# With filters
metrics get plans.plans_creation_and_active_users \
  --filter start_date=2026-01-01 \
  --filter end_date=2026-08-04

# Save to file
metrics get plans.plans_creation_and_active_users \
  --output results.csv \
  --format csv
```

### 4. List all metrics in a product
```bash
metrics list designer
```

### 5. View audit logs
```bash
# Your activity
metrics audit --user $(whoami)

# Failed queries
metrics audit --status FAILED

# Last 100 entries
metrics audit --limit 100
```

## Using as a Python Library

```python
from engine.metric_engine import MetricsEngine
import pandas as pd

# Initialize engine
engine = MetricsEngine()

# Get metric data
result = engine.get_metric(
    'trial_signups_total',
    product='trial',
    filters={'start_date': '2026-01-01'}
)

# Use as pandas DataFrame
print(f"Retrieved {len(result)} rows")
print(result.head())

# Save to file
result.to_csv('trial_signups.csv', index=False)
result.to_json('trial_signups.json')
```

## Common Tasks

### Search across all products
```bash
metrics search --keyword "adoption"
```

### Validate all metrics
```bash
metrics validate
```

### Validate specific product
```bash
metrics validate --product designer
```

### List all products
```bash
metrics products
```

## Troubleshooting

### "Metric not found"
```bash
# Search for similar metrics
metrics search --keyword "your_metric_name"

# Check if it's in a different product
metrics search "your_metric_name" --product alteryx-one
```

### "Snowflake connection failed"
```bash
# Re-authenticate with SSO
metrics auth --relogin

# Check warehouse status
# Visit: https://alteryx.snowflakecomputing.com
```

### "Could not compose metric"
The underlying tables might not be available. Contact:
📧 insights@alteryx.com

## Next Steps

- 📖 Read [CLI_REFERENCE.md](./docs/CLI_REFERENCE.md) for all commands
- 📚 Check [examples/](./examples/) for more use cases
- 🔧 See [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for system design
- 📓 Try [Jupyter notebooks](./docs/examples/notebooks/) for interactive examples

## Support

- 📧 Email: insights@alteryx.com
- 📋 Issues: https://github.com/alteryx/metrics-system/issues
- 💬 Slack: #metrics-support
