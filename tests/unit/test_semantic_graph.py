import unittest
from pathlib import Path
from engine.compiler.compiler import CatalogCompiler
from engine.semantic_graph.graph import SemanticGraph

class TestSemanticGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Compile a test catalog database
        cls.compiler = CatalogCompiler(output_dir=".telemetryiq_graph_test")
        cls.compiler.compile()
        cls.graph = SemanticGraph(".telemetryiq_graph_test/catalog.db")

    @classmethod
    def tearDownClass(cls):
        # Clean up database
        test_db = Path(".telemetryiq_graph_test/catalog.db")
        if test_db.exists():
            test_db.unlink()
        test_manifest = Path(".telemetryiq_graph_test/build_manifest.json")
        if test_manifest.exists():
            test_manifest.unlink()
        test_dir = Path(".telemetryiq_graph_test")
        if test_dir.exists():
            test_dir.rmdir()

    def test_graph_is_available(self):
        self.assertTrue(self.graph.is_available())

    def test_get_valid_relationship(self):
        rel = self.graph.get_relationship(
            "PLANS_MONTHLY_ACCOUNT_AT", 
            "ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT"
        )
        self.assertIsNotNone(rel)
        self.assertEqual(rel["relationship_id"], "plans_to_alteryx_one_billing_account")
        
        # Test reverse direction
        rel_reverse = self.graph.get_relationship(
            "ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT",
            "PLANS_MONTHLY_ACCOUNT_AT"
        )
        self.assertIsNotNone(rel_reverse)
        self.assertEqual(rel_reverse["relationship_id"], "plans_to_alteryx_one_billing_account")

    def test_check_join_compatibility_valid(self):
        compatible, msg = self.graph.check_join_compatibility(
            "PLANS_MONTHLY_ACCOUNT_AT",
            "ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT"
        )
        self.assertTrue(compatible)
        self.assertIn("Approved join", msg)

    def test_check_join_compatibility_invalid(self):
        # No relationship registered
        compatible, msg = self.graph.check_join_compatibility(
            "PLANS_MONTHLY_ACCOUNT_AT",
            "UNREGISTERED_DUMMY_TABLE"
        )
        self.assertFalse(compatible)
        self.assertIn("No semantic relationship contract registered", msg)

    def test_check_join_compatibility_many_to_many(self):
        # Inject mock many_to_many relationship
        mock_rel = {
            "relationship_id": "unsafe_many_to_many",
            "left_model": "TABLE_A",
            "right_model": "TABLE_B",
            "left_keys": ["ID"],
            "right_keys": ["ID"],
            "cardinality": "many_to_many",
            "approved_join_type": "inner",
            "certification": "draft"
        }
        self.graph._relationships.append(mock_rel)
        
        compatible, msg = self.graph.check_join_compatibility("TABLE_A", "TABLE_B")
        self.assertFalse(compatible)
        self.assertIn("unsafe many-to-many cardinality", msg)
        
        # Clean up mock injection
        self.graph._relationships.pop()

if __name__ == "__main__":
    unittest.main()
