# New Product Metrics Structure Template

This document outlines the standard structure for setting up metrics for a new product in the Alteryx Product-Insights-AI system.

---

## Directory Structure for New Products

```
Product-Insights-AI/products/
└── new_product_name/
    ├── README.md                              # Product overview
    ├── CODEOWNERS                             # Team ownership
    ├── product_context.yaml                   # Product details
    ├── owners.yaml                            # Metric owners
    ├── {PRODUCT}_METRICS_REFERENCE.md         # Auto-generated comprehensive reference
    │
    ├── metrics/                               # Individual metric definitions
    │   ├── metric_001.yaml                    # Each metric as separate YAML
    │   ├── metric_002.yaml
    │   └── ...
    │
    └── data/                                  # (Optional) Supporting data
        └── sample_queries.sql
```

---

## Metric YAML File Structure

Each metric must be defined as a separate `.yaml` file in the `metrics/` directory.

### Required Fields

```yaml
id: metric_unique_identifier
name: "Human Readable Metric Name"
description: "Clear description of what this metric measures and its business purpose"

status: validated  # validated, draft, deprecated
category: adoption  # adoption, engagement, funnel, retention, volume, etc.

product: product_name  # Must match parent directory name

source:
  database: DISCOVERY_PRODUCT_MANAGEMENT
  schema: METRIC_STORE
  view: SOURCE_VIEW_NAME
  columns:
    - name: COLUMN_NAME
      type: NUMBER
      description: "What this column represents"

sql_template: |
  SELECT
    COLUMN_NAME as metric_value
  FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.SOURCE_VIEW_NAME
  WHERE filter_condition = 'value'
  LIMIT 100

expected_range:
  min: 0
  max: 100  # (optional)
  unit: percentage

grain: overall  # overall, daily, monthly, hourly, etc.
freshness: daily  # daily, weekly, monthly, real-time, etc.

maintainer: team@alteryx.com
depends_on:
  - related_metric_id_1
  - related_metric_id_2

related_metrics:
  - metric_id_of_related_metric

tags:
  - tag1
  - tag2

last_updated: "2026-08-04"
version: "1.0"
```

### Optional Fields

```yaml
# Data quality indicators
data_quality:
  - null_percentage: 0.5  # Expected % of nulls
  - duplicate_check: false

# Calculation formula
definition:
  business: "Business logic explanation"
  technical: "Technical calculation formula"

# Historical context
changelog:
  - date: "2026-08-04"
    change: "Initial creation"
```

---

## Generating the Comprehensive Reference

Once all metrics YAML files are created, run:

```bash
python3 generate_all_metrics_references.py
```

This will automatically create a `{PRODUCT}_METRICS_REFERENCE.md` file containing:
- All metrics organized by category
- Definitions and descriptions
- Source tables and views
- SQL queries
- Dependencies and relationships
- Tags and metadata

---

## Example: Creating a New Product "my_new_product"

### Step 1: Create Directory Structure
```bash
mkdir -p Product-Insights-AI/products/my_new_product/metrics
cd Product-Insights-AI/products/my_new_product
```

### Step 2: Create product_context.yaml
```yaml
product_name: my_new_product
product_display_name: "My New Product"
description: "Description of what this product does"
owner_team: "product-team@alteryx.com"
launch_date: "2026-08-04"
status: active
```

### Step 3: Create owners.yaml
```yaml
product_owner: person1@alteryx.com
technical_owner: person2@alteryx.com
data_owner: person3@alteryx.com
analysts:
  - analyst1@alteryx.com
  - analyst2@alteryx.com
```

### Step 4: Create README.md
```markdown
# My New Product

Description and overview of the product metrics.

## Available Metrics

See `MY_NEW_PRODUCT_METRICS_REFERENCE.md` for complete list.

## Base Tables

- `MY_PRODUCT_ACTIVITY_AT`: Daily activity tracking
- `MY_PRODUCT_ENGAGEMENT_FUNNEL`: User engagement progression

## Contact

- Product Owner: person1@alteryx.com
- Analytics Lead: analyst1@alteryx.com
```

### Step 5: Create Metric YAML Files

Create files like:
- `metrics/metric_001.yaml`
- `metrics/metric_002.yaml`
- etc.

### Step 6: Auto-Generate Reference
```bash
python3 generate_all_metrics_references.py
```

This creates: `MY_NEW_PRODUCT_METRICS_REFERENCE.md`

---

