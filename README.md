# 📊 Alteryx Metrics System

Query any metric from Alteryx products. Connect to Snowflake with SSO. Get intelligent metric resolution with composition and suggestions.

## ✨ Features

- **🔍 Smart Metric Discovery**: Search and list 186+ metrics across 7 products
- **🧠 Intelligent Composition**: System automatically builds metrics from foundations
- **💡 Smart Suggestions**: Can't find a metric? Get recommendations
- **🔐 Secure SSO**: Snowflake Single Sign-On authentication
- **📋 Audit Logging**: Complete record of who accessed what, when
- **⚡ Multiple Interfaces**: CLI, Python library, REST API (coming)
- **📚 Comprehensive Docs**: Getting started guides, examples, architecture

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone <repo-url>
cd metrics-system
pip install -r requirements.txt
pip install -e .
```

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your Snowflake account details
```

### 3. Query a Metric
```bash
# Search
metrics search --product plans --keyword "creation"

# Get data
metrics get plans.plans_creation_and_active_users

# Save to file
metrics get trial.trial_signups_total --output results.csv --format csv
```

## 📖 Documentation

- **[GETTING_STARTED.md](./GETTING_STARTED.md)** - 10-min quick start (you are here)
- **[docs/CLI_REFERENCE.md](./docs/CLI_REFERENCE.md)** - All CLI commands
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design
- **[docs/METRIC_COMPOSITION.md](./docs/METRIC_COMPOSITION.md)** - How metrics are built
- **[examples/](./examples/)** - Python & bash examples
- **[docs/examples/notebooks/](./docs/examples/notebooks/)** - Jupyter notebooks

## 🎯 What's Included

### Metrics (186 Total)
- **account_user**: 16 metrics - Version adoption, support status
- **alteryx-one**: 56 metrics - Activation, engagement, contracts
- **ask_alteryx**: 45 metrics - Usage, feedback, adoption
- **designer**: 15 metrics - Version adoption, workflow execution
- **trial**: 19 metrics - Funnel, conversion, engagement
- **version_adoption**: 21 metrics - Product version tracking
- **plans**: 14 metrics - Plans creation, runs, tasks

### Components
```
engine/               # Core metric engine
├── metric_engine.py      # Main orchestrator
├── metric_loader.py      # Load YAML definitions
├── snowflake_connector.py # Snowflake access
├── metric_composer.py    # Build from foundations
├── audit_logger.py       # Audit trail
└── error_handler.py      # Smart error messages

cli/                 # Command-line interface
├── main.py              # CLI entry point
└── commands/            # Individual commands

products/            # Metric definitions (7 products)
├── account_user/
├── alteryx-one/
├── ask_alteryx/
├── designer/
├── trial/
├── version_adoption/
└── plans/

docs/               # Documentation
examples/           # Example scripts & notebooks
tests/              # Test suite
```

## 💻 CLI Commands

```bash
# Search & Discover
metrics search --keyword "adoption"                 # Search all
metrics search --product designer --keyword "2025" # Search product
metrics list designer                               # List all in product
metrics describe trial.trial_signups_total         # Details

# Get Data
metrics get trial.trial_signups_total              # Get metric
metrics get plans.plans_creation_and_active_users \
  --output result.csv --format csv                 # Save to file

# Manage
metrics products                                    # List all products
metrics validate                                    # Validate metrics
metrics validate --product designer                # Validate product
metrics audit --user $(whoami)                     # Your audit log
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

## 📝 Examples

### Example 1: Get metric to DataFrame
```python
result = engine.get_metric('trial_signups_total')
print(f"{len(result)} rows retrieved")
result.to_csv('trial_signups.csv')
```

### Example 2: Search and export
```bash
metrics search --product plans --keyword "run" --format json > plans_metrics.json
```

### Example 3: Validate and audit
```bash
# Check all metrics work
metrics validate

# Review your recent queries
metrics audit --user dhiraj.sahu --limit 50
```

## 🔐 Security & Authentication

- **SSO Only**: Uses Snowflake's external browser authentication
- **No Passwords**: Credentials never stored locally
- **Audit Trail**: Every query logged with timestamp and user
- **Role-Based**: Respects Snowflake role permissions

## 🐛 Troubleshooting

### "Metric not found"
```bash
# Search for similar metrics
metrics search --keyword "adoption"

# List all metrics in product
metrics list designer
```

### "Snowflake connection failed"
```bash
# Re-authenticate
metrics auth --relogin
```

### "Could not compose metric"
System tried but couldn't build it from available foundations.
Contact: **insights@alteryx.com**

## 📧 Support

- **Email**: insights@alteryx.com
- **Slack**: #metrics-support
- **GitHub**: [Issues](https://github.com/alteryx/metrics-system/issues)

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Want to add metrics? See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

**Ready to query?** → [Start with Getting Started Guide](./GETTING_STARTED.md)
