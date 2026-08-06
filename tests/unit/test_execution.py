import unittest
from engine.snowflake_connector import SnowflakeConnector
from engine.error_handler import SnowflakeError

class TestCertifiedExecutionPath(unittest.TestCase):
    def setUp(self):
        self.connector = SnowflakeConnector(use_sso=False)

    def test_validate_sql_safety_valid_queries(self):
        valid_queries = [
            "SELECT * FROM PLAN_USAGE_AT WHERE STATUS = 'active'",
            "WITH cte AS (SELECT * FROM PLANS) SELECT COUNT(*) FROM cte",
            "select count(*) from plans_fact_at -- count all active rows",
            "/* get plans */ SELECT * FROM PLANS_HEALTH"
        ]
        for query in valid_queries:
            is_safe, err = self.connector.validate_sql_safety(query)
            self.assertTrue(is_safe, f"Query failed safety check: {query}. Error: {err}")
            self.assertIsNone(err)

    def test_validate_sql_safety_invalid_queries(self):
        invalid_queries = [
            "DROP TABLE PLANS",
            "INSERT INTO PLANS (ID, NAME) VALUES (1, 'Test')",
            "DELETE FROM PLANS_FACT_AT WHERE ID = 5",
            "UPDATE PLANS SET STATUS = 'inactive'",
            "ALTER TABLE PLANS ADD COLUMN REVENUE INT",
            "TRUNCATE TABLE PLANS_FACT_AT"
        ]
        for query in invalid_queries:
            is_safe, err = self.connector.validate_sql_safety(query)
            self.assertFalse(is_safe, f"Mutational query bypass: {query}")
            self.assertIsNotNone(err)
            self.assertIn("Disallowed mutational/DDL keyword(s) detected", err)

    def test_validate_sql_safety_false_positives_prevented(self):
        # Disallowed keywords inside string literals or comments should NOT trigger security violations
        safe_queries_with_keywords = [
            "SELECT * FROM PLANS WHERE DESCRIPTION = 'This represents drop and insert operations'",
            "SELECT * FROM PLANS_FACT_AT -- we will update this soon",
            "/* Do not drop table */ SELECT COUNT(*) FROM PLANS_HEALTH",
            "SELECT * FROM PLANS WHERE LOG_MESSAGE = 'Completed insert successfully'"
        ]
        for query in safe_queries_with_keywords:
            is_safe, err = self.connector.validate_sql_safety(query)
            self.assertTrue(is_safe, f"False positive triggered for query: {query}. Error: {err}")
            self.assertIsNone(err)

if __name__ == "__main__":
    unittest.main()
