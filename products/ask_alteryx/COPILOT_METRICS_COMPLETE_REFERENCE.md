# Copilot Metrics Complete Reference

**Database:** DISCOVERY_PRODUCT_MANAGEMENT  
**Schema:** METRIC_STORE  
**Product:** ask_alteryx (Copilot)  
**Generated:** 2026-08-04  

---

## Overview

Complete reference for all Copilot metrics with definitions and individual SQL queries.
Each metric shows the calculation from base tables with monthly-level aggregations where applicable.

---

# COPILOT_USERS_ACTIVITY_FUNNEL_VIEW Metrics

## 1. ONBOARDED_USERS

**Definition:** Distinct count of Purchase users of type AACP (Alteryx AI Copilot Participant) with a valid email address who are present in the source activity data. This represents the total cohort of users eligible for Copilot usage analysis.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- USER_TYPE = 'aacp'
- USER_EMAIL IS NOT NULL

**Query:**
```sql
SELECT
    COUNT(DISTINCT USER_ID_RAW) AS ONBOARDED_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE LICENSE_TYPE = 'Purchase'
  AND USER_TYPE = 'aacp'
  AND USER_EMAIL IS NOT NULL
```

---

## 2. ACTIVE_USERS

**Definition:** Distinct count of onboarded users who have demonstrated activity by initiating at least one chat session. This metric identifies the engaged portion of the onboarded user cohort.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- USER_TYPE = 'aacp'
- USER_EMAIL IS NOT NULL
- CHAT_ID IS NOT NULL

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN CHAT_ID IS NOT NULL
        THEN USER_ID_RAW
    END) AS ACTIVE_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE LICENSE_TYPE = 'Purchase'
  AND USER_TYPE = 'aacp'
  AND USER_EMAIL IS NOT NULL
```

---

## 3. USERS_WITH_AT_LEAST_1_WORKFLOW

**Definition:** Distinct count of active users who have created or associated at least one non-empty workflow with their chat activities. This represents users who have moved beyond simple chat interactions to workflow creation.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- USER_TYPE = 'aacp'
- USER_EMAIL IS NOT NULL
- CHAT_ID IS NOT NULL
- WORKFLOW_ID IS NOT NULL
- WORKFLOW_ID <> ''

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN CHAT_ID IS NOT NULL
         AND WORKFLOW_ID IS NOT NULL
         AND WORKFLOW_ID <> ''
        THEN USER_ID_RAW
    END) AS USERS_WITH_AT_LEAST_1_WORKFLOW
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE LICENSE_TYPE = 'Purchase'
  AND USER_TYPE = 'aacp'
  AND USER_EMAIL IS NOT NULL
```

---

## 4. ENGAGED_USERS

**Definition:** Distinct count of users who have reached high engagement by creating five or more distinct conversations. This represents the most engaged segment of the user base, indicating serious product adoption.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- USER_TYPE = 'aacp'
- USER_EMAIL IS NOT NULL
- CHAT_ID IS NOT NULL
- GROUP BY USER_ID_RAW
- HAVING COUNT(DISTINCT CONVERSATION_ID) >= 5

**Query:**
```sql
WITH engaged_users AS (
    SELECT
        USER_ID_RAW
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE LICENSE_TYPE = 'Purchase'
      AND USER_TYPE = 'aacp'
      AND USER_EMAIL IS NOT NULL
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_ID_RAW
    HAVING COUNT(DISTINCT CONVERSATION_ID) >= 5
)
SELECT
    COUNT(DISTINCT USER_ID_RAW) AS ENGAGED_USERS
FROM engaged_users
```

---

# COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW Metrics

## 5. ONBOARDED_ACCOUNTS

**Definition:** Distinct count of Purchase accounts containing at least one AACP user present in the activity data. This represents the total set of accounts where Copilot has organizational presence.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- license_type = 'Purchase'
- user_type = 'aacp'
- billing_account_id_raw IS NOT NULL

**Query:**
```sql
SELECT
    COUNT(DISTINCT billing_account_id_raw) AS onboarded_accounts
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE license_type = 'Purchase'
  AND user_type = 'aacp'
  AND billing_account_id_raw IS NOT NULL
```

---

## 6. ACTIVE_ACCOUNTS

