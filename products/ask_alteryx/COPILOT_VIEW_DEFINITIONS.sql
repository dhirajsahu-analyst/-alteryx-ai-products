-- ============================================================================
-- COPILOT METRIC STORE VIEW DEFINITIONS
-- ============================================================================
-- Generated: 8 of 8 views
-- Database: DISCOVERY_PRODUCT_MANAGEMENT
-- Schema: METRIC_STORE
-- ============================================================================


-- View: COPILOT_USERS_ACTIVITY_FUNNEL_VIEW
create or replace view COPILOT_USERS_ACTIVITY_FUNNEL_VIEW(
	ONBOARDED_USERS COMMENT 'Distinct Purchase users of type AACP with a valid email who are present in the source data.',
	ACTIVE_USERS COMMENT 'Distinct onboarded users with at least one chat activity.',
	USERS_WITH_AT_LEAST_1_WORKFLOW COMMENT 'Distinct active users with at least one non-empty workflow ID, indicating that a workflow was created or associated with chat activity.',
	ENGAGED_USERS COMMENT 'Distinct users who have created five or more distinct conversations.'
) as
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
    COUNT(DISTINCT USER_ID_RAW) AS ONBOARDED_USERS,
    COUNT(DISTINCT CASE
        WHEN CHAT_ID IS NOT NULL
        THEN USER_ID_RAW
    END) AS ACTIVE_USERS,
    COUNT(DISTINCT CASE
        WHEN CHAT_ID IS NOT NULL
         AND WORKFLOW_ID IS NOT NULL
         AND WORKFLOW_ID <> ''
        THEN USER_ID_RAW
    END) AS USERS_WITH_AT_LEAST_1_WORKFLOW,
    COUNT(DISTINCT CASE
        WHEN USER_ID_RAW IN (
            SELECT USER_ID_RAW
            FROM engaged_users
        )
        THEN USER_ID_RAW
    END) AS ENGAGED_USERS
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE LICENSE_TYPE = 'Purchase'
  AND USER_TYPE = 'aacp'
  AND USER_EMAIL IS NOT NULL;


-- ----------------------------------------------------------------------------
-- 5. View: COPILOT_USERS_ADOPTION_RATE.VIEW
-- ----------------------------------------------------------------------------;


-- View: COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW
create or replace view COPILOT_ACCOUNTS_ACTIVITY_FUNNEL_VIEW(
	ONBOARDED_ACCOUNTS COMMENT 'Distinct Purchase accounts with at least one AACP user present in the source data.',
	ACTIVE_ACCOUNTS COMMENT 'Distinct onboarded accounts with at least one chat activity.',
	ACCOUNTS_WITH_AT_LEAST_1_WORKFLOW COMMENT 'Distinct active accounts with at least one non-empty workflow ID, indicating that a workflow was created or associated with chat activity.',
	ENGAGED_ACCOUNTS COMMENT 'Distinct accounts with at least one AACP user who has created five or more distinct conversations.'
) as
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
    COUNT(DISTINCT billing_account_id_raw) AS onboarded_accounts,
    COUNT(DISTINCT CASE
        WHEN chat_id IS NOT NULL
        THEN billing_account_id_raw
    END) AS active_accounts,
    COUNT(DISTINCT CASE
        WHEN chat_id IS NOT NULL
         AND workflow_id IS NOT NULL
         AND workflow_id <> ''
        THEN billing_account_id_raw
    END) AS accounts_with_at_least_1_workflow,
    COUNT(DISTINCT CASE
        WHEN billing_account_id_raw IN (
            SELECT billing_account_id_raw
            FROM engaged_accounts
        )
        THEN billing_account_id_raw
    END) AS engaged_accounts
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
WHERE license_type = 'Purchase'
  AND user_type = 'aacp'
  AND billing_account_id_raw IS NOT NULL;


-- ----------------------------------------------------------------------------
-- 4. View: COPILOT_USERS_ACTIVITY_FUNNEL.VIEW
-- ----------------------------------------------------------------------------;


