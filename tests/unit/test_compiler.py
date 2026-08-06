import unittest
import sqlite3
from pathlib import Path
from engine.compiler.compiler import get_catalog_compiler

class TestCatalogCompiler(unittest.TestCase):
    def setUp(self):
        # We will use a temporary output directory to avoid mutating the production cache
        self.compiler = get_catalog_compiler(output_dir=".telemetryiq_test")
        self.compiler.compile()

    def tearDown(self):
        # Clean up test database
        test_db = Path(".telemetryiq_test/catalog.db")
        if test_db.exists():
            test_db.unlink()
        test_manifest = Path(".telemetryiq_test/build_manifest.json")
        if test_manifest.exists():
            test_manifest.unlink()
        test_dir = Path(".telemetryiq_test")
        if test_dir.exists():
            test_dir.rmdir()

    def test_catalog_db_creation(self):
        test_db = Path(".telemetryiq_test/catalog.db")
        self.assertTrue(test_db.exists())

    def test_database_tables_populated(self):
        conn = sqlite3.connect(".telemetryiq_test/catalog.db")
        cursor = conn.cursor()
        
        # Verify products table has rows
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        self.assertGreater(product_count, 0)
        
        # Verify metrics table has rows
        cursor.execute("SELECT COUNT(*) FROM metrics")
        metric_count = cursor.fetchone()[0]
        self.assertGreater(metric_count, 0)
        
        # Verify alteryx_one has been compiled
        cursor.execute("SELECT name, status FROM products WHERE product_id = 'alteryx_one'")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Alteryx One")
        self.assertEqual(row[1], "active")
        
        conn.close()

if __name__ == "__main__":
    unittest.main()