**Definition:** Distinct count of onboarded accounts that contain at least one chat activity. This identifies accounts with actual product usage.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- license_type = 'Purchase'
- user_type = 'aacp'
- billing_account_id_raw IS NOT NULL
- chat_id IS NOT NULL

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN chat_id IS NOT NULL
        THEN billing_account_id_raw
    END) AS active_accounts
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE license_type = 'Purchase'
  AND user_type = 'aacp'
  AND billing_account_id_raw IS NOT NULL
```

---

## 7. ACCOUNTS_WITH_AT_LEAST_1_WORKFLOW

**Definition:** Distinct count of active accounts that have created at least one non-empty workflow. This represents accounts that have moved beyond basic chat usage to workflow automation.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- license_type = 'Purchase'
- user_type = 'aacp'
- billing_account_id_raw IS NOT NULL
- chat_id IS NOT NULL
- workflow_id IS NOT NULL
- workflow_id <> ''

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN chat_id IS NOT NULL
         AND workflow_id IS NOT NULL
         AND workflow_id <> ''
        THEN billing_account_id_raw
    END) AS accounts_with_at_least_1_workflow
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE license_type = 'Purchase'
  AND user_type = 'aacp'
  AND billing_account_id_raw IS NOT NULL
```

---

## 8. ENGAGED_ACCOUNTS

**Definition:** Distinct count of accounts that contain at least one AACP user who has achieved high engagement (5+ distinct conversations). This represents accounts with power users of the product.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- license_type = 'Purchase'
- user_type = 'aacp'
- chat_id IS NOT NULL
- billing_account_id_raw IS NOT NULL
- GROUP BY billing_account_id_raw, created_by_id
- HAVING COUNT(DISTINCT conversation_id) >= 5

**Query:**
```sql
WITH engaged_accounts AS (
    SELECT
        billing_account_id_raw
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE license_type = 'Purchase'
      AND user_type = 'aacp'
      AND chat_id IS NOT NULL
      AND billing_account_id_raw IS NOT NULL
    GROUP BY
        billing_account_id_raw,
        created_by_id
    HAVING COUNT(DISTINCT conversation_id) >= 5
)
SELECT
    COUNT(DISTINCT billing_account_id_raw) AS engaged_accounts
FROM engaged_accounts
```

---

# COPILOT_ELIGIBLE_ACCOUNT_FUNNEL_VIEW Metrics (Monthly Level)

## 9. TOTAL_AYX_ACCOUNTS

**Definition:** Monthly count of distinct Purchase Alteryx billing accounts. This is the total addressable market of all Alteryx customers.

**Base Table:** ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT

**Aggregation Level:** Monthly (YEAR_MONTH)

**Filters:**
- PRODUCT_NAME = 'ALTERYX'
- LICENSE_TYPE = 'Purchase'
- YEAR_MONTH > '2026-01-01'

**Query:**
```sql
SELECT
    YEAR_MONTH::DATE AS MONTH_YEAR,
    COUNT(DISTINCT BILLING_ACCOUNT_ID_RAW) AS TOTAL_AYX_ACCOUNTS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT
WHERE PRODUCT_NAME = 'ALTERYX'
  AND LICENSE_TYPE = 'Purchase'
  AND YEAR_MONTH > '2026-01-01'
GROUP BY YEAR_MONTH::DATE
ORDER BY YEAR_MONTH::DATE DESC
```

---

## 10. TOTAL_AYX1_ACCOUNTS

**Definition:** Monthly count of distinct Purchase Alteryx accounts on 2025 Pricing & Packaging. This represents the modern account base eligible for new products.

**Base Table:** ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT

**Aggregation Level:** Monthly (YEAR_MONTH)

**Filters:**
- PRODUCT_NAME = 'ALTERYX'
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = 2025
- YEAR_MONTH > '2026-01-01'

**Query:**
```sql
SELECT
    YEAR_MONTH::DATE AS MONTH_YEAR,
    COUNT(DISTINCT CASE  
        WHEN PRICING_AND_PACKAGING = 2025
        THEN BILLING_ACCOUNT_ID_RAW
    END) AS TOTAL_AYX1_ACCOUNTS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT
WHERE PRODUCT_NAME = 'ALTERYX'
  AND LICENSE_TYPE = 'Purchase'
  AND YEAR_MONTH > '2026-01-01'
GROUP BY YEAR_MONTH::DATE
ORDER BY YEAR_MONTH::DATE DESC
```

---

## 11. ACCOUNTS_WITH_ENT_AND_PRO

**Definition:** Monthly count of distinct AYX1 Purchase accounts with Enterprise or Professional edition. These are the accounts that meet the minimum tier requirement for Copilot eligibility.