-- View: COPILOT_ELIGIBLE_ACCOUNT_FUNNEL_VIEW
create or replace view COPILOT_ELIGIBLE_ACCOUNT_FUNNEL_VIEW(
	MONTH_YEAR COMMENT 'The calendar reporting month normalized to the first day of the month.',
	TOTAL_AYX_ACCOUNTS COMMENT 'Distinct Purchase Alteryx billing accounts for the selected month.',
	TOTAL_AYX1_ACCOUNTS COMMENT 'Distinct Purchase Alteryx billing accounts on 2025 Pricing & Packaging.',
	ACCOUNTS_WITH_ENT_AND_PRO COMMENT 'Distinct AYX1 Purchase accounts with Enterprise or Professional edition.',
	COPILOT_ELIGIBLE_ACCOUNTS COMMENT 'Distinct Enterprise/Professional AYX1 Purchase accounts running product version 2025.2 or higher. These accounts are eligible to use Copilot.'
) as
SELECT 
    YEAR_MONTH::DATE AS MONTH_YEAR,
    COUNT(DISTINCT BILLING_ACCOUNT_ID_RAW) AS "TOTAL_AYX_ACCOUNTS",
    COUNT(DISTINCT CASE  
        WHEN PRICING_AND_PACKAGING = 2025
        THEN BILLING_ACCOUNT_ID_RAW
    END) AS "TOTAL_AYX1_ACCOUNTS",
    COUNT(DISTINCT CASE 
        WHEN PRICING_AND_PACKAGING = 2025
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
        THEN BILLING_ACCOUNT_ID_RAW
    END) AS "ACCOUNTS_WITH_ENT_AND_PRO",
    COUNT(DISTINCT CASE 
        WHEN PRICING_AND_PACKAGING = 2025
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND ACCOUNT_MAX_VERSION >= '2025.2'
        THEN BILLING_ACCOUNT_ID_RAW
    END) AS "COPILOT_ELIGIBLE_ACCOUNTS"
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT
WHERE PRODUCT_NAME = 'ALTERYX'
  AND LICENSE_TYPE = 'Purchase'
  AND YEAR_MONTH > '2026-01-01'
GROUP BY YEAR_MONTH::DATE
ORDER BY YEAR_MONTH::DATE DESC;


-- ----------------------------------------------------------------------------
-- 2. View: COPILOT_ELIGBLE_USERS_VIEW
-- ----------------------------------------------------------------------------;


-- View: COPILOT_ELIGBLE_USERS_VIEW
create or replace view COPILOT_ELIGBLE_USERS_VIEW(
	ENTERPRISE_PRO_USERS COMMENT 'Distinct activated users belonging to Purchase accounts on 2025 Pricing & Packaging with Enterprise or Professional edition.',
	COPILOT_ENABLED_USERS COMMENT 'Distinct activated Enterprise/Professional AYX1 users where Copilot has been enabled.',
	ELIGIBLE_USERS_2025_2 COMMENT 'Distinct activated Enterprise/Professional AYX1 users with Copilot enabled and running product version 2025.2 or higher. These users are eligible to use Copilot.',
	COPILOT_ELIGIBLE_USERS COMMENT 'Distinct activated Enterprise/Professional AYX1 users with Copilot enabled, Designer activated, not using offline activation, and currently on product version 2025.2. These users satisfy all current Copilot eligibility criteria.'
) as
SELECT
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
        THEN USER_ID_RAW
    END) AS ENTERPRISE_PRO_USERS,
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
         AND COPILOT_ENABLED = TRUE
        THEN USER_ID_RAW
    END) AS COPILOT_ENABLED_USERS,
    COUNT(DISTINCT CASE
        WHEN LICENSE_TYPE = 'Purchase'
         AND PRICING_AND_PACKAGING = '2025'
         AND ACCOUNT_EDITION IN ('Enterprise', 'Professional')
         AND STATUS = 'ACTIVATED'
         AND ALTERYX_USER_EMAIL IS NOT NULL
         AND COPILOT_ENABLED = TRUE
         AND MAXIMUM_RAW_PRODUCT_VERSION >= '2025.2'
        THEN USER_ID_RAW
    END) AS ELIGIBLE_USERS_2025_2,
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
FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT;


-- ----------------------------------------------------------------------------
-- 3. View: COPILOT_ACCOUNTS_ACTIVITY_FUNNEL.VIEW
-- ----------------------------------------------------------------------------;


-- View: COPILOT_WORKFLOW_DETAILS_VIEW
create or replace view COPILOT_WORKFLOW_DETAILS_VIEW(
	COPILOT_MAPPED_WORKFLOW_RUNS COMMENT 'Total number of Designer workflow runs mapped to workflows created by Ask Alteryx.',
	COPILOT_PCT_WORKFLOW_RUNS COMMENT 'The percentage of Designer workflow runs mapped to Copilot, represented as a decimal ratio between 0 and 1.'
) as
-- ============================================================================
-- VIEW: COPILOT_WORKFLOW_DETAILS_VIEW
-- DESCRIPTION: Computes Copilot mapped workflow runs and run percentage metrics,
-- using the standard metric source COPILOT_DESIGNER_WORKFLOW_PCT_AT.
-- ============================================================================
SELECT

