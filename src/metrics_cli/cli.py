"""
Metrics CLI with Claude AI Integration
Commands: list, get, search, ask, execute, validate, explain, export, stats
Runs completely offline except for Snowflake execution
"""

import typer
import json
import os
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from anthropic import Anthropic

from metrics_loader import MetricsLoader
from metrics_validator import MetricsValidator

# Initialize Typer app
app = typer.Typer(
    name="metrics",
    help="Alteryx Metrics CLI - Query metrics with AI, execute SQL, discover insights",
    no_args_is_help=True
)

console = Console()

# Global state
_loader = None
_metrics = None
_claude_client = None


def get_metrics():
    """Lazy load metrics on first access."""
    global _loader, _metrics
    if _metrics is None:
        metrics_root = Path(__file__).parent.parent / 'metrics'
        _loader = MetricsLoader(metrics_root)
        _metrics = _loader.load_all_metrics()
    return _metrics


def get_claude_client():
    """Get Claude client with API key from environment."""
    global _claude_client
    if _claude_client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            console.print(
                "⚠️  ANTHROPIC_API_KEY not set. Set it to use 'metrics ask' command.",
                style="yellow"
            )
            return None
        _claude_client = Anthropic(api_key=api_key)
    return _claude_client


@app.command()
def list_metrics(
    product: Optional[str] = typer.Option(None, help="Filter by product"),
    category: Optional[str] = typer.Option(None, help="Filter by category"),
    tags: Optional[str] = typer.Option(None, help="Filter by tags (comma-separated)"),
    status: Optional[str] = typer.Option("active", help="Filter by status"),
    format: str = typer.Option("table", help="Output format (table, json, csv)"),
):
    """List all metrics with optional filters."""
    metrics = get_metrics()

    # Apply filters
    filtered = list(metrics.values())

    if product:
        filtered = [m for m in filtered if m.product == product]
    if category:
        filtered = [m for m in filtered if m.category == category]
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        filtered = [m for m in filtered if any(t in m.tags for t in tag_list)]
    if status:
        filtered = [m for m in filtered if m.status == status]

    filtered.sort(key=lambda m: (m.product, m.category, m.name))

    if format == "json":
        data = [
            {
                "id": m.id,
                "name": m.name,
                "product": m.product,
                "category": m.category,
                "tags": m.tags,
            }
            for m in filtered
        ]
        console.print_json(data=data)

    elif format == "csv":
        console.print("id,name,product,category,tags")
        for m in filtered:
            tags_str = ";".join(m.tags)
            console.print(f"{m.id},{m.name},{m.product},{m.category},{tags_str}")

    else:  # table
        table = Table(title=f"Metrics ({len(filtered)} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Product", style="green")
        table.add_column("Category", style="yellow")

        for m in filtered[:50]:  # Show first 50
            table.add_row(m.id, m.name[:40], m.product, m.category)

        console.print(table)

    console.print(f"\n✅ Found {len(filtered)} metrics")


@app.command()
def get(
    metric_id: str = typer.Argument(..., help="Metric ID"),
    format: str = typer.Option("table", help="Output format (table, json, yaml)"),
):
    """Get details of a specific metric."""
    metrics = get_metrics()

    if metric_id not in metrics:
        console.print(f"❌ Metric not found: {metric_id}", style="red")
        raise typer.Exit(1)

    metric = metrics[metric_id]

    if format == "json":
        data = {
            "id": metric.id,
            "name": metric.name,
            "description": metric.description,
            "product": metric.product,
            "category": metric.category,
            "definition": metric.definition,
            "sql_template": metric.sql_template,
            "tags": metric.tags,
        }
        console.print_json(data=data)

    elif format == "yaml":
        console.print(f"id: {metric.id}")
        console.print(f"name: {metric.name}")
        console.print(f"description: {metric.description}")
        console.print(f"product: {metric.product}")
        console.print(f"category: {metric.category}")
        console.print(f"tags: {metric.tags}")
        console.print(f"\nsql_template: |")
        for line in metric.sql_template.split('\n'):
            console.print(f"  {line}")

    else:  # table
        table = Table(title=metric.name)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", metric.id)
        table.add_row("Product", metric.product)
        table.add_row("Category", metric.category)
        table.add_row("Description", metric.description[:60])
        table.add_row("Tags", ", ".join(metric.tags))
        table.add_row("Freshness", metric.freshness)

        console.print(table)
        console.print(f"\n📝 SQL Query:\n")
        console.print(metric.sql_template, style="dim")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, help="Max results"),
):
    """Search metrics by keyword."""
    metrics = get_metrics()

    query_lower = query.lower()
    results = []

    for metric in metrics.values():
        score = 0
        if query_lower in metric.id:
            score += 10
        if query_lower in metric.name.lower():
            score += 8
        if query_lower in metric.description.lower():
            score += 5
        if any(query_lower in tag for tag in metric.tags):
            score += 7

        if score > 0:
            results.append((metric, score))

    results.sort(key=lambda x: x[1], reverse=True)
    results = results[:limit]

    if not results:
        console.print(f"❌ No metrics found for: {query}", style="yellow")
        return

    table = Table(title=f"Search Results for '{query}'")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Match", style="yellow")

    for metric, score in results:
        table.add_row(metric.id, metric.name[:40], f"{score} pts")

    console.print(table)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Natural language question about metrics"),
    limit: int = typer.Option(5, help="Max results to return"),
):
    """Find metrics using natural language (powered by Claude)."""
    metrics = get_metrics()
    client = get_claude_client()

    if not client:
        console.print("❌ Claude API key not configured. Set ANTHROPIC_API_KEY.", style="red")
        raise typer.Exit(1)

    # Build metric index for Claude
    metric_names = "\n".join([
        f"- {m.id}: {m.name} (product: {m.product}, tags: {', '.join(m.tags)})"
        for m in list(metrics.values())[:100]  # Send first 100 for context
    ])

    console.print("🤖 Searching with Claude...", style="blue")

    try:
        response = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=500,
            system=f"""You are a metrics discovery assistant for Alteryx.

Available metrics (sample):
{metric_names}

User question: "{question}"

Return ONLY a JSON array of metric IDs that answer this question.
Format: ["metric_id_1", "metric_id_2", ...]
Be concise. Return at most {limit} results.""",
            messages=[{"role": "user", "content": question}]
        )

        # Parse response
        response_text = response.content[0].text
        # Extract JSON from response
        import json as json_lib
        metric_ids = json_lib.loads(response_text)

    except Exception as e:
        console.print(f"❌ Claude error: {e}", style="red")
        raise typer.Exit(1)

    if not metric_ids:
        console.print(f"❌ Claude found no matching metrics for: {question}", style="yellow")
        return

    # Show results
    table = Table(title=f"Claude found {len(metric_ids)} relevant metrics")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Product", style="green")
    table.add_column("Category", style="yellow")

    for metric_id in metric_ids:
        if metric_id in metrics:
            m = metrics[metric_id]
            table.add_row(m.id, m.name[:40], m.product, m.category)

    console.print(table)
    console.print(f"\n✅ Found {len(metric_ids)} relevant metrics")
    console.print("\nTip: Use 'metrics explain <id>' to understand a metric")


