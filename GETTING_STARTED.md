# 🚀 TelemetryIQ Getting Started & User Playbook

Welcome to **TelemetryIQ**, an enterprise-grade, Git-native semantic intelligence platform. TelemetryIQ acts as the governed semantic layer between your natural-language questions and Snowflake telemetry data, ensuring that every answer is **accurate, governed, traceable, and explainable**.

This comprehensive playbook is designed for three distinct roles:
1. 📊 **Business Users & Analysts** who want to search, discover, and fetch metric values.
2. 🧪 **Metric Owners & Creators** who define, validate, and register new metric contracts.
3. ⚙️ **Platform Engineers & Admins** who manage compiler builds, safety guardrails, and schema compliance.

---

## 🧭 Persona Roadmap: Where to Start?

* **Just want to retrieve data?** Skip straight to **[Section 3: The Analyst Playbook](#3-the-analyst--business-user-playbook)**.
* **Stuck on installation or `pip` errors?** Go to **[Section 2: Zero-to-One Installation Guide](#2-zero-to-one-installation-guide)**.
* **Want to add a new metric to the platform?** Go to **[Section 4: The Metric Creator's Tutorial](#4-the-metric-creators-tutorial)**.

---

## 2. Zero-to-One Installation Guide

This section helps you set up Python, resolve common terminal path errors, install the CLI, and connect to Snowflake.

### Step 2.1: Fix "pip command not found" or "python not found"
If you type `pip` or `python` and receive an error, select your operating system below to configure your terminal PATH.

####  macOS Setup
macOS comes with Python 3, but `pip3` may not be symlinked as `pip`. Run these commands:
```bash
# 1. Install macOS Command Line Tools (includes python3 and pip3)
xcode-select --install

# 2. Add standard symlinks to your shell profile
echo "alias python=python3" >> ~/.zshrc
echo "alias pip=pip3" >> ~/.zshrc
source ~/.zshrc

# 3. Verify
python --version
pip --version
```

#### 🐧 Ubuntu / Debian Linux Setup
```bash
# 1. Update system package index
sudo apt update

# 2. Install Python 3, Pip, and Virtual Environment utilities
sudo apt install -y python3 python3-pip python3-venv

# 3. Verify
python3 --version
pip3 --version
```

#### ⊞ Windows Setup (PowerShell)
```powershell
# 1. Install Python using winget (Windows Package Manager)
winget install Python.Python.3.9

# 2. Restart PowerShell and verify
python --version
pip --version
```

---

### Step 2.2: Clone and Install TelemetryIQ
Run these commands in your terminal:
```bash
# 1. Clone the platform repository
git clone https://github.com/dhirajsahu-analyst/-alteryx-ai-products.git
cd -alteryx-ai-products

# 2. Create a virtual environment (highly recommended to avoid library conflicts)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install required libraries
pip install -r requirements.txt

# 4. Install the CLI in editable development mode
pip install -e .
```

---

### Step 2.3: Configure Snowflake Connectivity
Create a `.env` file in the project's root folder:
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
*Note: Since TelemetryIQ uses secure Single Sign-On (SSO) authentication, **no password** is written into this configuration file.*

---

### Step 2.4: Compile the Local Catalog
This command compiles the entire repository, validates all manifests, and caches them into a lightning-fast SQLite local database:
```bash
metrics build
```

---

## 3. The Analyst & Business User Playbook

This section is for analysts, product leaders, and business stakeholders who want to discover, trace, and extract metrics data.

### Command 3.1: List Available Products
Lists all active product domains registered in the platform and shows how many metrics are available for each:
```bash
metrics products
```
**Expected Output:**
```text
                 Available Products                  
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
┃ Product          ┃ Name        ┃ Metrics ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
│ alteryx_one      │ Alteryx One │ 28      │ active │
│ plans            │ plans       │ 17      │ active │
│ trial            │ trial       │ 21      │ active │
└──────────────────┴─────────────┴─────────┴━━━━━━━━┘
```

### Command 3.2: List Metrics for a Specific Product
Lists all compiled metrics registered under a product domain (e.g. `plans`):
```bash
metrics list plans
```

### Command 3.3: Search for Metrics by Keyword
TelemetryIQ features an **indexed relational search engine** that ranks results based on match quality (exact ID matches are prioritized over name or description substring matches):
```bash
metrics search engagement
```

### Command 3.4: Trace Metric Lineage (Traceability)
Shows which raw Snowflake tables, models, and base metrics contribute to a specific metric's values:
```bash
metrics lineage plans_engagement_rate
```
**Expected Output:**
```text
Upstream Lineage Map:
  Asset ID:   plans_engagement_rate
  Name:       Plans Engagement Rate
  Product:    plans
  Asset Type: metric

Direct Source Tables/Models:
  • PLANS_FACT_AT
```

### Command 3.5: Query Metric Data from Snowflake
Connects to Snowflake via your secure SSO role, validates the SQL against safety rules, compiles it, and returns the actual results:
```bash
metrics get plans_funnel_active
```
*(This command will trigger your default browser to complete Alteryx SSO authentication if your session has expired).*

---

## 4. The Metric Creator's Tutorial

This section walks metric owners, analytical engineers, and data developers through creating, validating, testing, and registering a new metric contract.

### Step 4.1: Write the Metric Contract
Every production metric in TelemetryIQ is governed by a machine-readable YAML contract. Under your product's metric folder (e.g., `products/plans/metrics/`), create a new file named `plans_my_new_metric.yaml`:

```yaml
id: plans_my_new_metric
name: Plans - Core Adoption - My New Metric
description: Total active plans showing consistent task utilization.
product: plans
category: adoption
status: active
grain: daily
definition:
  business: Traces active automated plans with at least one current task.
  technical: Count of distinct PLAN_ID where CURRENT_TASK_COUNT > 0
source: PLANS_FACT_AT
sql_template: >
  SELECT 
      PLAN_CREATED_AT::DATE AS CREATION_DATE,
      COUNT(DISTINCT PLAN_ID) AS ACTIVE_PLANS_COUNT
  FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.PLANS_FACT_AT
  WHERE CURRENT_TASK_COUNT > 0
  GROUP BY 1
  ORDER BY 1 DESC
tags:
  - plans
  - adoption
maintainer: your_email@alteryx.com
last_updated: '2026-08-05'
version: '1.0'
```

### Step 4.2: Build the Catalog & Run Schema-Validation
Compile your new contract into the local SQLite database. The compiler will automatically validate your YAML file against `schemas/metric.schema.json`:
```bash
metrics build
```
*If you made a typo (such as setting an invalid status enum or an unquoted float version), the compiler will immediately print a clear schema warning to your terminal to help you fix it.*

### Step 4.3: Audit with TelemetryIQ Doctor
Ensure your new metric complies with all production security, ownership, and credit-safety guidelines:
```bash
metrics doctor
```
*If your `sql_template` does not contain time-range bounds (like `DATEADD` or `BETWEEN`) or row limits, the doctor will flag a **CRITICAL RISK** to warn you against potentially executing unbounded, expensive queries on Snowflake.*

---

## 5. Cross-Product Joins & Relationship Mapping

TelemetryIQ uses a **Semantic Graph** to govern and safeguard table joins. The query planner will **never** invent or perform a many-to-many join; joins are permitted only through explicit relationship contracts.

### Step 5.1: Create a Relationship Contract
To join two models/tables (e.g. `PLANS_MONTHLY_ACCOUNT_AT` and `ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT`), register their link inside `shared/relationships/`:

Create `shared/relationships/my_new_relationship.yaml`:
```yaml
relationship_id: plans_to_alteryx_one_billing_account
left_model: PLANS_MONTHLY_ACCOUNT_AT
right_model: ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT
left_keys:
  - BILLING_ACCOUNT_ID
right_keys:
  - BILLING_ACCOUNT_ID
cardinality: one_to_one
approved_join_type: inner
relationship_direction: bi_directional
effective_date_logic: JOIN on LEFT.YEAR_MONTH = RIGHT.YEAR_MONTH
null_behavior: drop
required_pre_aggregation: false
supported_grains:
  - monthly
supported_dimensions:
  - BILLING_ACCOUNT_ID
supported_metrics:
  - plans_funnel_active
  - alteryx_one_monthly_active_users
known_duplication_risks: None
certification: certified
owner: product_governance@alteryx.com
validation_tests: []
```

### Step 5.2: Test Downstream Impact of Model Changes
If you modify a table schema, you can verify which relationships and metrics are impacted by running:
```bash
metrics impact PLANS_MONTHLY_ACCOUNT_AT
```

---

## 6. Troubleshooting & Common Error Solutions

| Symptom / Error | Root Cause | Direct Resolution |
| :--- | :--- | :--- |
| **`metrics: command not found`** | Package is not installed locally in your shell environment. | Run `pip install -e .` inside your repository directory. If using a virtual environment, ensure it is active. |
| **`SQL validation failed: Disallowed mutational/DDL keyword detected...`** | You (or a metric contract) attempted to run an query containing write operations (`DROP`, `INSERT`, `UPDATE`, `ALTER`, etc.). | TelemetryIQ is **strictly read-only**. Ensure your `sql_template` consists only of analytical `SELECT` or `WITH` queries. |
| **`SQL failed compilation: Object 'XYZ' does not exist or not authorized`** | Snowflake was unable to compile the query because either the table doesn't exist, or your active role lacks permissions. | Ensure you are connected with the correct role (`DHIRAJ_SAHU_ROLE`) and that the table name is correct. Search matching tables using: <br>`python3 -c "import os; from engine.snowflake_connector import get_snowflake_connector; conn=get_snowflake_connector(); conn.connect(); print(conn.execute_query(\"SHOW TABLES LIKE '%XYZ%'\"))"` |
| **`[AUTH_ERROR] Not connected to Snowflake`** | The metrics engine tried to fetch data before connecting to Snowflake. | Double-check your credentials in your `.env` file and verify your internet connection. |
| **`TypeError: ... is not of type 'string'`** | YAML parser interpreted a value (such as `version: 1.0`) as a float/number instead of a string. | Quote the value in your YAML file, changing it to `version: '1.0'`. Run `metrics build` to re-verify. |