-- ============================================
-- METRIC DEFINITIONS
-- ============================================

-- COPILOT_MAPPED_WORKFLOW_RUNS
-- Total number of workflow runs that have been successfully
-- mapped to workflows created by Ask Alteryx (Copilot).
-- Represents the numerator used in the Copilot Run Percentage metric.

    COPILOT_MAPPED_WORKFLOW_RUNS,

-- COPILOT_PCT_WORKFLOW_RUNS
-- Percentage of Designer workflow runs that were generated
-- or mapped to Ask Alteryx (Copilot) workflows.
--
-- Formula:
-- Copilot Mapped Workflow Runs / Total Eligible Workflow Runs
--
-- Returned as a decimal ratio.
-- Example: 0.1189 represents 11.89%.

    ROUND(COPILOT_PCT_WORKFLOW_RUNS / 100.0, 4) AS COPILOT_PCT_WORKFLOW_RUNS

FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_DESIGNER_WORKFLOW_PCT_AT;;


-- View: COPILOT_7_15_RETENTION_RATE_VIEW
create or replace view COPILOT_7_15_RETENTION_RATE_VIEW(
	TOTAL_USERS COMMENT 'The total count of unique Purchase users eligible for 7-15 day retention analysis.',
	RETURNING_USERS_7_15D COMMENT 'The number of eligible users who returned to use Copilot at least once between Day 7 and Day 15.',
	RETURNING_RATE_PCT COMMENT 'The returning user rate represented as a decimal ratio between 0 and 1.'
) as
-- ============================================================================
-- VIEW: COPILOT_7_15_RETENTION_RATE_VIEW
-- DESCRIPTION: Computes 7-15 day retention rate of Purchase users on Professional/Enterprise
-- accounts who have at least one Copilot chat activity, using the standard metric
-- source COPILOT_ACTIVITY_USAGE_AT.
-- ============================================================================
WITH

-- ============================================
-- USER_ACTIVITY
-- ============================================
-- Captures all Purchase Enterprise/Professional users
-- who have at least one Copilot chat activity.
-- Each record represents a user's activity on a given day.

user_activity AS (
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        CAST(CONV_CREATED_DATE AS DATE) AS activity_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
),

-- ============================================
-- FIRST_USE
-- ============================================
-- Determines the first day each user used Copilot.
-- This date is used as the cohort start date.

first_use AS (
    SELECT
        CREATED_BY_ID,
        MIN(activity_date) AS first_date
    FROM user_activity
    GROUP BY CREATED_BY_ID
),

-- ============================================
-- ELIGIBLE_COHORT
-- ============================================
-- Users whose first Copilot usage occurred at least
-- seven days before today, making them eligible
-- for 7–15 day retention measurement.

eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -7, CURRENT_DATE())
),

-- ============================================
-- RETURNS_7_15
-- ============================================
-- Users who returned to use Copilot between
-- Day 7 and Day 15 after their first usage.

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

-- ============================================
-- METRIC DEFINITIONS
-- ============================================

-- TOTAL_USERS
-- Number of users eligible for 7–15 day retention analysis.
-- These users first used Copilot at least seven days ago.

    (SELECT COUNT(*) FROM eligible_cohort) AS total_users,

-- RETURNING_USERS_7_15D
-- Number of eligible users who returned to use Copilot
-- at least once between Day 7 and Day 15 after first use.

    (SELECT COUNT(*) FROM returns_7_15) AS returning_users_7_15d,

-- RETURNING_RATE_PCT
-- Percentage of eligible users who returned between
-- Day 7 and Day 15 after first using Copilot.
--
-- Formula:
-- Returning Users (7–15 Days) / Total Eligible Users
--
-- Returned as a decimal ratio.
-- Example: 0.2845 = 28.45%

    ROUND(
        ROUND(
            (SELECT COUNT(*) FROM returns_7_15) * 100.0 /
            NULLIF((SELECT COUNT(*) FROM eligible_cohort), 0),
            2
        ) / 100.0,
        4
    ) AS returning_rate_pct;;


-- View: COPILOT_30_60_RETENTION_RATE_VIEW
create or replace view COPILOT_30_60_RETENTION_RATE_VIEW(
	TOTAL_USERS COMMENT 'The total count of unique Purchase users eligible for 30-60 day retention analysis.',
	RETURNING_USERS_30_60D COMMENT 'The number of eligible users who returned to use Copilot at least once between Day 30 and Day 60.',
	RETURNING_RATE_PCT COMMENT 'The returning user rate represented as a decimal ratio between 0 and 1.'
) as
-- ============================================================================
-- VIEW: COPILOT_30_60_RETENTION_RATE_VIEW
-- DESCRIPTION: Computes 30-60 day retention rate of Purchase users on Professional/Enterprise
-- accounts who have at least one Copilot chat activity, using the standard metric
-- source COPILOT_ACTIVITY_USAGE_AT.
-- ============================================================================
WITH

