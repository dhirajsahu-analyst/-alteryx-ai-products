import unittest
from pathlib import Path
from engine.compiler.compiler import CatalogCompiler
from engine.lineage.lineage import LineageEngine

class TestLineageEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Compile a test catalog database
        cls.compiler = CatalogCompiler(output_dir=".telemetryiq_lineage_test")
        cls.compiler.compile()
        cls.engine = LineageEngine(".telemetryiq_lineage_test/catalog.db")

    @classmethod
    def tearDownClass(cls):
        # Clean up database
        test_db = Path(".telemetryiq_lineage_test/catalog.db")
        if test_db.exists():
            test_db.unlink()
        test_manifest = Path(".telemetryiq_lineage_test/build_manifest.json")
        if test_manifest.exists():
            test_manifest.unlink()
        test_dir = Path(".telemetryiq_lineage_test")
        if test_dir.exists():
            test_dir.rmdir()

    def test_lineage_is_available(self):
        self.assertTrue(self.engine.is_available())

    def test_get_upstream_lineage(self):
        result = self.engine.get_upstream_lineage("alteryx_one_activated_full_users")
        self.assertIsNotNone(result)
        self.assertEqual(result["asset_id"], "alteryx_one_activated_full_users")
        self.assertEqual(result["product"], "alteryx_one")
        # Direct sources list should match the YAML definition's source field
        self.assertIn("ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT", result["direct_sources"])

    def test_get_downstream_impact_table(self):
        result = self.engine.get_downstream_impact("PLANS_MONTHLY_ACCOUNT_AT")
        self.assertIsNotNone(result)
        self.assertEqual(result["target_asset"], "PLANS_MONTHLY_ACCOUNT_AT")
        
        # Verify that it finds the affected relationship we created
        self.assertGreater(len(result["affected_relationships"]), 0)
        rel = result["affected_relationships"][0]
        self.assertEqual(rel["relationship_id"], "plans_to_alteryx_one_billing_account")

if __name__ == "__main__":
    unittest.main()
