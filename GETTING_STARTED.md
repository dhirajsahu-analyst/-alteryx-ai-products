# 🚀 Getting Started with TelemetryIQ Semantic Intelligence Platform

Complete step-by-step guide to install, configure, and use the modern, Git-native, and governed TelemetryIQ semantic telemetry platform.

---

## 1. Prerequisites & Terminal Environment Setup

If you or your team members run into a `pip: command not found` error, it means Python and its package manager are either not installed or not exposed in your system's `PATH`. Follow these setup steps:

### For macOS
macOS comes with Python 3 out of the box, but `pip3` may not be symlinked to `pip`:
```bash
# Install or update Command Line Tools (includes python3 and pip3)
xcode-select --install

# Add symlinks so you can type "python" and "pip" directly
echo "alias python=python3" >> ~/.zshrc
echo "alias pip=pip3" >> ~/.zshrc
source ~/.zshrc

# Verify they are available
python --version
pip --version
```

### For Ubuntu / Linux
```bash
# Update package registry
sudo apt update

# Install Python 3, Pip, and virtual environment utilities
sudo apt install -y python3 python3-pip python3-venv

# Verify
python3 --version
pip3 --version
```

### For Windows (PowerShell)
```powershell
# Install Python using winget (the Windows Package Manager)
winget install Python.Python.3.9

# Restart your terminal and verify
python --version
pip --version
```

---

## 2. Install LLM CLI Ecosystem (Pro / Enterprise Accounts)
If you have Pro or Enterprise accounts, you do not need API keys for CLI usage. Simply run the standard commands to install your preferred AI agent CLIs:

### Install Gemini CLI
```bash
npm install -g @google/gemini-cli
```

### Install Claude CLI
```bash
npm install -g @anthropic/claude-cli
```

### Install GitHub Copilot / Codex CLI
```bash
# Install the GitHub CLI first, then install the copilot extension
gh extension install github/gh-copilot
```

---

## 3. Clone and Install TelemetryIQ

```bash
# 1. Clone the repository
git clone https://github.com/dhirajsahu-analyst/-alteryx-ai-products.git
cd -alteryx-ai-products

# 2. Install required telemetry, database, and schema packages
pip3 install -r requirements.txt

# 3. Install alteryx-metrics as an editable local package
pip3 install -e .
```

---

## 4. Configure Snowflake Connectivity
Create a `.env` file in the repository root directory:

```bash
cat << 'EOF' > .env
SNOWFLAKE_ACCOUNT=ALTERYX-ALTERYX_EDW
SNOWFLAKE_USER=YOUR_EMAIL@ALTERYX.COM
SNOWFLAKE_WAREHOUSE=ANALYTICS_WH
SNOWFLAKE_DATABASE=DISCOVERY_PRODUCT_MANAGEMENT
SNOWFLAKE_SCHEMA=METRIC_STORE
USER=YOUR_EMAIL@ALTERYX.COM
SNOWFLAKE_ROLE=DHIRAJ_SAHU_ROLE
EOF
```

*Note: Since TelemetryIQ uses secure SSO Authentication (`externalbrowser`), no password needs to be stored in this file.*

---

## 5. Compile the Local Semantic Catalog
Build and compile the telemetry catalog. This scans all product manifests, metric contracts, and relationships, validates them against strict JSON schemas, and compiles them into a local SQLite database (`.telemetryiq/catalog.db`):

```bash
metrics build
```

---

## 6. Core Usage & Diagnostics Commands

### Audit Workspace Readiness
Audits your configurations, metadata coverage, and Snowflake query boundaries, outputting an executive scorecard:
```bash
metrics doctor
```

### Search for Metrics
Uses our high-speed, relational, relevance-ranked search engine to find matching metrics:
```bash
metrics search engagement
```

### Trace Upstream Lineage
Traces exactly which raw models and Snowflake tables feed into a specific metric:
```bash
metrics lineage plans_engagement_rate
```

### Trace Downstream Impact
Simulates modifying a table and shows all affected metrics and semantic relationships:
```bash
metrics impact PLANS_MONTHLY_ACCOUNT_AT
```

### Fetch Metric Data from Snowflake
Connects to Snowflake via SSO and retrieves actual compiled dataframe numbers:
```bash
metrics get plans_funnel_active
```