-- ============================================
-- USER_ACTIVITY
-- ============================================
-- Captures Purchase users from Professional or Enterprise accounts
-- who have at least one Copilot chat activity.
-- Each record represents a user's activity on a specific date.

user_activity AS (    
    SELECT
        USER_EMAIL AS CREATED_BY_ID,
        CAST(CONV_CREATED_DATE AS DATE) AS activity_date
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE ACCOUNT_EDITION IN ('Professional','Enterprise')
      AND LICENSE_TYPE = 'Purchase'
      AND CHAT_ID IS NOT NULL
),

-- ============================================
-- FIRST_USE
-- ============================================
-- Identifies the first date each user used Copilot.
-- This date is used as the cohort anchor for retention analysis.

first_use AS (
    SELECT
        CREATED_BY_ID,
        MIN(activity_date) AS first_date
    FROM user_activity
    GROUP BY CREATED_BY_ID
),

-- ============================================
-- ELIGIBLE_COHORT
-- ============================================
-- Users whose first Copilot activity occurred at least 30 days ago.
-- These users have reached the beginning of the 30–60 day return window.

eligible_cohort AS (
    SELECT
        CREATED_BY_ID,
        first_date
    FROM first_use
    WHERE first_date <= DATEADD(day, -30, CURRENT_DATE())
),

-- ============================================
-- RETURNS_30_60
-- ============================================
-- Users who returned to Copilot at least once between
-- Day 30 and Day 60 after their first use.

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

-- ============================================
-- METRIC DEFINITIONS
-- ============================================

-- TOTAL_USERS
-- Number of users eligible for 30–60 day retention analysis.
-- These users first used Copilot at least 30 days ago.

    (SELECT COUNT(*) FROM eligible_cohort) AS total_users,

-- RETURNING_USERS_30_60D
-- Number of eligible users who returned to use Copilot
-- at least once between Day 30 and Day 60 after first use.

    (SELECT COUNT(*) FROM returns_30_60) AS returning_users_30_60d,

-- RETURNING_RATE_PCT
-- Share of eligible users who returned between
-- Day 30 and Day 60 after first using Copilot.
--
-- Formula:
-- Returning Users (30–60 Days) / Total Eligible Users
--
-- Returned as a decimal ratio.
-- Example: 0.1845 represents 18.45%.

    ROUND(
        ROUND(
            (SELECT COUNT(*) FROM returns_30_60) * 100.0 /
            NULLIF((SELECT COUNT(*) FROM eligible_cohort), 0),
            2
        ) / 100.0,
        4
    ) AS returning_rate_pct;;


-- View: COPILOT_USERS_ADOPTION_RATE_VIEW
create or replace view COPILOT_USERS_ADOPTION_RATE_VIEW(
	ACTIVE_USERS COMMENT 'Distinct Purchase AACP users with at least one Copilot chat.',
	ELIGIBLE_USERS COMMENT 'Distinct users satisfying all Copilot eligibility criteria.',
	ADOPTION_PERCENTAGE COMMENT 'Percentage of eligible users who actively used Copilot (Active Users / Eligible Users).'
) as
WITH numerator AS (
    SELECT
        COUNT(DISTINCT USER_ID_RAW) AS num
    FROM DISCOVERY_PRODUCT_MANAGEMENT.METRIC_STORE.COPILOT_ACTIVITY_USAGE_AT
    WHERE LICENSE_TYPE = 'Purchase'
      AND USER_TYPE = 'aacp'
      AND USER_ID_RAW IS NOT NULL
      AND USER_EMAIL IS NOT NULL
      AND CHAT_ID IS NOT NULL
),
denominator AS (
    SELECT
        COUNT(DISTINCT USER_ID_RAW) AS denom
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
)
SELECT
    numerator.num AS active_users,
    denominator.denom AS eligible_users,
    ROUND(
        ROUND(
            100.0 * numerator.num / NULLIF(denominator.denom, 0),
            2
        ) / 100.0,
        4
    ) AS adoption_percentage
FROM numerator,
     denominator;


-- ----------------------------------------------------------------------------
-- 6. View: COPILOT_ACCOUNTS_ADOPTION_RATE.VIEW
-- ----------------------------------------------------------------------------;

