"""
Core module: Load metrics from YAML files and validate structure.
Provides the foundation for the metric system - loads all 274 metrics.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricDefinition:
    """Represents a single metric with all its properties."""
    id: str
    name: str
    description: str
    product: str
    category: str
    status: str
    freshness: str
    grain: str
    definition: Dict  # {business, technical}
    source: str
    tables: List[str]
    sql_template: str
    tags: List[str]
    maintainer: str
    last_updated: str
    version: str


class MetricsLoader:
    """Load and parse all metrics from YAML files."""

    def __init__(self, metrics_root: Path):
        """
        Initialize loader with root path to metrics directory.

        Args:
            metrics_root: Path to metrics folder containing product subdirectories
        """
        self.metrics_root = Path(metrics_root)
        self.metrics: Dict[str, MetricDefinition] = {}

    def load_all_metrics(self) -> Dict[str, MetricDefinition]:
        """
        Load all metrics from all products.

        Returns:
            Dictionary mapping metric_id -> MetricDefinition
        """
        if not self.metrics_root.exists():
            raise FileNotFoundError(f"Metrics root not found: {self.metrics_root}")

        # Discover all product directories
        for product_dir in self.metrics_root.iterdir():
            if not product_dir.is_dir() or product_dir.name.startswith('.'):
                continue

            metrics_path = product_dir / 'metrics'
            if not metrics_path.exists():
                logger.warning(f"No metrics folder found in {product_dir.name}")
                continue

            # Load all YAML files in this product
            yaml_files = list(metrics_path.glob('*.yaml'))
            logger.info(f"Found {len(yaml_files)} metrics in {product_dir.name}")

            for yaml_file in yaml_files:
                try:
                    metric = self._load_metric_file(yaml_file)
                    self.metrics[metric.id] = metric
                except Exception as e:
                    logger.error(f"Failed to load {yaml_file}: {e}")

        logger.info(f"Successfully loaded {len(self.metrics)} metrics")
        return self.metrics

    def _load_metric_file(self, file_path: Path) -> MetricDefinition:
        """
        Load a single metric YAML file.

        Args:
            file_path: Path to .yaml file

        Returns:
            Validated MetricDefinition

        Raises:
            ValueError: If required fields are missing
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required_fields = [
            'id', 'name', 'description', 'product', 'category',
            'definition', 'sql_template', 'tags'
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")

        return MetricDefinition(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            product=data['product'],
            category=data['category'],
            status=data.get('status', 'active'),
            freshness=data.get('freshness', 'daily'),
            grain=data.get('grain', 'point_in_time'),
            definition=data['definition'],
            source=data.get('source', ''),
            tables=data.get('tables', []),
            sql_template=data['sql_template'],
            tags=data.get('tags', []),
            maintainer=data.get('maintainer', 'unknown'),
            last_updated=data.get('last_updated', ''),
            version=data.get('version', '1.0')
        )

    def get_metric(self, metric_id: str) -> Optional[MetricDefinition]:
        """Get a metric by ID."""
        return self.metrics.get(metric_id)

    def get_by_product(self, product: str) -> List[MetricDefinition]:
        """Get all metrics for a product."""
        return [m for m in self.metrics.values() if m.product == product]

    def get_by_category(self, category: str) -> List[MetricDefinition]:
        """Get all metrics in a category."""
        return [m for m in self.metrics.values() if m.category == category]

    def get_by_tags(self, tags: List[str]) -> List[MetricDefinition]:
        """Get metrics that have ANY of the given tags."""
        return [m for m in self.metrics.values() if any(t in m.tags for t in tags)]

    def list_all_products(self) -> List[str]:
        """Get all unique products."""
        return sorted(set(m.product for m in self.metrics.values()))

    def list_all_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(set(m.category for m in self.metrics.values()))

    def list_all_tags(self) -> List[str]:
        """Get all unique tags across all metrics."""
        tags = set()
        for m in self.metrics.values():
            tags.update(m.tags)
        return sorted(tags)
