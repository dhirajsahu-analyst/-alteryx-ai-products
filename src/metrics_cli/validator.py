"""
Core module: Validate metrics YAML structure and SQL syntax.
Ensures 274 metrics are production-ready.
"""

import logging
import re
from typing import List, Dict, Tuple
from metrics_loader import MetricDefinition

logger = logging.getLogger(__name__)


class ValidationError:
    """Represents a single validation error."""

    def __init__(self, metric_id: str, severity: str, message: str):
        self.metric_id = metric_id
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message

    def __str__(self):
        return f"[{self.severity.upper()}] {self.metric_id}: {self.message}"


class MetricsValidator:
    """Validate metrics for correctness and consistency."""

    VALID_CATEGORIES = [
        'funnel', 'adoption', 'engagement', 'retention', 'health',
        'activation', 'rate', 'usage', 'distribution', 'compliance'
    ]

    VALID_TAGS = [
        'funnel', 'funnel-stage', 'adoption', 'adoption-rate',
        'engagement', 'retention', 'cohort-analysis', 'rate-metric',
        'daily-active', 'weekly-active', 'monthly-active',
        'conversion', 'churn', 'activation', 'onboarding'
    ]

    def __init__(self):
        self.errors: List[ValidationError] = []

    def validate_metric(self, metric: MetricDefinition) -> bool:
        """
        Validate a single metric.

        Args:
            metric: MetricDefinition to validate

        Returns:
            True if metric passes all validations
        """
        self.errors = []

        # Required fields
        if not metric.id or not metric.id.strip():
            self._error(metric.id, "ID is empty")
        if not metric.name or not metric.name.strip():
            self._error(metric.id, "Name is empty")
        if not metric.description or not metric.description.strip():
            self._error(metric.id, "Description is empty")
        if not metric.product or not metric.product.strip():
            self._error(metric.id, "Product is empty")
        if not metric.category or not metric.category.strip():
            self._error(metric.id, "Category is empty")
        if not metric.sql_template or not metric.sql_template.strip():
            self._error(metric.id, "SQL template is empty")
        if not metric.tags or len(metric.tags) == 0:
            self._warn(metric.id, "No tags defined")

        # ID format
        if metric.id and not re.match(r'^[a-z0-9_]+$', metric.id):
            self._error(metric.id, f"ID must be lowercase with underscores only: {metric.id}")

        # Category validation
        if metric.category not in self.VALID_CATEGORIES:
            self._warn(metric.id, f"Unknown category: {metric.category}")

        # Tags validation
        for tag in metric.tags:
            if tag not in self.VALID_TAGS:
                self._warn(metric.id, f"Unknown tag: {tag}")

        # SQL validation
        if metric.sql_template:
            self._validate_sql(metric.id, metric.sql_template)

        # Definition validation
        if isinstance(metric.definition, dict):
            if 'business' not in metric.definition:
                self._warn(metric.id, "No business definition provided")
            if 'technical' not in metric.definition:
                self._warn(metric.id, "No technical definition provided")
        else:
            self._error(metric.id, "Definition must be a dictionary")

        # Status check
        if metric.status not in ['active', 'deprecated', 'experimental']:
            self._warn(metric.id, f"Unknown status: {metric.status}")

        return len(self.errors) == 0

    def validate_all(self, metrics: Dict[str, MetricDefinition]) -> Tuple[int, int, int]:
        """
        Validate all metrics.

        Args:
            metrics: Dictionary of metric_id -> MetricDefinition

        Returns:
            Tuple of (total, errors, warnings)
        """
        all_errors = []
        all_warnings = []

        for metric in metrics.values():
            self.errors = []
            self.validate_metric(metric)

            for error in self.errors:
                if error.severity == 'error':
                    all_errors.append(error)
                else:
                    all_warnings.append(error)

        self._print_summary(metrics, all_errors, all_warnings)
        return len(metrics), len(all_errors), len(all_warnings)

    def _validate_sql(self, metric_id: str, sql: str):
        """Validate SQL query syntax (basic checks)."""
        sql_upper = sql.upper()

        # Check for required SQL keywords
        if 'SELECT' not in sql_upper:
            self._error(metric_id, "SQL must contain SELECT")

        # Check for common issues
        if sql.count(';') > 1:
            self._warn(metric_id, "SQL contains multiple statements")

        # Check for CTEs
        if 'WITH' not in sql_upper:
            self._warn(metric_id, "SQL doesn't use CTEs (consider using WITH for clarity)")

        # Check for date functions
        if 'CURRENT_DATE' not in sql_upper and 'NOW()' not in sql_upper:
            self._warn(metric_id, "SQL doesn't reference current date (may be intentional)")

    def _error(self, metric_id: str, message: str):
        """Record an error."""
        self.errors.append(ValidationError(metric_id, 'error', message))

    def _warn(self, metric_id: str, message: str):
        """Record a warning."""
        self.errors.append(ValidationError(metric_id, 'warning', message))

    def _print_summary(self, metrics: Dict, errors: List, warnings: List):
        """Print validation summary."""
        total = len(metrics)
        error_count = len(errors)
        warning_count = len(warnings)

        print("\n" + "=" * 80)
        print("METRICS VALIDATION REPORT")
        print("=" * 80)
        print(f"\nTotal metrics:    {total}")
        print(f"Errors:           {error_count}")
        print(f"Warnings:         {warning_count}")

        if error_count > 0:
            print("\n🔴 ERRORS:")
            for error in errors[:10]:  # Show first 10
                print(f"  {error}")
            if error_count > 10:
                print(f"  ... and {error_count - 10} more")

        if warning_count > 0:
            print("\n⚠️  WARNINGS:")
            for warning in warnings[:10]:  # Show first 10
                print(f"  {warning}")
            if warning_count > 10:
                print(f"  ... and {warning_count - 10} more")

        if error_count == 0 and warning_count == 0:
            print("\n✅ All metrics validated successfully!")

        print("=" * 80 + "\n")
