# Product Metrics Index

**Database:** DISCOVERY_PRODUCT_MANAGEMENT  
**Schema:** METRIC_STORE  
**Last Updated:** 2026-08-04  

---

## Overview

Complete index of all Alteryx product metrics with direct links to comprehensive reference documents.

| Product | Total Metrics | Reference | Status |
|---------|---------------|-----------|--------|
| **Account User** | 16 | [ACCOUNT_USER_METRICS_REFERENCE.md](./account_user/ACCOUNT_USER_METRICS_REFERENCE.md) | ✅ Active |
| **Alteryx One** | 56 | [ALTERYX-ONE_METRICS_REFERENCE.md](./alteryx-one/ALTERYX-ONE_METRICS_REFERENCE.md) | ✅ Active |
| **Ask Alteryx (Copilot)** | 45 | [COPILOT_METRICS_COMPLETE_REFERENCE.md](./ask_alteryx/COPILOT_METRICS_COMPLETE_REFERENCE.md) | ✅ Active |
| **Designer** | 15 | [DESIGNER_METRICS_REFERENCE.md](./designer/DESIGNER_METRICS_REFERENCE.md) | ✅ Active |
| **Trial** | 19 | [TRIAL_METRICS_REFERENCE.md](./trial/TRIAL_METRICS_REFERENCE.md) | ✅ Active |
| **Version Adoption** | 21 | [VERSION_ADOPTION_METRICS_REFERENCE.md](./version_adoption/VERSION_ADOPTION_METRICS_REFERENCE.md) | ✅ Active |
| **TOTAL** | **172** | — | — |

---

## Quick Links

### By Product

- **[Account User](./account_user/)** - User account lifecycle and management metrics
  - 16 metrics across account types and lifecycle stages
  - Key metrics: Active accounts, new signups, churn

- **[Alteryx One](./alteryx-one/)** - Platform adoption and engagement metrics
  - 56 metrics covering adoption, engagement, retention, deployment
  - Key metrics: Active users, deployment rate, user retention

- **[Ask Alteryx / Copilot](./ask_alteryx/)** - AI assistant adoption and usage metrics
  - 45 metrics across adoption, engagement, retention, workflow usage
  - Key metrics: Adoption percentage, engaged users, workflow runs
  - **Reference:** COPILOT_METRICS_COMPLETE_REFERENCE.md (comprehensive with definitions)

- **[Designer](./designer/)** - Desktop product metrics
  - 15 metrics for designer usage and execution
  - Key metrics: Active users, workflow execution, version adoption

- **[Trial](./trial/)** - Trial conversion and user onboarding metrics
  - 19 metrics for trial experience and conversion
  - Key metrics: Trial signups, conversion rate, completion time

- **[Version Adoption](./version_adoption/)** - Product version adoption metrics
  - 21 metrics tracking version usage patterns
  - Key metrics: Version adoption rate, upgrade velocity, supported versions

---

## Metric Categories Across All Products

### Adoption Metrics (37 total)
Measures how users/accounts are adopting products and features
- Adoption rate
- Adoption velocity
- Adoption gap
- New activations

**Products:** Alteryx One, Ask Alteryx, Designer, Trial, Version Adoption

### Engagement Metrics (28 total)
Measures depth of usage and feature interaction
- Engagement rate
- Highly engaged users
- Feature adoption
- User retention

**Products:** Alteryx One, Ask Alteryx, Account User

### Funnel Metrics (18 total)
Measures progression through user journey stages
- Account funnel health
- User funnel health
- Conversion funnel
- Qualification funnel

**Products:** Alteryx One, Ask Alteryx, Trial

### Retention Metrics (16 total)
Measures user return and churn
- 7-15 day retention
- 30-60 day retention
- Churn rate
- Retention decay

**Products:** Ask Alteryx, Alteryx One

### Volume Metrics (42 total)
Measures absolute counts and quantities
- Active users
- Active accounts
- Onboarded users
- Enabled users

**Products:** All products

### Market Size Metrics (12 total)
Measures addressable market and eligibility
- Eligible accounts
- Eligible users
- Penetration rate
- Eligibility rate

**Products:** Ask Alteryx, Alteryx One

### Usage Metrics (13 total)
Measures feature and product usage
- Workflow runs
- Feature usage
- Usage percentage
- Query volume

**Products:** Ask Alteryx, Designer

### Quality Metrics (6 total)
Measures data and execution quality
- Execution success rate
- Data quality
- Version distribution

**Products:** Designer, Alteryx One

---

## Base Tables by Product

### Ask Alteryx / Copilot
- `COPILOT_ACTIVITY_USAGE_AT` - Core activity tracking
- `ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT` - Account monthly metrics
- `COPILOT_DESIGNER_WORKFLOW_PCT_AT` - Workflow execution metrics

