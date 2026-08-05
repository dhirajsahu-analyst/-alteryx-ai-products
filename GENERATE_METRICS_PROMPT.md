# Generate Metrics from Snowflake Views - Prompt Template

This guide helps you generate metrics markdown files from Snowflake `_VIEW` tables using Claude AI or similar LLM.

## Quick Start

### Step 1: Find Your View Name

First, identify the Snowflake view for your product:

```sql
-- Run this in Snowflake to find views with _VIEW suffix
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = 'DISCOVERY'
AND TABLE_SCHEMA = 'METRIC_STORE'
AND TABLE_NAME LIKE '%_VIEW'
ORDER BY TABLE_NAME;
```

Example results:
- `COPILOT_USERS_ACTIVITY_FUNNEL_VIEW`
- `COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW`
- `ALTERYX_ONE_ACTIVATION_FUNNEL_VIEW`
- `TRIAL_FUNNEL_TRACKING_VIEW`
- `VERSION_ADOPTION_TRACKING_VIEW`
- `LIVE_QUERY_METRICS_VIEW`

### Step 2: Get View Schema

```sql
-- Run this in Snowflake to see all columns
DESC DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.<YOUR_VIEW_NAME>;
```

### Step 3: Use Prompt with Claude or LLM

Copy the appropriate prompt below and fill in your details:

---

## Prompt Template (Copy & Use)

### For Ask Alteryx / Copilot Metrics

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Ask Alteryx (Copilot)
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW

VIEW SCHEMA:
[PASTE THE COLUMNS HERE FROM DESC OUTPUT]

REQUIREMENTS:
1. Create a markdown table with these columns: Product | Metric Name | Description | SQL Query | Tags
2. Each metric should have:
   - Clear, descriptive name
   - Business definition (what it measures)
   - Complete SQL query in ```sql code blocks
   - Relevant tags (copilot, engagement, funnel, users, active, etc.)
3. Extract metrics from the view structure (look at column names to infer metrics)
4. Follow the naming convention: product_dimension_measure
5. Include retention metrics (7-15 day, 30-60 day windows if applicable)
6. Include funnel stage metrics (onboarded → active → with_workflow → engaged)
7. Include adoption and rate metrics (percentages as _pct suffix)

OUTPUT FORMAT:
# Ask Alteryx Metrics

## Overview
[Brief description of what metrics track]

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Ask Alteryx | [Metric Name] | [Description] | ```sql [COMPLETE SQL QUERY] ``` | tag1, tag2, tag3 |

---

## Notes
[Add any important notes about filters, calculations, or assumptions]
```

---

### For Alteryx One Metrics

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Alteryx One
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_ONE_ACTIVATION_FUNNEL_VIEW

VIEW SCHEMA:
[PASTE THE COLUMNS HERE FROM DESC OUTPUT]

REQUIREMENTS:
1. Create a markdown table with columns: Product | Metric Name | Description | SQL Query | Tags
2. Each metric should have:
   - Clear, descriptive name
   - Business definition
   - Complete SQL query in ```sql code blocks
   - Relevant tags (alteryx-one, funnel, accounts, users, engagement, activation, etc.)
3. Extract metrics from view columns
4. Include account funnel metrics (prospect → onboarded → activated → active → engaged)
5. Include user funnel metrics (registered → active → engaged)
6. Include role-based activation (full users, basic users, viewers, account admins)
7. Include retention windows (7d, 1-7d, 7-14d, 14-30d, 30-60d)
8. Include engagement and health metrics

OUTPUT FORMAT:
# Alteryx One Metrics

## Overview
[Description of metrics]

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Alteryx One | [Metric Name] | [Description] | ```sql [COMPLETE SQL QUERY] ``` | tag1, tag2, tag3 |

---

## Notes
[Important notes about calculations and filters]
```

---

### For Plans / Subscriptions Metrics

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Plans
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.SUBSCRIPTIONS_PLAN_TRACKING

VIEW SCHEMA:
[PASTE THE COLUMNS HERE FROM DESC OUTPUT]

REQUIREMENTS:
1. Create markdown table: Product | Metric Name | Description | SQL Query | Tags
2. Include:
   - Plan distribution metrics (Enterprise, Professional, Standard)
   - Subscription lifecycle (active, expired, cancelled)
   - Rate metrics (upgrade rate, churn rate, renewal rate)
   - Revenue metrics (MRR, CLV by tier)
   - Feature adoption (workflows, deployments, automations)