@app.command()
def validate():
    """Validate all metrics for correctness."""
    metrics = get_metrics()
    validator = MetricsValidator()

    total, errors, warnings = validator.validate_all(metrics)

    if errors == 0:
        raise typer.Exit(0)
    else:
        raise typer.Exit(1)


@app.command()
def explain(
    metric_id: str = typer.Argument(..., help="Metric ID to explain"),
):
    """Explain what a metric measures in plain English."""
    metrics = get_metrics()

    if metric_id not in metrics:
        console.print(f"❌ Metric not found: {metric_id}", style="red")
        raise typer.Exit(1)

    metric = metrics[metric_id]

    console.print(f"\n📊 {metric.name}\n", style="bold magenta")

    console.print("[bold]Business Definition:[/bold]")
    if isinstance(metric.definition, dict):
        console.print(metric.definition.get('business', 'N/A'))

    console.print("\n[bold]How It's Calculated:[/bold]")
    if isinstance(metric.definition, dict):
        console.print(metric.definition.get('technical', 'N/A'))

    console.print("\n[bold]Related Metrics:[/bold]")
    console.print(f"Category: {metric.category}")
    console.print(f"Tags: {', '.join(metric.tags)}")

    console.print("\n[bold]Details:[/bold]")
    console.print(f"Product: {metric.product}")
    console.print(f"Freshness: {metric.freshness}")
    console.print(f"Last Updated: {metric.last_updated}\n")


@app.command()
def export(
    format: str = typer.Option("json", help="Export format (json, csv, markdown)"),
    output: Optional[str] = typer.Option(None, help="Output file path"),
    product: Optional[str] = typer.Option(None, help="Filter by product"),
):
    """Export metrics catalog."""
    metrics = get_metrics()

    if product:
        metrics = {k: v for k, v in metrics.items() if v.product == product}

    if format == "json":
        data = [
            {
                "id": m.id,
                "name": m.name,
                "product": m.product,
                "category": m.category,
                "tags": m.tags,
            }
            for m in metrics.values()
        ]
        output_str = json.dumps(data, indent=2)

    elif format == "csv":
        lines = ["id,name,product,category"]
        for m in metrics.values():
            lines.append(f'"{m.id}","{m.name}","{m.product}","{m.category}"')
        output_str = "\n".join(lines)

    elif format == "markdown":
        lines = ["# Metrics Catalog\n"]
        by_product = {}
        for m in metrics.values():
            if m.product not in by_product:
                by_product[m.product] = []
            by_product[m.product].append(m)

        for product in sorted(by_product.keys()):
            lines.append(f"## {product}\n")
            for m in sorted(by_product[product], key=lambda x: x.id):
                lines.append(f"- **{m.id}**: {m.name}")
            lines.append("")

        output_str = "\n".join(lines)

    if output:
        Path(output).write_text(output_str)
        console.print(f"✅ Exported to {output}", style="green")
    else:
        console.print(output_str)


@app.command()
def stats():
    """Show system statistics."""
    metrics = get_metrics()

    products = set()
    categories = set()
    tags = set()

    for m in metrics.values():
        products.add(m.product)
        categories.add(m.category)
        tags.update(m.tags)

    console.print("\n[bold]Metrics System Statistics[/bold]\n")
    console.print(f"Total Metrics:     {len(metrics)}")
    console.print(f"Products:          {len(products)}")
    console.print(f"Categories:        {len(categories)}")
    console.print(f"Unique Tags:       {len(tags)}\n")

    console.print("[bold]By Product:[/bold]")
    for product in sorted(products):
        count = len([m for m in metrics.values() if m.product == product])
        console.print(f"  {product:20} : {count:3d}")

    console.print("\n[bold]By Category:[/bold]")
    for category in sorted(categories):
        count = len([m for m in metrics.values() if m.category == category])
        console.print(f"  {category:20} : {count:3d}\n")


if __name__ == "__main__":
    app()
