# 📊 Alteryx Metrics System

**Unified metrics platform for all Alteryx products.** Query 180+ metrics across 6 products with Snowflake SSO authentication. Get data instantly via CLI, Python library, or REST API.

> **Status**: Production Ready | **Version**: 2.0+ | **Last Updated**: August 2026

## ✨ Key Features

- **🔍 Smart Metric Discovery**: Browse and search 180+ metrics across 6 products
- **⚡ Fast Queries**: Direct SQL execution with intelligent caching
- **🔐 Secure SSO**: Snowflake Single Sign-On (no passwords stored)
- **📋 Audit Trail**: Complete audit logging of all metric access
- **🐍 Multiple Interfaces**: CLI, Python library, JSON API
- **📊 Export Options**: CSV, JSON, Parquet formats
- **📚 Complete Documentation**: Getting started, API reference, examples

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the Repository
```bash
git clone https://github.com/dhirajsahu-analyst/-alteryx-ai-products.git
cd -alteryx-ai-products
```

### Step 2: Install Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
pip install -e .
```

### Step 3: Configure Snowflake Connection
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file with your details (SSO enabled by default)
# SNOWFLAKE_ACCOUNT: ALTERYX-ALTERYX_EDW
# SNOWFLAKE_WAREHOUSE: COMPUTE_WH
# SNOWFLAKE_DATABASE: DISCOVERY_PRODUCT_MANAGEMENT
# SNOWFLAKE_SCHEMA: METRIC_STORE
# USER: your_email@alteryx.com
```

### Step 4: Test Connection
```bash
# List available products
python -m cli.main products

# Search for a metric
python -m cli.main search --keyword "adoption"

# Get your first metric
python -m cli.main get ask_alteryx.copilot_active_users
```

### Step 5: Export Results
```bash
# Save to CSV
python -m cli.main get trial.trial_signups_total --output results.csv --format csv

# Get as JSON
python -m cli.main get plans.total_active_subscriptions --format json
```

## 📖 Documentation

- **[GETTING_STARTED.md](./GETTING_STARTED.md)** - 10-min quick start (you are here)
- **[docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md)** - All CLI commands
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design
- **[docs/METRIC_COMPOSITION.md](./docs/METRIC_COMPOSITION.md)** - How metrics are built
- **[examples/](./examples/)** - Python & bash examples
- **[docs/examples/notebooks/](./docs/examples/notebooks/)** - Jupyter notebooks

## 🎯 Products & Metrics

### 6 Product Lines (180+ Metrics)

| Product | Metrics | Focus Areas |
|---------|---------|------------|
| **Ask Alteryx** | 28 | Copilot usage, engagement, retention, adoption |
| **Alteryx One** | 23 | Account/user funnels, activation, retention, engagement |
| **Plans** | 16 | Subscriptions, churn, upgrades, revenue (MRR/CLV) |
| **Trial** | 14 | Signup → conversion funnel, satisfaction, pipeline revenue |
| **Version Adoption** | 16 | Version distribution, upgrade windows, health scores |
| **Account/User** | 16 | User lifecycle, role distribution, activation |

**Total Metrics**: 113+ with complete SQL queries and documentation

### Repository Structure
```
.
├── README.md                 # You are here
├── GETTING_STARTED.md       # Detailed setup guide
├── VERSION                  # Current version (2.0+)
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── .env.example             # Configuration template
│
├── cli/                      # Command-line interface
│   ├── main.py              # CLI entry point
│   └── commands/            # CLI command implementations
│
├── engine/                   # Core metrics engine
│   ├── metric_engine.py      # Main orchestrator
│   ├── metric_loader.py      # Load YAML definitions
│   ├── snowflake_connector.py # Snowflake access
│   ├── metric_composer.py    # Build computed metrics
│   ├── audit_logger.py       # Audit trail logging
│   └── error_handler.py      # Smart error handling
│
├── products/                 # Metric definitions (6 products)
│   ├── ask_alteryx/          # 28 Copilot metrics
│   │   └── metrics/
│   ├── alteryx-one/          # 23 platform metrics
│   │   └── metrics/
│   ├── plans/                # 16 subscription metrics
│   │   └── metrics/
│   ├── trial/                # 14 trial metrics
│   │   └── metrics/
│   ├── version_adoption/     # 16 version metrics
│   │   └── metrics/
│   └── account_user/         # 16 user metrics
│       └── metrics/
│
├── docs/                     # Documentation
│   ├── CLI_REFERENCE.md      # Full CLI documentation
│   ├── ARCHITECTURE.md       # System design
│   ├── QUICK_START.md        # Quick start guide
│   └── FAQ.md               # Frequently asked questions
│
├── examples/                 # Example scripts
│   ├── python/              # Python examples
│   └── bash/                # Bash script examples
│
└── .github/
    └── workflows/           # CI/CD pipelines
```