3. SQL queries should filter on STATUS = 'ACTIVE' where appropriate
4. Use tags: plans, distribution, churn, revenue, mrr, clv, upgrade, renewal, engagement

OUTPUT FORMAT:
# Plans Metrics

## Overview
[Description]

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Plans | [Metric Name] | [Description] | ```sql [COMPLETE SQL QUERY] ``` | tag1, tag2, tag3 |

---

## Notes
[Important notes about status filters, calculations, percentage rounding]
```

---

### For Trial Metrics

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Trial
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.TRIAL_FUNNEL_TRACKING

VIEW SCHEMA:
[PASTE THE COLUMNS HERE FROM DESC OUTPUT]

REQUIREMENTS:
1. Create markdown table: Product | Metric Name | Description | SQL Query | Tags
2. Include complete trial funnel:
   - Signup metrics (monthly, total)
   - Activation (first login)
   - Engagement (5+ logins OR workflow creation)
   - Conversion (to paid)
   - Revenue metrics (MRR, ARR, pipeline, closed-won)
3. Include quality metrics (response quality, solution usefulness)
4. Include churn and retention metrics
5. Tags: trial, funnel, signups, activation, conversion, revenue, quality

OUTPUT FORMAT:
# Trial Metrics

## Overview
[Description of trial funnel metrics]

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Trial | [Metric Name] | [Description] | ```sql [COMPLETE SQL QUERY] ``` | tag1, tag2, tag3 |

---

## Notes
[Important notes about engagement thresholds, revenue types, calculations]
```

---

### For Version Adoption Metrics

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Version Adoption
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.VERSION_ADOPTION_TRACKING

VIEW SCHEMA:
[PASTE THE COLUMNS HERE FROM DESC OUTPUT]

REQUIREMENTS:
1. Create markdown table: Product | Metric Name | Description | SQL Query | Tags
2. Include:
   - Version distribution (2025.2, 2025.1, 2024.x, legacy)
   - Latest version adoption (count and percentage)
   - Adoption windows (30-day, 60-day, 90-day from release)
   - Health scores by version
   - End-of-support user tracking
   - Enterprise vs Professional adoption rates
   - Average days to upgrade
3. Tags: version-adoption, adoption, distribution, health, support, enterprise, professional

OUTPUT FORMAT:
# Version Adoption Metrics

## Overview
[Description of version metrics]

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Version Adoption | [Metric Name] | [Description] | ```sql [COMPLETE SQL QUERY] ``` | tag1, tag2, tag3 |

---

## Notes
[Important notes about version filtering, health calculations, support dates]
```

---

### For Live Query Metrics

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Live Query
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.LIVE_QUERY_[YOUR_VIEW_NAME]

VIEW SCHEMA:
[PASTE THE COLUMNS HERE FROM DESC OUTPUT]

REQUIREMENTS:
1. Create markdown table: Product | Metric Name | Description | SQL Query | Tags
2. Include all available metrics from the view
3. Each metric should have:
   - Clear name describing what it measures
   - Business definition
   - Complete SQL query in code blocks
   - Relevant tags
4. Extract metrics from column structure
5. Include engagement, performance, and usage metrics

OUTPUT FORMAT:
# Live Query Metrics

## Overview
[Description of Live Query metrics and what they track]

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Live Query | [Metric Name] | [Description] | ```sql [COMPLETE SQL QUERY] ``` | tag1, tag2, tag3 |

---

## Notes
[Important notes about calculations and data sources]
```

---

## How to Use

### Via Claude Code / Claude AI

1. **Go to**: https://claude.ai/code (or use Claude Code CLI)

2. **Copy the prompt** above for your product

3. **Fill in the placeholders**:
   - Replace `[YOUR_VIEW_NAME]` with actual Snowflake view name
   - Replace `[PASTE THE COLUMNS HERE...]` with output from DESC command

4. **Submit the prompt**

5. **Claude will generate** the complete metrics markdown file

6. **Save the output** as `{product_name}.metrics.md`

### Via Command Line

```bash
# Using Claude Code CLI
claude --prompt "$(cat prompt.txt)" > product.metrics.md
```