## Metric Naming Conventions

### ID Format
```
{product_short}_{metric_type}_{description}

Examples:
- copilot_adoption_rate
- designer_active_users
- trial_conversion_funnel
- alteryx_one_engagement_rate
```

### Name Format
```
"{Descriptive Name}" - Use title case, include context

Examples:
- "Copilot Adoption Rate"
- "Designer Active Users"
- "Trial to Paid Conversion"
- "Alteryx One Account Engagement"
```

### Category Format
Use one of:
- adoption
- engagement
- funnel
- retention
- volume
- market_size
- usage
- quality
- growth
- churn
- activation

---

## SQL Query Standards

All SQL queries should:

1. **Use full table paths**
   ```sql
   FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.TABLE_NAME
   ```

2. **Include meaningful column aliases**
   ```sql
   COUNT(DISTINCT user_id) as active_users_count
   ROUND(percentage, 2) as adoption_rate_pct
   ```

3. **Use LIMIT for safety**
   ```sql
   LIMIT 100  # or appropriate limit
   ```

4. **Handle nulls explicitly**
   ```sql
   WHERE value IS NOT NULL
   AND filter_condition > 0
   ```

5. **Use CTEs for complex logic**
   ```sql
   WITH cohort AS (
       SELECT ...
   ),
   returns AS (
       SELECT ...
   )
   SELECT ...
   FROM returns
   ```

---

## Product Dependencies Map

Include a dependency diagram showing:

```
Base Tables
    ↓
Raw Activity Tables (_AT suffix)
    ↓
Metric Store Views (METRIC_NAME_VIEW)
    ↓
Metrics (SQL queries)
    ↓
Dashboards & Reports
```

Example:
```
USER_ACTIVITY_AT
    ↓
COPILOT_USERS_ACTIVITY_FUNNEL_VIEW
    ↓
copilot_active_users, copilot_engaged_users, etc.
```

---

## Validation Checklist for New Product

- [ ] Directory created: `products/{product_name}/`
- [ ] `product_context.yaml` filled out
- [ ] `owners.yaml` with team info
- [ ] `README.md` with overview
- [ ] All metrics have `.yaml` files
- [ ] Each YAML has required fields
- [ ] SQL queries are tested in Snowflake
- [ ] Metric categories assigned consistently
- [ ] Dependencies documented
- [ ] Auto-generated reference created
- [ ] Reference added to main index

---

## Auto-Generation Process

The `generate_all_metrics_references.py` script:

1. **Discovers** all products in the `products/` directory
2. **Reads** each metric YAML file
3. **Extracts** definitions, SQL, and metadata
4. **Groups** metrics by category
5. **Generates** comprehensive markdown reference
6. **Saves** as `{PRODUCT}_METRICS_REFERENCE.md`

### Running the Generator

```bash
cd /Users/ayx105566/Alteryx\ August/Product-Insights-AI/products
python3 generate_all_metrics_references.py
```

### Output

For each product:
```
{PRODUCT}_METRICS_REFERENCE.md
├── Overview table (metrics by category)
├── Detailed metrics section (grouped by category)
│   ├── Metric ID
│   ├── Definition
│   ├── Source view/table
│   ├── SQL query
│   ├── Dependencies
│   └── Related metrics
└── Summary statistics
```

---

## Master Index

All product metric references are indexed in:
```
Product-Insights-AI/products/PRODUCT_METRICS_INDEX.md
```

This provides quick links to:
- Account User Metrics (16)
- Alteryx One Metrics (56)
- Ask Alteryx/Copilot Metrics (45)
- Designer Metrics (15)
- Trial Metrics (19)
- Version Adoption Metrics (21)

---

## Best Practices

1. **Keep metrics focused**: One metric = one clear measurement
2. **Document assumptions**: Explain filtering, aggregation logic
3. **Maintain dependencies**: Track which metrics depend on others
4. **Version metrics**: Increment version when logic changes
5. **Update freshness**: Keep freshness metadata current
6. **Archive old metrics**: Mark deprecated metrics as such
7. **Test queries**: Verify all SQL runs without errors
8. **Consistent naming**: Follow naming conventions strictly
9. **Link relationships**: Use tags and related_metrics fields
10. **Update dates**: Keep last_updated field current

---

## Support

For questions about metric structure:
- Check existing product examples
- Review `PRODUCT_METRICS_REFERENCE.md` files
- Contact: analytics-team@alteryx.com