**Base Table:** ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT

**Aggregation Level:** Monthly (YEAR_MONTH)

**Filters:**
- PRODUCT_NAME = 'ALTERYX'
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = 2025
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- YEAR_MONTH > '2026-01-01'

**Query:**
```sql
SELECT
    YEAR_MONTH::DATE AS MONTH_YEAR,
    COUNT(DISTINCT CASE 
        WHEN PRICING_AND_PACKAGING = 2025
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
        THEN BILLING_ACCOUNT_ID_RAW
    END) AS ACCOUNTS_WITH_ENT_AND_PRO
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT
WHERE PRODUCT_NAME = 'ALTERYX'
  AND LICENSE_TYPE = 'Purchase'
  AND YEAR_MONTH > '2026-01-01'
GROUP BY YEAR_MONTH::DATE
ORDER BY YEAR_MONTH::DATE DESC
```

---

## 12. COPILOT_ELIGIBLE_ACCOUNTS

**Definition:** Monthly count of distinct Enterprise/Professional AYX1 Purchase accounts running product version 2025.2 or higher. These accounts meet all technical and licensing requirements for Copilot usage.

**Base Table:** ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT

**Aggregation Level:** Monthly (YEAR_MONTH)

**Filters:**
- PRODUCT_NAME = 'ALTERYX'
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = 2025
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- ACCOUNT_MAX_VERSION >= '2025.2'
- YEAR_MONTH > '2026-01-01'

**Query:**
```sql
SELECT
    YEAR_MONTH::DATE AS MONTH_YEAR,
    COUNT(DISTINCT CASE 
        WHEN PRICING_AND_PACKAGING = 2025
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND ACCOUNT_MAX_VERSION >= '2025.2'
        THEN BILLING_ACCOUNT_ID_RAW
    END) AS COPILOT_ELIGIBLE_ACCOUNTS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT
WHERE PRODUCT_NAME = 'ALTERYX'
  AND LICENSE_TYPE = 'Purchase'
  AND YEAR_MONTH > '2026-01-01'
GROUP BY YEAR_MONTH::DATE
ORDER BY YEAR_MONTH::DATE DESC
```

---

# COPILOT_ELIGBLE_USERS_VIEW Metrics

## 13. ENTERPRISE_PRO_USERS

**Definition:** Distinct count of activated users belonging to Purchase accounts on 2025 Pricing & Packaging with Enterprise or Professional edition. These users have access to enterprise-grade features.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = '2025'
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- STATUS = 'ACTIVATED'
- ALTERYX_USER_EMAIL IS NOT NULL

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
        THEN USER_ID_RAW
    END) AS ENTERPRISE_PRO_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
```

---

## 14. COPILOT_ENABLED_USERS

**Definition:** Distinct count of activated Enterprise/Professional AYX1 users where Copilot feature flag has been explicitly enabled by administrators. This represents the administratively-approved user base.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = '2025'
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- STATUS = 'ACTIVATED'
- ALTERYX_USER_EMAIL IS NOT NULL
- COPILOT_ENABLED = TRUE

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
         AND COPILOT_ENABLED = TRUE
        THEN USER_ID_RAW
    END) AS COPILOT_ENABLED_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
```

---

## 15. ELIGIBLE_USERS_2025_2

**Definition:** Distinct count of activated Enterprise/Professional AYX1 users with Copilot enabled and running product version 2025.2 or higher. These users meet technical version requirements.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = '2025'
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- STATUS = 'ACTIVATED'
- ALTERYX_USER_EMAIL IS NOT NULL
- COPILOT_ENABLED = TRUE
- MAXIMUM_RAW_PRODUCT_VERSION >= '2025.2'

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
         AND COPILOT_ENABLED = TRUE
         AND MAXIMUM_RAW_PRODUCT_VERSION >= '2025.2'
        THEN USER_ID_RAW
    END) AS ELIGIBLE_USERS_2025_2
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
```

---

## 16. COPILOT_ELIGIBLE_USERS

**Definition:** Distinct count of activated Enterprise/Professional AYX1 users satisfying ALL Copilot eligibility criteria: Copilot enabled, Designer activated, not using offline activation, and running product version 2025.2. These users represent the fully-qualified Copilot user base.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = '2025'
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- STATUS = 'ACTIVATED'
- ALTERYX_USER_EMAIL IS NOT NULL
- COPILOT_ENABLED = TRUE
- DESIGNER_ACTIVATION_STATUS = TRUE
- DESIGNER_OFFLINE_ACTIVATION = FALSE
- MAXIMUM_RAW_PRODUCT_VERSION = '2025.2'

**Query:**
```sql
SELECT
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
         AND COPILOT_ENABLED = TRUE
         AND DESIGNER_ACTIVATION_STATUS = TRUE
         AND DESIGNER_OFFLINE_ACTIVATION = FALSE
         AND MAXIMUM_RAW_PRODUCT_VERSION = '2025.2'
        THEN USER_ID_RAW
    END) AS COPILOT_ELIGIBLE_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