## 💻 CLI Commands Reference

### Discovery & Search
```bash
# List all available products
python -m cli.main products

# List all metrics in a product
python -m cli.main list ask_alteryx
python -m cli.main list alteryx-one
python -m cli.main list plans

# Search metrics by keyword
python -m cli.main search --keyword "adoption"
python -m cli.main search --product ask_alteryx --keyword "retention"

# Get metric details
python -m cli.main describe ask_alteryx.copilot_active_users
```

### Fetch Data
```bash
# Get metric data (prints to console)
python -m cli.main get ask_alteryx.copilot_active_users

# Export to CSV
python -m cli.main get trial.trial_signups_total --output results.csv --format csv

# Export to JSON
python -m cli.main get plans.total_active_subscriptions --format json --output subs.json

# Export to Parquet
python -m cli.main get alteryx-one.user_funnel_active --format parquet --output data.parquet
```

### System Management
```bash
# Validate all metric definitions
python -m cli.main validate

# Validate specific product
python -m cli.main validate --product alteryx-one

# View your audit log
python -m cli.main audit --user your_email@alteryx.com

# Show version and system info
python -m cli.main version
```

## 🐍 Python Library

```python
from engine.metric_engine import MetricsEngine

engine = MetricsEngine()

# Get metric
result = engine.get_metric('trial_signups_total', product='trial')

# Search
metrics = engine.search_metrics('adoption', product='designer')

# List
all_metrics = engine.list_metrics('plans')

# Details
info = engine.get_metric_info('designer_2025_adoption_rate')
```

## 🔄 How It Works

### Query Flow
```
User: metrics get trial_signups_total
         ↓
Engine: Load metric definition from YAML
         ↓
        Try direct Snowflake query
         ↓ (if fails)
        Try to compose from base metrics
         ↓ (if fails)
        Suggest alternatives
         ↓
Result: Data or helpful error message
         ↓
Audit Log: Record user action
```

### Metric Resolution
1. **Direct Query**: Execute SQL directly from metric definition
2. **Composition**: Build from base metrics using join rules
3. **Suggestions**: Recommend similar metrics
4. **Error Message**: User-friendly guidance

## 📝 Real-World Examples

### Example 1: Track Copilot Adoption
```bash
# Get active Copilot users
python -m cli.main get ask_alteryx.copilot_active_users

# Get adoption rate percentage
python -m cli.main get ask_alteryx.copilot_adoption_rate_pct

# Export retention metrics to CSV
python -m cli.main get ask_alteryx.copilot_7_15_day_retention_rate_pct \
  --output copilot_retention.csv --format csv
```

### Example 2: Analyze Trial Conversion
```bash
# Get monthly trial signups
python -m cli.main get trial.monthly_signups

# Get conversion funnel (signup → activated → engaged → converted)
python -m cli.main get trial.conversion_rate_pct

# Export revenue from converted trials
python -m cli.main get trial.monthly_closed_won_revenue --format json
```

### Example 3: Monitor Plan Health
```bash
# Check active subscriptions by tier
python -m cli.main list plans | grep "distribution"

# Get churn rate
python -m cli.main get plans.churn_rate

# Export MRR breakdown
python -m cli.main get plans.mrr_by_plan_tier_enterprise --format csv
```

### Example 4: Version Upgrade Tracking
```bash
# Latest version adoption percentage
python -m cli.main get version_adoption.latest_version_adoption_pct

# 30/60/90-day adoption windows
python -m cli.main get version_adoption.30_day_version_adoption

# Enterprise vs Professional adoption
python -m cli.main get version_adoption.enterprise_adoption_pct
```