### Alteryx One
- `ALTERYX_ONE_ACTIVITY_USAGE_AT` - Platform activity
- `ALTERYX_ONE_ENGAGEMENT_FUNNEL_AT` - Engagement progression
- `ALTERYX_ONE_ACCOUNT_METRICS_AT` - Account-level metrics

### Designer
- `DESIGNER_ACTIVITY_USAGE_AT` - Desktop app activity
- `DESIGNER_EXECUTION_STATS_AT` - Workflow execution

### Trial
- `TRIAL_USER_JOURNEY_AT` - Trial user progression
- `TRIAL_CONVERSION_FUNNEL_AT` - Conversion tracking

### Account User
- `ACCOUNT_USER_LIFECYCLE_AT` - Account lifecycle events
- `USER_ACTIVITY_SUMMARY_AT` - User activity summary

### Version Adoption
- `VERSION_ADOPTION_METRICS_AT` - Version usage metrics
- `ACCOUNT_VERSION_DISTRIBUTION_AT` - Version distribution

---

## How to Use These References

### Finding a Specific Metric

1. **Know the product?**
   - Use the table above to find the product reference
   - Open the reference document
   - Use Ctrl+F to search for the metric

2. **Know the metric name?**
   - Search all references for keyword
   - All references follow consistent format

3. **Know the category?**
   - See "Metric Categories" section above
   - Find which products have that category
   - Check those product references

### Understanding a Metric

Each metric reference includes:
- **Definition:** What the metric measures
- **Source View/Table:** Where data comes from
- **SQL Query:** How to calculate the metric
- **Dependencies:** Other metrics it depends on
- **Status:** Current state (validated, draft, deprecated)
- **Freshness:** How often data updates
- **Tags:** Categorization and searchability

### Running a Metric Query

1. Open the product's reference document
2. Find the metric you need
3. Copy the SQL query section
4. Paste into Snowflake
5. Execute in DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE schema

---

## Generator Script

All references are auto-generated from the YAML metric definitions.

**Script:** `generate_all_metrics_references.py`

**To regenerate all references:**
```bash
cd /Users/ayx105566/Alteryx August/Product-Insights-AI/products
python3 generate_all_metrics_references.py
```

**To add a new product:**
1. Create directory: `products/new_product_name/`
2. Create metrics YAML files in `new_product_name/metrics/`
3. Run the generator script
4. Reference is automatically created

---

## Setting Up a New Product

See: [PRODUCT_METRICS_TEMPLATE.md](./PRODUCT_METRICS_TEMPLATE.md)

**Quick steps:**
1. Create product directory
2. Create `product_context.yaml`
3. Create metric YAML files
4. Run generator script
5. Reference document created automatically

---

## Metrics by Aggregation Level

### Overall/Snapshot
Metrics aggregated across all time
- Alteryx One: Total active users, total accounts
- Ask Alteryx: Total eligible users
- Designer: Total active users

### Monthly
Metrics broken down by month
- Ask Alteryx: Monthly account eligibility
- Alteryx One: Monthly adoption rates
- Version Adoption: Monthly version distribution

### Cohort-Based
Metrics tracking user cohorts over time
- Ask Alteryx: 7-15 day retention, 30-60 day retention
- Alteryx One: Cohort retention analysis
- Trial: Conversion funnel by cohort

### Daily (Real-time)
Metrics updated daily
- Ask Alteryx: Active users, engaged users
- Designer: Execution counts
- Alteryx One: Daily engagement

---

## Data Freshness

| Freshness | Products | Update Schedule |
|-----------|----------|-----------------|
| Real-time | Ask Alteryx, Designer | Multiple times daily |
| Daily | All products | Once per day |
| Weekly | Account User, Version Adoption | Weekly |
| Monthly | Alteryx One, Trial | Monthly |

---

## Metric Quality Standards

All metrics meet these requirements:
- ✅ Defined in YAML with required fields
- ✅ SQL tested and validated
- ✅ Documentation complete
- ✅ Marked as "validated" status
- ✅ Data quality expectations documented
- ✅ Dependencies tracked
- ✅ Regular maintenance schedule

---

## Support & Contact

For questions about:
- **Specific metrics:** See maintainer field in reference
- **SQL queries:** Review the query in reference document
- **New metrics:** Use PRODUCT_METRICS_TEMPLATE.md
- **Generator script:** Contact analytics-team@alteryx.com

---

## Version History

| Date | Change |
|------|--------|
| 2026-08-04 | Initial index created, all products documented |

---

## Related Documentation

- [Product Metrics Template](./PRODUCT_METRICS_TEMPLATE.md) - How to add new products
- [Copilot Complete Reference](./ask_alteryx/COPILOT_METRICS_COMPLETE_REFERENCE.md) - Detailed example
- [Product Context Files](./*/product_context.yaml) - Individual product details