```

---

# COPILOT_WORKFLOW_DETAILS_VIEW Metrics

## 17. COPILOT_MAPPED_WORKFLOW_RUNS

**Definition:** Total count of Designer workflow runs that have been successfully mapped or generated by Ask Alteryx (Copilot). This represents the volume of Copilot-assisted workflows executed.

**Base Table:** COPILOT_DESIGNER_WORKFLOW_PCT_AT

**Query:**
```sql
SELECT
    COPILOT_MAPPED_WORKFLOW_RUNS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_DESIGNER_WORKFLOW_PCT_AT
```

---

## 18. COPILOT_PCT_WORKFLOW_RUNS

**Definition:** Percentage of all Designer workflow runs that were generated or mapped to Ask Alteryx (Copilot) workflows. This metric shows Copilot penetration in the workflow execution ecosystem. Returned as decimal ratio (0-1).

**Base Table:** COPILOT_DESIGNER_WORKFLOW_PCT_AT

**Query:**
```sql
SELECT
    ROUND(COPILOT_PCT_WORKFLOW_RUNS / 100.0, 4) AS COPILOT_PCT_WORKFLOW_RUNS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_DESIGNER_WORKFLOW_PCT_AT
```

---

# COPILOT_7_15_RETENTION_RATE_VIEW Metrics

## 19. TOTAL_USERS (7-15 Day Retention)

**Definition:** Total count of users eligible for 7-15 day retention analysis. These are users whose first Copilot activity occurred at least 7 days ago, making them candidates for measuring return behavior.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- ACCOUNT_EDITION IN ('Professional','Enterprise')
- LICENSE_TYPE = 'Purchase'
- CHAT_ID IS NOT NULL
- first_date <= DATEADD(day, -7, CURRENT_DATE())

**Query:**
```sql
WITH first_use AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        MIN(CAST(CONV_CREATED_DATE AS DATE)) AS first_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_EMAIL
),
eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -7, CURRENT_DATE())
)
SELECT
    COUNT(*) AS TOTAL_USERS
FROM eligible_cohort
```

---

## 20. RETURNING_USERS_7_15D

**Definition:** Count of eligible users who returned to use Copilot at least once between Day 7 and Day 15 after their initial first use. This measures short-term retention behavior.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Retention Window:** Day 7 to Day 15 after first use

**Query:**
```sql
WITH first_use AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        MIN(CAST(CONV_CREATED_DATE AS DATE)) AS first_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_EMAIL
),
eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -7, CURRENT_DATE())
),
user_activity AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        CAST(CONV_CREATED_DATE AS DATE) AS activity_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
),
returns_7_15 AS (
    SELECT
        fu.CREATED_BY_ID,
        MIN(ua.activity_date) AS first_return_date_in_window
    FROM eligible_cohort fu
    JOIN user_activity ua
      ON ua.CREATED_BY_ID = fu.CREATED_BY_ID
     AND ua.activity_date BETWEEN DATEADD(day, 7, fu.first_date)
                              AND DATEADD(day, 15, fu.first_date)
    GROUP BY fu.CREATED_BY_ID
)
SELECT
    COUNT(*) AS RETURNING_USERS_7_15D
