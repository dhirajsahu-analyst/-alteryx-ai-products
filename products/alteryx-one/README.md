# Alteryx One — Product Analytics Module

## Product Overview

**Alteryx One** is Alteryx's cloud-native, collaborative analytics platform enabling team-based analytics workflows.

This module provides:
- 17 semantic metric views
- 6 primary metrics (active users, activation, engagement, deployment, retention, funnel)
- Complete lineage from raw EDW tables
- Column-level documentation
- Data quality rules
- Example queries

## Quick Start

```sql
-- Active users this month
SELECT YEAR_MONTH, MONTHLY_ACTIVE_USER
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_ONE_ACTIVE_USERS_VIEW
WHERE YEAR_MONTH >= DATE_TRUNC('MONTH', CURRENT_DATE())
ORDER BY YEAR_MONTH DESC;
```

## Metric Catalog

| Metric | Grain | Source View | Status |
|--------|-------|------------|--------|
| Monthly Active Users | Monthly | ALTERYX_ONE_ACTIVE_USERS_VIEW | ✓ Validated |
| Activated Users | Monthly | ALTERYX_ONE_ACTIVE_USERS_VIEW | ✓ Validated |
| Engagement Rate | Monthly | ALTERYX_ONE_ENGAGED_ACCOUNTS_VIEW | ✓ Validated |
| Deployment Rate | Monthly | ALTERYX_ONE_DEPLOYED_ACCOUNT_PERCENTAGE_VIEW | ✓ Validated |
| Activation Funnel | Monthly | ALTERYX_ONE_ACTIVATION_FUNNEL_VIEW | ✓ Validated |
| User Retention | Cohort | ALTERYX_ONE_USERS_RETENTIONS_VIEW | ✓ Validated |

## Key Definitions

### Active User
A user who has performed at least one action within Alteryx One during the calendar month.

### Activated User
A user who has accepted an invitation and successfully logged in to Alteryx One.

### Engaged Account
An account with active users performing meaningful actions (e.g., creating/running workflows).

### Deployed Account
An account that has completed the deployment process and has at least one active user.

## Documentation

- [Metric Catalog](./metrics/) — Individual metric definitions
- [View Documentation](./views/) — View DDLs and purposes
- [Column Context](./columns/) — Column-level business meanings
- [Lineage](./lineage/) — Upstream and downstream dependencies
- [Examples](./examples/) — Sample queries and use cases
- [Data Quality](./data_quality/) — Freshness, volume, and validation rules

## Owner

**Product Owner:** Alteryx One Team
**Data Owner:** Analytics Data Team
**Support:** alteryx_one_team@alteryx.com

---

*Last Updated: 2026-08-03T12:26:18.260367*