### Output Example

```markdown
# Ask Alteryx Metrics

## Overview
Ask Alteryx (Copilot) metrics track user and account engagement...

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Ask Alteryx | Copilot Active Users | Number of users with at least one Copilot chat activity | ```sql SELECT COUNT(DISTINCT USER_ID_RAW) AS ACTIVE_USERS FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_FUNNEL_VIEW WHERE CHAT_ID IS NOT NULL``` | copilot, engagement, funnel, users, active |
| Ask Alteryx | Copilot 7-15 Day Retention Rate % | Percentage of users who returned... | ```sql WITH user_activity AS (SELECT...) ``` | copilot, retention, cohort-analysis |
```

---

## Tips for Best Results

### 1. Use Complete View Names
```
✅ DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW
❌ COPILOT_USERS_ACTIVITY_FUNNEL_VIEW
```

### 2. Include Full Schema Output
```bash
# Good: Include full DESC output
DESC DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.YOUR_VIEW_NAME;
# Then copy all column output
```

### 3. Specify SQL Requirements
- Complete FROM and WHERE clauses
- No hardcoded dates (use DATEADD, CURRENT_DATE)
- Use proper Snowflake functions
- Include CAST for type conversions

### 4. Add Metric Details
- Include both business and technical definitions
- Add relevant tags for discovery
- Specify any filters or conditions
- Document assumptions

---

## SQL Query Standards

All generated SQL queries should follow these standards:

✅ **DO:**
- Use full schema paths: `DISCOVERY.METRIC_STORE.TABLE_NAME`
- Filter on `LICENSE_TYPE = 'Purchase'` for customer data
- Use `COUNT(DISTINCT ...)` for unique counts
- Round percentages to 4 decimals: `ROUND(pct / 100, 4)`
- Test in Snowflake first
- Document complex logic

❌ **DON'T:**
- Hardcode dates
- Use `SELECT *`
- Mix time zones without conversion
- Assume column existence
- Leave queries without comments

---

## Example: Complete Workflow

### Step 1: Get View Info
```sql
-- Run in Snowflake
DESC DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW;
```

Output:
```
| name                    | type    | kind    | null? | default | primary key | unique key | check | expression | comment | policy name |
|-------------------------|---------|---------|-------|---------|-------------|------------|-------|-----------|---------|-------------|
| USER_ID_RAW             | VARCHAR | COLUMN  | Y     | NULL    | N           | N          |       |           |         |             |
| CONVERSATION_ID         | VARCHAR | COLUMN  | Y     | NULL    | N           | N          |       |           |         |             |
| CHAT_ID                 | VARCHAR | COLUMN  | Y     | NULL    | N           | N          |       |           |         |             |
| CREATED_DATE            | DATE    | COLUMN  | Y     | NULL    | N           | N          |       |           |         |             |
...
```

### Step 2: Copy the Appropriate Prompt

For Ask Alteryx, copy the "For Ask Alteryx / Copilot Metrics" prompt above.

### Step 3: Fill in Details

```
You are a metrics expert. I need you to generate a metrics markdown file from a Snowflake view.

PRODUCT: Ask Alteryx (Copilot)
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW

VIEW SCHEMA:
USER_ID_RAW: VARCHAR
CONVERSATION_ID: VARCHAR
CHAT_ID: VARCHAR
CREATED_DATE: DATE
LICENSE_TYPE: VARCHAR
USER_TYPE: VARCHAR
ACCOUNT_EDITION: VARCHAR
...

REQUIREMENTS:
[Copy all requirements from template above]

OUTPUT FORMAT:
[Copy format template]
```

### Step 4: Submit to Claude

Paste into https://claude.ai/ or Claude Code and submit.

### Step 5: Save Output

Save Claude's markdown output as `ask_alteryx.metrics.md`

### Step 6: Add to ZIP (Optional)

If building ChatGPT agent skill:
```bash
zip metrics_skill.zip ask_alteryx.metrics.md alteryx_one.metrics.md ...
```

---

## Support

- **Questions about prompts?** → insights@alteryx.com
- **Need view names?** → Check Snowflake INFORMATION_SCHEMA
- **Template issues?** → See CONTRIBUTING.md

---

**Ready to generate?** Pick your product and follow the steps above! 🚀