FROM returns_7_15
```

---

## 21. RETURNING_RATE_PCT (7-15 Day)

**Definition:** Percentage of eligible users (7-15 day cohort) who returned to use Copilot at least once during the 7-15 day window. Returned as decimal ratio (0-1).

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Formula:** (RETURNING_USERS_7_15D / TOTAL_USERS) * 100

**Query:**
```sql
WITH first_use AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        MIN(CAST(CONV_CREATED_DATE AS DATE)) AS first_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_EMAIL
),
eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -7, CURRENT_DATE())
),
user_activity AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        CAST(CONV_CREATED_DATE AS DATE) AS activity_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
),
returns_7_15 AS (
    SELECT
        fu.CREATED_BY_ID,
        MIN(ua.activity_date) AS first_return_date_in_window
    FROM eligible_cohort fu
    JOIN user_activity ua
      ON ua.CREATED_BY_ID = fu.CREATED_BY_ID
     AND ua.activity_date BETWEEN DATEADD(day, 7, fu.first_date)
                              AND DATEADD(day, 15, fu.first_date)
    GROUP BY fu.CREATED_BY_ID
)
SELECT
    ROUND(
        ROUND(
            (SELECT COUNT(*) FROM returns_7_15) * 100.0 /
            NULLIF((SELECT COUNT(*) FROM eligible_cohort), 0),
            2
        ) / 100.0,
        4
    ) AS RETURNING_RATE_PCT
```

---

# COPILOT_30_60_RETENTION_RATE_VIEW Metrics

## 22. TOTAL_USERS (30-60 Day Retention)

**Definition:** Total count of users eligible for 30-60 day retention analysis. These are users whose first Copilot activity occurred at least 30 days ago, making them candidates for measuring longer-term return behavior.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- ACCOUNT_EDITION IN ('Professional','Enterprise')
- LICENSE_TYPE = 'Purchase'
- CHAT_ID IS NOT NULL
- first_date <= DATEADD(day, -30, CURRENT_DATE())

**Query:**
```sql
WITH first_use AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        MIN(CAST(CONV_CREATED_DATE AS DATE)) AS first_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_EMAIL
),
eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -30, CURRENT_DATE())
)
SELECT
    COUNT(*) AS TOTAL_USERS
FROM eligible_cohort
```

---

## 23. RETURNING_USERS_30_60D

**Definition:** Count of eligible users who returned to use Copilot at least once between Day 30 and Day 60 after their initial first use. This measures medium-term retention behavior.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Retention Window:** Day 30 to Day 60 after first use

**Query:**
```sql
WITH first_use AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        MIN(CAST(CONV_CREATED_DATE AS DATE)) AS first_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_EMAIL
),
eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -30, CURRENT_DATE())
),
user_activity AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        CAST(CONV_CREATED_DATE AS DATE) AS activity_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
),
returns_30_60 AS (
    SELECT
        e.CREATED_BY_ID,
        MIN(ua.activity_date) AS first_return_date_in_window
    FROM eligible_cohort e
    JOIN user_activity ua
      ON ua.CREATED_BY_ID = e.CREATED_BY_ID
     AND ua.activity_date BETWEEN DATEADD(day, 30, e.first_date)
                              AND DATEADD(day, 60, e.first_date)
    GROUP BY e.CREATED_BY_ID
)
SELECT
    COUNT(*) AS RETURNING_USERS_30_60D
FROM returns_30_60
```

---

## 24. RETURNING_RATE_PCT (30-60 Day)

**Definition:** Percentage of eligible users (30-60 day cohort) who returned to use Copilot at least once during the 30-60 day window. Returned as decimal ratio (0-1).

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Formula:** (RETURNING_USERS_30_60D / TOTAL_USERS) * 100

**Query:**
```sql
WITH first_use AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        MIN(CAST(CONV_CREATED_DATE AS DATE)) AS first_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
    GROUP BY USER_EMAIL
),
eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -30, CURRENT_DATE())
),
user_activity AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        CAST(CONV_CREATED_DATE AS DATE) AS activity_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
),
returns_30_60 AS (
    SELECT
        e.CREATED_BY_ID,
        MIN(ua.activity_date) AS first_return_date_in_window
    FROM eligible_cohort e
    JOIN user_activity ua
      ON ua.CREATED_BY_ID = e.CREATED_BY_ID
     AND ua.activity_date BETWEEN DATEADD(day, 30, e.first_date)
                              AND DATEADD(day, 60, e.first_date)
    GROUP BY e.CREATED_BY_ID
)
SELECT
    ROUND(
        ROUND(
            (SELECT COUNT(*) FROM returns_30_60) * 100.0 /
            NULLIF((SELECT COUNT(*) FROM eligible_cohort), 0),
            2
        ) / 100.0,
        4
    ) AS RETURNING_RATE_PCT
