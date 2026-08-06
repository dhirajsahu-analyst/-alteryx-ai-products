import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from engine.metric_composer import MetricComposer
from engine.error_handler import CompositionError

class TestQueryCompositionSafety(unittest.TestCase):
    def setUp(self):
        # Patch loader, connector, and graph in MetricComposer to isolate tests
        self.loader_patcher = patch('engine.metric_composer.get_metric_loader')
        self.connector_patcher = patch('engine.metric_composer.get_snowflake_connector')
        self.graph_patcher = patch('engine.metric_composer.get_semantic_graph')
        
        self.mock_loader = self.loader_patcher.start()().load_metric
        self.mock_connector = self.connector_patcher.start()().execute_query
        self.mock_graph = self.graph_patcher.start()()
        
        self.composer = MetricComposer()

    def tearDown(self):
        self.loader_patcher.stop()
        self.connector_patcher.stop()
        self.graph_patcher.stop()

    def test_compose_from_base_metrics_compatible(self):
        # Setup mock metric definitions
        metric_a = {
            "id": "metric_a",
            "sql_template": "SELECT * FROM PLANS_MONTHLY_ACCOUNT_AT",
            "source": "PLANS_MONTHLY_ACCOUNT_AT"
        }
        metric_b = {
            "id": "metric_b",
            "sql_template": "SELECT * FROM ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT",
            "source": "ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT"
        }
        
        # Loader mock return values
        self.mock_loader.side_effect = lambda m_id, product=None: {
            "metric_a": metric_a,
            "metric_b": metric_b
        }.get(m_id)
        
        # Connector executing mock dataframes
        df_a = pd.DataFrame({"BILLING_ACCOUNT_ID": [1, 2], "VAL_A": [10, 20]})
        df_b = pd.DataFrame({"BILLING_ACCOUNT_ID": [1, 2], "VAL_B": [100, 200]})
        self.mock_connector.side_effect = lambda q, filt: {
            "SELECT * FROM PLANS_MONTHLY_ACCOUNT_AT": df_a,
            "SELECT * FROM ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT": df_b
        }.get(q)
        
        # Graph returns join approval
        self.mock_graph.check_join_compatibility.return_value = (True, "Approved join contract")
        
        # Act
        result = self.composer._compose_from_base_metrics(
            base_metric_ids=["metric_a", "metric_b"],
            join_rule={"join_on": "BILLING_ACCOUNT_ID", "join_type": "inner"},
            filters=None
        )
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertIn("VAL_A", result.columns)
        self.assertIn("VAL_B", result.columns)
        self.mock_graph.check_join_compatibility.assert_called_once_with(
            "PLANS_MONTHLY_ACCOUNT_AT",
            "ALTERYX_MONTHLY_ACCOUNT_ONBOARDING_ADAPTION_USAGE_AT"
        )

    def test_compose_from_base_metrics_incompatible_blocks_join(self):
        # Setup mock metrics from incompatible models
        metric_a = {
            "id": "metric_a",
            "sql_template": "SELECT * FROM PLANS_MONTHLY_ACCOUNT_AT",
            "source": "PLANS_MONTHLY_ACCOUNT_AT"
        }
        metric_c = {
            "id": "metric_c",
            "sql_template": "SELECT * FROM UNRELATED_MYSTERIOUS_TABLE",
            "source": "UNRELATED_MYSTERIOUS_TABLE"
        }
        
        # Loader mock return values
        self.mock_loader.side_effect = lambda m_id, product=None: {
            "metric_a": metric_a,
            "metric_c": metric_c
        }.get(m_id)
        
        # Connector mock execute dataframes
        df_a = pd.DataFrame({"BILLING_ACCOUNT_ID": [1, 2], "VAL_A": [10, 20]})
        df_c = pd.DataFrame({"BILLING_ACCOUNT_ID": [1, 2], "VAL_C": [100, 200]})
        self.mock_connector.side_effect = lambda q, filt: {
            "SELECT * FROM PLANS_MONTHLY_ACCOUNT_AT": df_a,
            "SELECT * FROM UNRELATED_MYSTERIOUS_TABLE": df_c
        }.get(q)
        
        # Graph returns rejection block
        self.mock_graph.check_join_compatibility.return_value = (False, "No join contract registered")
        
        # Act & Assert
        with self.assertRaises(CompositionError) as ctx:
            self.composer._compose_from_base_metrics(
                base_metric_ids=["metric_a", "metric_c"],
                join_rule={"join_on": "BILLING_ACCOUNT_ID", "join_type": "inner"},
                filters=None
            )
            
        self.assertIn("Join blocked by semantic governance", ctx.exception.reason)
        self.mock_graph.check_join_compatibility.assert_called_once_with(
            "PLANS_MONTHLY_ACCOUNT_AT",
            "UNRELATED_MYSTERIOUS_TABLE"
        )

if __name__ == "__main__":
    unittest.main()
