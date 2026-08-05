# Quick Prompt Template - Copy & Paste

Use this to generate metrics markdown files from Snowflake `_VIEW` tables.

---

## STEP 1: Find Your View Name

Run in Snowflake:
```sql
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_CATALOG = 'DISCOVERY'
AND TABLE_SCHEMA = 'METRIC_STORE'
AND TABLE_NAME LIKE '%_VIEW'
ORDER BY TABLE_NAME;
```

Example views:
- `COPILOT_USERS_ACTIVITY_FUNNEL_VIEW`
- `COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW`
- `ALTERYX_ONE_ACTIVATION_FUNNEL_VIEW`
- `TRIAL_FUNNEL_TRACKING_VIEW`
- `VERSION_ADOPTION_TRACKING_VIEW`
- `LIVE_QUERY_METRICS_VIEW`

---

## STEP 2: Get View Columns

Run in Snowflake:
```sql
DESC DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.<YOUR_VIEW_NAME>;
```

Copy all the column names and types.

---

## STEP 3: Copy-Paste This Prompt to Claude

Replace `[YOUR_PRODUCT]`, `[YOUR_VIEW]`, and `[COLUMNS]` with your values:

```
Generate a metrics markdown file for my Snowflake view.

PRODUCT: [YOUR_PRODUCT]
Example: Ask Alteryx, Alteryx One, Plans, Trial, Version Adoption, Live Query

VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.[YOUR_VIEW]
Example: COPILOT_USERS_ACTIVITY_FUNNEL_VIEW

VIEW COLUMNS:
[PASTE COLUMNS FROM DESC OUTPUT]

CREATE A MARKDOWN FILE WITH:

# [YOUR_PRODUCT] Metrics

## Overview
Brief description of what these metrics measure.

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| [Product] | [Clear metric name] | [What it measures] | ```sql [COMPLETE SQL QUERY FROM VIEW] ``` | [relevant tags] |

TABLE REQUIREMENTS:
- Generate 10-20 metrics from the view
- Each metric gets a complete SQL query in ```sql``` code block
- Include funnel/stage metrics if applicable (onboarded → active → engaged)
- Include retention metrics if applicable (7-day, 30-day, 60-day)
- Include rate metrics (percentages with _pct suffix)
- Include adoption metrics
- Use proper naming: product_dimension_measure
- Add relevant tags separated by commas

## Notes
Important notes about calculations, filters, or assumptions.

IMPORTANT:
- SQL queries must be COMPLETE and executable
- Use DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE prefix for all views
- Filter on LICENSE_TYPE = 'Purchase' where applicable
- Round percentages to 4 decimal places
- Use proper Snowflake date functions (no hardcoded dates)
```

---

## STEP 4: Submit

1. Go to https://claude.ai/code or https://claude.ai
2. Paste the prompt above with your values filled in
3. Submit
4. Copy the markdown output
5. Save as `[product_name].metrics.md`

---

## QUICK EXAMPLES

### Example 1: Ask Alteryx

```
PRODUCT: Ask Alteryx
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW

VIEW COLUMNS:
USER_ID_RAW: VARCHAR
CONVERSATION_ID: VARCHAR
CHAT_ID: VARCHAR
CREATED_DATE: DATE
LICENSE_TYPE: VARCHAR
ACCOUNT_EDITION: VARCHAR
...

[Include all columns from DESC output]
```

### Example 2: Plans

```
PRODUCT: Plans
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.SUBSCRIPTIONS_PLAN_TRACKING

VIEW COLUMNS:
SUBSCRIPTION_ID: VARCHAR
ACCOUNT_ID: VARCHAR
PLAN_TIER: VARCHAR
STATUS: VARCHAR
MONTHLY_RECURRING_REVENUE: NUMBER
...

[Include all columns from DESC output]
```

### Example 3: Trial

```
PRODUCT: Trial
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.TRIAL_FUNNEL_TRACKING

VIEW COLUMNS:
TRIAL_ACCOUNT_ID: VARCHAR
SIGNUP_DATE: DATE
ACTIVATED: BOOLEAN
ACTIVATED_DATE: DATE
ENGAGED: BOOLEAN
LOGIN_COUNT: NUMBER
...

[Include all columns from DESC output]
```

### Example 4: Live Query

```
PRODUCT: Live Query
VIEW NAME: DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.LIVE_QUERY_METRICS_VIEW

VIEW COLUMNS:
QUERY_ID: VARCHAR
USER_ID: VARCHAR
EXECUTION_TIME: FLOAT
STATUS: VARCHAR
ROWS_RETURNED: NUMBER
...

[Include all columns from DESC output]
```

---

## OUTPUT WILL LOOK LIKE:

```markdown
# Ask Alteryx Metrics

## Overview
Ask Alteryx (Copilot) metrics track user and account engagement across the Copilot platform...

---

## Metrics Reference

| Product | Metric Name | Description | SQL Query | Tags |
|---------|-------------|-------------|-----------|------|
| Ask Alteryx | Copilot Active Users | Number of users with at least one Copilot chat activity | ```sql SELECT COUNT(DISTINCT USER_ID_RAW) AS ACTIVE_USERS FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_USERS_ACTIVITY_FUNNEL_VIEW WHERE LICENSE_TYPE = 'Purchase' AND CHAT_ID IS NOT NULL ``` | copilot, engagement, users, active |
| Ask Alteryx | Copilot 7-15 Day Retention Rate | Percentage of users who returned within 7-15 days | ```sql WITH first_use AS (...) ... ``` | copilot, retention, cohort |
| ... | ... | ... | ... | ... |

---

## Notes
- All metrics use Purchase license filter
- Retention cohorts based on days since first activity
- Percentages rounded to 4 decimal places
```

---

## BEST PRACTICES

✅ Use **complete** Snowflake paths: `DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.TABLE`

✅ Include **full DESC output** with all columns

✅ Request **10-20 metrics** per view (not too few, not too many)

✅ Ask for **SQL queries in code blocks** (```sql ```)

✅ Request **proper Snowflake functions** (DATEADD, CURRENT_DATE, etc.)

✅ Ask for **relevant tags** for metric discovery

❌ Don't use **SELECT ***

❌ Don't use **hardcoded dates**

❌ Don't request **incomplete SQL**

---

## SAVE YOUR OUTPUT

```bash
# Save Claude's output to file
# Name it: {product_name}.metrics.md
# Example: ask_alteryx.metrics.md

# Then add to ZIP if needed:
zip metrics_skill.zip ask_alteryx.metrics.md alteryx_one.metrics.md trial.metrics.md ...
```

---

## NEED HELP?

**Can't find your view?**
→ Run: `SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE '%VIEW' LIMIT 50`

**View has no columns?**
→ Check if it exists: `DESC DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.YOUR_VIEW`

**Claude output incomplete?**
→ Re-submit with: "Generate at least 15 metrics from this view"

**Have questions?**
→ insights@alteryx.com

---

**That's it! You're ready to generate metrics. 🚀**