```

---

# COPILOT_USERS_ADOPTION_RATE_VIEW Metrics

## 25. ACTIVE_USERS (Adoption)

**Definition:** Distinct count of Purchase AACP users with at least one Copilot chat activity. This is the numerator in adoption rate calculation.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- USER_TYPE = 'aacp'
- USER_ID_RAW IS NOT NULL
- USER_EMAIL IS NOT NULL
- CHAT_ID IS NOT NULL

**Query:**
```sql
SELECT
    COUNT(DISTINCT USER_ID_RAW) AS ACTIVE_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE LICENSE_TYPE = 'Purchase'
  AND USER_TYPE = 'aacp'
  AND USER_ID_RAW IS NOT NULL
  AND USER_EMAIL IS NOT NULL
  AND CHAT_ID IS NOT NULL
```

---

## 26. ELIGIBLE_USERS (Adoption)

**Definition:** Distinct count of users satisfying all Copilot eligibility criteria. This is the denominator in adoption rate calculation.

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Filters:**
- LICENSE_TYPE = 'Purchase'
- PRICING_AND_PACKAGING = '2025'
- ACCOUNT_EDITION IN ('Enterprise', 'Professional')
- STATUS = 'ACTIVATED'
- ALTERYX_USER_EMAIL IS NOT NULL
- COPILOT_ENABLED = TRUE
- DESIGNER_ACTIVATION_STATUS = TRUE
- DESIGNER_OFFLINE_ACTIVATION = FALSE
- MAXIMUM_RAW_PRODUCT_VERSION >= 2025.2

**Query:**
```sql
SELECT
    COUNT(DISTINCT USER_ID_RAW) AS ELIGIBLE_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE LICENSE_TYPE = 'Purchase'
  AND PRICING_AND_PACKAGING = '2025'
  AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
  AND STATUS = 'ACTIVATED'
  AND ALTERYX_USER_EMAIL IS NOT NULL
  AND COPILOT_ENABLED = TRUE
  AND DESIGNER_ACTIVATION_STATUS = TRUE
  AND DESIGNER_OFFLINE_ACTIVATION = FALSE
  AND TRY_TO_DECIMAL(MAXIMUM_RAW_PRODUCT_VERSION, 10, 2) >= 2025.2
```

---

## 27. ADOPTION_PERCENTAGE

**Definition:** Percentage of eligible users who have actively used Copilot (have at least one chat). This is the key adoption metric measuring actual product engagement. Returned as decimal ratio (0-1).

**Base Table:** COPILOT_ACTIVITY_USAGE_AT

**Formula:** (ACTIVE_USERS / ELIGIBLE_USERS) * 100

**Query:**
```sql
SELECT
    ROUND(
        ROUND(
            100.0 * 
            (SELECT COUNT(DISTINCT USER_ID_RAW) 
             FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
             WHERE LICENSE_TYPE = 'Purchase'
               AND USER_TYPE = 'aacp'
               AND USER_ID_RAW IS NOT NULL
               AND USER_EMAIL IS NOT NULL
               AND CHAT_ID IS NOT NULL) /
            NULLIF(
                (SELECT COUNT(DISTINCT USER_ID_RAW) 
                 FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
                 WHERE LICENSE_TYPE = 'Purchase'
                   AND PRICING_AND_PACKAGING = '2025'
                   AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
                   AND STATUS = 'ACTIVATED'
                   AND ALTERYX_USER_EMAIL IS NOT NULL
                   AND COPILOT_ENABLED = TRUE
                   AND DESIGNER_ACTIVATION_STATUS = TRUE
                   AND DESIGNER_OFFLINE_ACTIVATION = FALSE
                   AND TRY_TO_DECIMAL(MAXIMUM_RAW_PRODUCT_VERSION, 10, 2) >= 2025.2),
                0
            ),
            2
        ) / 100.0,
        4
    ) AS ADOPTION_PERCENTAGE
```

---

# Summary

**Total Metrics:** 27  
**Base Tables Used:**
- COPILOT_ACTIVITY_USAGE_AT (primary activity data)
- ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT (account hierarchy & editions)
- COPILOT_DESIGNER_WORKFLOW_PCT_AT (workflow execution metrics)

**Aggregation Levels:**
- Transaction level (individual chats, users, accounts)
- Monthly level (YEAR_MONTH aggregations)
- Cohort-based (retention window analysis)

**Key Dates & Filters:**
- Modern accounts: PRICING_AND_PACKAGING = 2025
- Eligible editions: Enterprise, Professional
- Min version: 2025.2
- Activity dates: YEAR_MONTH > '2026-01-01'
- Admin flags: Copilot_enabled = TRUE, Designer_activated = TRUE
