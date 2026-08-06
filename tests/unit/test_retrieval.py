import unittest
import sqlite3
from pathlib import Path
from engine.compiler.compiler import CatalogCompiler
from engine.retrieval.retriever import MetadataRetriever

class TestMetadataRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Compile a test catalog database
        cls.compiler = CatalogCompiler(output_dir=".telemetryiq_retrieval_test")
        cls.compiler.compile()
        cls.retriever = MetadataRetriever(".telemetryiq_retrieval_test/catalog.db")

    @classmethod
    def tearDownClass(cls):
        # Clean up database
        test_db = Path(".telemetryiq_retrieval_test/catalog.db")
        if test_db.exists():
            test_db.unlink()
        test_manifest = Path(".telemetryiq_retrieval_test/build_manifest.json")
        if test_manifest.exists():
            test_manifest.unlink()
        test_dir = Path(".telemetryiq_retrieval_test")
        if test_dir.exists():
            test_dir.rmdir()

    def test_retriever_is_available(self):
        self.assertTrue(self.retriever.is_available())

    def test_load_metric(self):
        metric = self.retriever.load_metric("alteryx_one_activated_full_users")
        self.assertIsNotNone(metric)
        self.assertEqual(metric["id"], "alteryx_one_activated_full_users")
        self.assertEqual(metric["product"], "alteryx_one")

    def test_list_metrics(self):
        metrics = self.retriever.list_metrics("alteryx_one")
        self.assertGreater(len(metrics), 0)
        for m in metrics:
            self.assertEqual(m["product"], "alteryx_one")

    def test_search_relevance_ranking(self):
        # Search for 'engagement'
        results = self.retriever.search_metrics("engagement")
        self.assertGreater(len(results), 0)
        
        # Exact/highly-weighted matches on ID or Name should appear before weak matches
        first_metric = results[0]
        # Let's check that the first metric is indeed highly relevant (ID contains 'engagement')
        self.assertTrue("engagement" in first_metric["id"] or "engagement" in first_metric["name"].lower())

    def test_get_all_products(self):
        products = self.retriever.get_all_products()
        self.assertGreater(len(products), 0)
        
        # Verify that alteryx_one has correct properties mapped for backwards compatibility
        alteryx_one = next((p for p in products if p["product_id"] == "alteryx_one"), None)
        self.assertIsNotNone(alteryx_one)
        self.assertEqual(alteryx_one["product_name"], "alteryx_one")
        self.assertEqual(alteryx_one["full_name"], "Alteryx One")
        self.assertGreater(alteryx_one["metric_count"], 0)

if __name__ == "__main__":
    unittest.main()
