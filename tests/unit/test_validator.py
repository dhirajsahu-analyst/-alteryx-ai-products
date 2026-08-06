import unittest
from engine.catalog.validator import SchemaValidator

class TestSchemaValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SchemaValidator()

    def test_validate_valid_product(self):
        valid_product = {
            "product_id": "alteryx_one",
            "name": "Alteryx One",
            "description": "Adoption and retention telemetry",
            "status": "active",
            "version": "1.0.0",
            "owners": {
                "business": "biz_team@alteryx.com",
                "analytics": "analytics_team@alteryx.com",
                "engineering": "eng_team@alteryx.com"
            },
            "domains": ["activation", "retention"]
        }
        is_valid, err = self.validator.validate_product(valid_product)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_validate_invalid_product(self):
        invalid_product = {
            "product_id": "Alteryx-One-Invalid",  # Upper case and dash not allowed by schema regex
            "name": "Alteryx One",
            "status": "invalid_status",          # Not in enum
            "version": "1.0"                      # Not full semver pattern
        }
        is_valid, err = self.validator.validate_product(invalid_product)
        self.assertFalse(is_valid)
        self.assertIsNotNone(err)
        self.assertIn("product_id", err)
        self.assertIn("status", err)
        self.assertIn("version", err)

    def test_validate_valid_metric(self):
        valid_metric = {
            "id": "plans_engagement_rate",
            "name": "Plans Engagement Rate",
            "description": "Active plans over created plans",
            "product": "plans",
            "status": "active",
            "sql_template": "SELECT * FROM PLANS_FACT_AT"
        }
        is_valid, err = self.validator.validate_metric(valid_metric)
        self.assertTrue(is_valid)
        self.assertIsNone(err)

    def test_validate_invalid_metric(self):
        invalid_metric = {
            "id": "invalid-id-with-dash",
            "name": "Metric with missing fields"
            # missing product, status, sql_template
        }
        is_valid, err = self.validator.validate_metric(invalid_metric)
        self.assertFalse(is_valid)
        self.assertIsNotNone(err)

if __name__ == "__main__":
    unittest.main()
