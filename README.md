# 📊 TelemetryIQ Semantic Intelligence Platform

### *The Governed Semantic Layer between Business Questions and Snowflake Telemetry*

TelemetryIQ is a Git-native, enterprise-grade semantic intelligence platform designed for Alteryx. It acts as a secure, traceable, and explainable interface, allowing business users, product leaders, and analysts to ask natural-language questions about product telemetry and receive governed, accurate answers directly from Snowflake.

---

## 🎯 Status & Badges

![Production Status](https://img.shields.io/badge/Status-Production--Ready-green?style=for-the-badge)
![Platform Engine](https://img.shields.io/badge/Engine-SQLite%20+%20Snowflake-blue?style=for-the-badge)
![Validation Tests](https://img.shields.io/badge/Tests-26%20Passed%20(100%25)-brightgreen?style=for-the-badge)
![Security Guardrails](https://img.shields.io/badge/Security-Enforced%20(Read--Only)-red?style=for-the-badge)
![Codeowner Status](https://img.shields.io/badge/Governance-Certified%20Assets-blueviolet?style=for-the-badge)

---

## ✨ Key Platform Capabilities

* **🔍 Relational Metric Discovery:** Blazing-fast local searching of **146 active metric contracts** across 7 product domains without real-time file-system overhead.
* **🛡️ Hard SQL Safety & Guardrails:** Zero-trust read-only SQL validation, EXPLAIN compilation checks on Snowflake, 30-second statement timeouts, and 10,000 row limits.
* **🔗 Semantic Graph Joins:** Join governance preventing accidental many-to-many Cartesian explosions, restricting cross-product analysis only to certified relationship contracts.
* **🌳 Multi-Tier Lineage:** Traceability showing exactly which raw Snowflake tables contribute to a metric, and tracing downstream impacts before table schema changes are deployed.
* **🧪 Self-Testing & Diagnostic Auditing:** High-fidelity test suites and a **745-point `metrics doctor` execution** reporting comprehensive readiness scorecards.

---

## 🏗️ Six-Layer Architecture

TelemetryIQ is architected around clean interfaces across six distinct, modular layers:

```text
  ┌────────────────────────────────────────────────────────────────────────┐
  │                           1. EXPERIENCE LAYER                          │
  │              CLI (metrics)  •  Audits  •  Diagnostics  •  UX           │
  └───────────────────────────────────────────────────┬────────────────────┘
                                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                          2. INTELLIGENCE LAYER                         │
  │     Query Planning  •  Relevance Ranking  •  FTS Retrieval  •  RCA     │
  └───────────────────────────────────────────────────┬────────────────────┘
                                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                      3. SEMANTIC GOVERNANCE LAYER                      │
  │        Metric Contracts  •  Entities  •  Grains  •  Relationships      │
  └───────────────────────────────────────────────────┬────────────────────┘
                                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                         4. DATA EXECUTION LAYER                        │
  │     SQL Validation  •  EXPLAIN Pre-Checks  •  Snowflake connection     │
  └───────────────────────────────────────────────────┬────────────────────┘
                                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                      5. TRUST & OBSERVABILITY LAYER                    │
  │        Audit Ledgers  •  Lineage Graph  •  Data Quality  •  FAQ        │
  └───────────────────────────────────────────────────┬────────────────────┘
                                                      ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                       6. PLATFORM ENGINEERING LAYER                    │
  │      Catalog Compiler  •  SQLite Cache  •  JSON Schemas  •  Tests      │
  └────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 2-Minute Quick Start

Get TelemetryIQ up and running on your terminal instantly:

### Step 1: Clone the Platform Repository
```bash
git clone https://github.com/dhirajsahu-analyst/-alteryx-ai-products.git
cd -alteryx-ai-products
```

### Step 2: Set up and Install Dependencies
```bash
# Create and activate virtual environment (highly recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
pip install -e .
```
*(If you run into `pip: command not found`, consult our OS-specific setup in **[GETTING_STARTED.md](./GETTING_STARTED.md)**).*

### Step 3: Configure Snowflake Connection
Create a `.env` file in the root folder of the repository:
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

### Step 4: Compile the Local Catalog
Scan, validate, and compile all product, metric, and relationship contracts into SQLite:
```bash
metrics build
```

---

## 📊 Interactive Playbook Examples

### 1. Audit Workspace Readiness (`metrics doctor`)
Executes a 745-point health check across metadata completeness and Snowflake credit safety:
```bash
metrics doctor
```

### 2. Search for Metrics (`metrics search`)
Uses our indexed, weighted relational search engine to find and rank relevant metrics:
```bash
metrics search engagement
```

### 3. Trace Traced Lineage (`metrics lineage`)
Inspects a metric contract and traces upstream contributors and raw source tables:
```bash
metrics lineage plans_engagement_rate
```

### 4. Trace Downstream Impact (`metrics impact`)
Analyzes which metrics and relationships are impacted before modifying a database table:
```bash
metrics impact PLANS_MONTHLY_ACCOUNT_AT
```

### 5. Query Metric Data from Snowflake (`metrics get`)
Fetches governed, cached pandas dataframe results from Snowflake via secure SSO:
```bash
metrics get plans_funnel_active
```

---

## 🛡️ Trust & Governance Model

To preserve analytical integrity and secure Snowflake resources, TelemetryIQ enforces a strict, zero-trust security paradigm:

1. **Read-Only Verification:** All queries are parsed to verify they do not contain mutational commands (`INSERT`, `UPDATE`, `DELETE`, `DROP`, etc.). Any attempt immediately throws a security violation.
2. **Pre-execution Compilation (EXPLAIN):** Standard SQL statements execute an `EXPLAIN` on Snowflake first, testing syntax on the server without consuming warehouse credits.
3. **Session Guards:** Queries are bounded by a hard **30-second timeout** and result dataframes are limited to **10,000 rows** to safeguard memory.
4. **Strict Join Verification:** The query engine rejects joins between tables unless there is a certified relationship contract mapped in the Semantic Graph, protecting against Cartesian explosions.

---

## 🤝 Contribution Workflow

We welcome contributions from Alteryx engineers, metric owners, and analysts:

```text
  1. Author YAML Contract (under products/<product>/metrics/)
  2. Validate against JSON schema locally using 'metrics build'
  3. Verify SQL and parameters using 'metrics doctor'
  4. Submit a Pull Request (PR) -> runs automated tests in CI
  5. Merge to main -> triggers automated catalog recompilation
```

For more details on authoring, troubleshooting, and persona playbooks, read our comprehensive **[GETTING_STARTED.md Guide](./GETTING_STARTED.md)**!
