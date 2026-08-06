import unittest
from pathlib import Path
from engine.compiler.compiler import CatalogCompiler
from engine.observability.doctor import TelemetryIQDoctor

class TestTelemetryIQDoctor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Compile a test catalog database
        cls.compiler = CatalogCompiler(output_dir=".telemetryiq_doctor_test")
        cls.compiler.compile()
        cls.doctor = TelemetryIQDoctor(".telemetryiq_doctor_test/catalog.db")

    @classmethod
    def tearDownClass(cls):
        # Clean up database
        test_db = Path(".telemetryiq_doctor_test/catalog.db")
        if test_db.exists():
            test_db.unlink()
        test_manifest = Path(".telemetryiq_doctor_test/build_manifest.json")
        if test_manifest.exists():
            test_manifest.unlink()
        test_dir = Path(".telemetryiq_doctor_test")
        if test_dir.exists():
            test_dir.rmdir()

    def test_doctor_is_available(self):
        self.assertTrue(self.doctor.is_available())

    def test_doctor_audit_run(self):
        is_ready, report = self.doctor.run_audit()
        
        # We assert that the report contains all structural dimensions
        self.assertIn("readiness_score", report)
        self.assertIn("summary", report)
        self.assertIn("critical_risks", report)
        self.assertIn("high_priority_remediations", report)
        self.assertIn("metric_coverage", report)
        self.assertIn("product_maturity", report)
        
        # Verify basic inventory counts are tracked
        self.assertGreater(report["summary"]["total_products"], 0)
        self.assertGreater(report["summary"]["total_metrics"], 0)
        self.assertGreater(report["summary"]["total_relationships"], 0)
        self.assertGreater(report["summary"]["total_checks"], 0)
        
        # Verify coverage reporting percentages
        self.assertEqual(report["metric_coverage"]["business_definitions"], 100.0)
        self.assertEqual(report["metric_coverage"]["owners"], 100.0)

if __name__ == "__main__":
    unittest.main()