## 🔐 Security & Authentication

- **SSO Only**: Uses Snowflake's external browser authentication
- **No Passwords**: Credentials never stored locally
- **Audit Trail**: Every query logged with timestamp and user
- **Role-Based**: Respects Snowflake role permissions

## 🐛 Troubleshooting

### Snowflake Authentication Issues

**Problem**: "Authentication failed" or browser doesn't open
```bash
# Solution 1: Clear browser cache and try again
rm ~/.snowsql/config  # Clear cached credentials

# Solution 2: Force re-login
python -m cli.main auth --force-relogin

# Solution 3: Check credentials in .env
cat .env | grep SNOWFLAKE_ACCOUNT
# Expected: ALTERYX-ALTERYX_EDW
```

**Problem**: "Role not found" error
```bash
# Verify your Snowflake role in .env
# Expected: DHIRAJ_SAHU_ROLE or your assigned role
# Contact: IT team if unsure
```

### Metric Not Found

**Problem**: "Metric 'xyz' not found"
```bash
# Search for similar metrics
python -m cli.main search --keyword "activation"

# List all metrics in a product
python -m cli.main list ask_alteryx

# Check if product exists
python -m cli.main products
```

### Data Query Issues

**Problem**: "Query timeout" or "Too much data"
```bash
# Add date filters (if metric supports them)
python -m cli.main get trial.monthly_signups --from-date 2024-01-01

# Check metric documentation for filters
python -m cli.main describe trial.monthly_signups
```

**Problem**: "No results returned"
```bash
# 1. Verify the metric exists
python -m cli.main describe plans.total_active_subscriptions

# 2. Check Snowflake has data for the metric
# Contact: insights@alteryx.com if data issue persists
```

### System Issues

**Problem**: "ModuleNotFoundError: No module named 'cli'"
```bash
# Solution: Install package in development mode
pip install -e .
```

**Problem**: "Permission denied" when accessing metrics
```bash
# Check your Snowflake role permissions
# Contact: IT team for role elevation

# Verify .env USER field
grep USER .env
```

## 📚 Documentation

- **[GETTING_STARTED.md](./GETTING_STARTED.md)** - Comprehensive setup guide with screenshots
- **[docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md)** - Complete CLI command reference
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design and components
- **[docs/FAQ.md](./docs/FAQ.md)** - Frequently asked questions
- **[examples/](./examples/)** - Example scripts and use cases

## 🆘 Getting Help

### Quick Support
| Issue | Solution |
|-------|----------|
| Can't find a metric | Run: `python -m cli.main search --keyword "your_keyword"` |
| Authentication error | See **Troubleshooting** section above |
| Need a new metric | Contact insights@alteryx.com with description |
| Data seems wrong | Verify query with DESCRIBE then contact insights team |

### Contact Information
- **Email**: insights@alteryx.com
- **Slack**: #product-insights-metrics
- **Issues**: Create an issue on GitHub

## 🚀 Contributing

### Adding New Metrics

1. **Create metric YAML file** in `products/<product>/metrics/`
   ```yaml
   id: my_metric_id
   name: My Metric Name
   description: What this metric measures
   product: product_name
   sql_template: SELECT ... FROM DISCOVERY.METRIC_STORE...
   tags: [tag1, tag2]
   ```

2. **Test the metric**
   ```bash
   python -m cli.main describe my_metric_id
   python -m cli.main get my_metric_id
   ```

3. **Submit pull request** with metric YAML and documentation

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## 📄 License

MIT License - See [LICENSE](./LICENSE) file

## 🎯 What's Next?

✅ **New to metrics?** → [GETTING_STARTED.md](./GETTING_STARTED.md)

✅ **Want to use via Python?** → [examples/python/](./examples/python/)

✅ **Need CLI command reference?** → [docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md)

✅ **Have questions?** → Check [docs/FAQ.md](./docs/FAQ.md)

---

**Last Updated**: August 2026 | **Version**: 2.0+ | **Status**: Production Ready ✅
