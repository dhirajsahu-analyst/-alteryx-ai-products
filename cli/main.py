"""Main CLI entry point"""

import typer
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
load_dotenv()

from engine.metric_engine import MetricsEngine
from engine.error_handler import ErrorFormatter, MetricNotFoundError, CompositionError
from engine.compiler.compiler import get_catalog_compiler
from engine.lineage.lineage import get_lineage_engine
from engine.observability.doctor import get_telemetry_doctor
import os

app = typer.Typer(
    name="metrics",
    help="Alteryx Metrics CLI - Query metrics from Snowflake",
    no_args_is_help=True
)

console = Console()
engine = MetricsEngine()

# Get current user
def get_user():
    return os.getenv("USER", "anonymous")

@app.command()
def get(
    metric_id: str = typer.Argument(..., help="Metric identifier (e.g., trial_signups_total)"),
    product: Optional[str] = typer.Option(None, "--product", "-p", help="Product name"),
    format_type: str = typer.Option("table", "--format", "-f", help="Output format (table, json, csv)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Save to file"),
):
    """Get metric data from Snowflake"""
    
    try:
        console.print(f"[cyan]Fetching metric: {metric_id}...[/cyan]")
        
        result = engine.get_metric(metric_id, product, user_id=get_user())
        
        # Format output
        if format_type == "json":
            output = result.to_json(orient="records", indent=2)
        elif format_type == "csv":
            output = result.to_csv(index=False)
        else:  # table
            output = result.to_string(index=False)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            console.print(f"[green]✓ Saved to {output_file}[/green]")
        else:
            console.print(output)
        
        console.print(f"\n[green]✓ Retrieved {len(result)} rows[/green]")
    
    except MetricNotFoundError as e:
        console.print(ErrorFormatter.format_not_found_error(e))
    except CompositionError as e:
        console.print(ErrorFormatter.format_composition_error(e))
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

@app.command()
def search(
    keyword: str = typer.Argument(..., help="Search keyword"),
    product: Optional[str] = typer.Option(None, "--product", "-p", help="Limit to product"),
):
    """Search for metrics"""
    
    try:
        console.print(f"[cyan]Searching for: {keyword}...[/cyan]\n")
        
        results = engine.search_metrics(keyword, product, user_id=get_user())
        
        if not results:
            console.print("[yellow]No metrics found matching your search[/yellow]")
            return
        
        # Display results in table
        from rich.table import Table
        table = Table(title=f"Found {len(results)} metrics")
        
        table.add_column("Metric ID", style="cyan")
        table.add_column("Product", style="magenta")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        
        for metric in results:
            table.add_row(
                metric.get('id', ''),
                metric.get('product', ''),
                metric.get('name', ''),
                metric.get('status', 'unknown')
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

@app.command()
def list(
    product: str = typer.Argument(..., help="Product name"),
):
    """List all metrics in a product"""
    
    try:
        console.print(f"[cyan]Listing metrics for product: {product}...[/cyan]\n")
        
        metrics = engine.list_metrics(product, user_id=get_user())
        
        if not metrics:
            console.print("[yellow]No metrics found for this product[/yellow]")
            return
        
        from rich.table import Table
        table = Table(title=f"{product.upper()} - {len(metrics)} metrics")
        
        table.add_column("Metric ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Category", style="magenta")
        table.add_column("Status", style="yellow")
        
        for metric in sorted(metrics, key=lambda x: x.get('id', '')):
            table.add_row(
                metric.get('id', ''),
                metric.get('name', '')[:40],
                metric.get('category', ''),
                metric.get('status', 'unknown')
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

@app.command()
def describe(
    metric_id: str = typer.Argument(..., help="Metric identifier"),
    product: Optional[str] = typer.Option(None, "--product", "-p", help="Product name"),
):
    """Show detailed metric information"""
    
    try:
        metric_info = engine.get_metric_info(metric_id, product, user_id=get_user())
        
        console.print(f"\n[bold cyan]Metric: {metric_info.get('name', metric_id)}[/bold cyan]")
        console.print(f"[dim]ID: {metric_info.get('id')}[/dim]\n")
        
        # Display key information
        console.print("[bold]Basic Information:[/bold]")
        console.print(f"  Product: {metric_info.get('product', 'N/A')}")
        console.print(f"  Status: {metric_info.get('status', 'N/A')}")
        console.print(f"  Category: {metric_info.get('category', 'N/A')}")
        console.print(f"  Description: {metric_info.get('description', 'N/A')}\n")
        
        # Definition
        if 'definition' in metric_info:
            console.print("[bold]Definition:[/bold]")
            console.print(f"  Business: {metric_info['definition'].get('business', 'N/A')}")
            console.print(f"  Technical: {metric_info['definition'].get('technical', 'N/A')}\n")
        
        # Source
        if 'source' in metric_info:
            console.print("[bold]Source:[/bold]")
            source = metric_info['source']
            if isinstance(source, dict):
                console.print(f"  Database: {source.get('database', 'N/A')}")
                console.print(f"  Schema: {source.get('schema', 'N/A')}")
                
                base_tables = source.get('base_tables', [])
                if base_tables:
                    console.print(f"  Base Tables:")
                    for table in base_tables:
                        console.print(f"    • {table}")
            else:
                console.print(f"  {source}")
            console.print()
        
        # Metadata
        console.print("[bold]Metadata:[/bold]")
        console.print(f"  Aggregation Level: {metric_info.get('aggregation_level', 'N/A')}")
        console.print(f"  Freshness: {metric_info.get('freshness', 'N/A')}")
        console.print(f"  Maintainer: {metric_info.get('maintainer', 'N/A')}")
        console.print(f"  Last Updated: {metric_info.get('last_updated', 'N/A')}\n")
    
    except MetricNotFoundError as e:
        console.print(ErrorFormatter.format_not_found_error(e))
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

@app.command()
def products():
    """List all available products"""
    
    try:
        products_list = engine.get_products()
        
        from rich.table import Table
        table = Table(title="Available Products")
        
        table.add_column("Product", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Metrics", style="yellow")
        table.add_column("Status", style="magenta")
        
        for product in sorted(products_list, key=lambda x: x.get('product_name', '')):
            table.add_row(
                product.get('product_name', ''),
                product.get('full_name', ''),
                str(product.get('metric_count', 0)),
                product.get('status', 'active')
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

@app.command()
def build():
    """Discover, validate, and compile all products and metrics into local SQLite database"""
    console.print("[cyan]Compiling repository telemetry catalog...[/cyan]\n")
    try:
        compiler = get_catalog_compiler()
        success, summary = compiler.compile()
        
        if success:
            console.print("[bold green]✓ Compilation successful![/bold green]")
        else:
            console.print("[bold red]✗ Compilation failed with errors.[/bold red]")
            
        console.print(f"\n[bold]Build Summary:[/bold]")
        console.print(f"  Products Discovered:      {summary['products_discovered']}")
        console.print(f"  Products Compiled:        {summary['products_compiled']}")
        console.print(f"  Metrics Discovered:       {summary['metrics_discovered']}")
        console.print(f"  Metrics Compiled:         {summary['metrics_compiled']}")
        console.print(f"  Relationships Discovered: {summary.get('relationships_discovered', 0)}")
        console.print(f"  Relationships Compiled:   {summary.get('relationships_compiled', 0)}")
        
        if summary['warnings']:
            console.print(f"\n[bold yellow]Warnings ({len(summary['warnings'])}):[/bold yellow]")
            for warn in summary['warnings'][:10]:
                console.print(f"  • {warn}")
            if len(summary['warnings']) > 10:
                console.print(f"  ... and {len(summary['warnings']) - 10} more warnings.")
                
        if summary['errors']:
            console.print(f"\n[bold red]Errors ({len(summary['errors'])}):[/bold red]")
            for err in summary['errors']:
                console.print(f"  • {err}")
                
    except Exception as e:
        console.print(f"[red]✗ Build error: {str(e)}[/red]")

@app.command()
def lineage(asset_id: str = typer.Argument(..., help="Asset or metric ID to trace upstream lineage")):
    """Trace upstream models, tables, and contributors for a given metric"""
    console.print(f"[cyan]Tracing upstream lineage for asset: {asset_id}...[/cyan]\n")
    try:
        engine = get_lineage_engine()
        result = engine.get_upstream_lineage(asset_id)
        if not result:
            console.print(f"[red]✗ Asset [{asset_id}] not found in compiled catalog. Build the catalog first.[/red]")
            return
            
        console.print(f"[bold cyan]Upstream Lineage Map:[/bold cyan]")
        console.print(f"  Asset ID:   {result['asset_id']}")
        console.print(f"  Name:       {result['name']}")
        console.print(f"  Product:    {result['product']}")
        console.print(f"  Asset Type: {result['type']}")
        
        console.print(f"\n[bold green]Direct Source Tables/Models:[/bold green]")
        if result['direct_sources']:
            for src in result['direct_sources']:
                console.print(f"  • {src}")
        else:
            console.print("  • None (Direct Query or unmapped)")
            
        if result['base_metrics']:
            console.print(f"\n[bold yellow]Contributing Base Metrics:[/bold yellow]")
            for base in result['base_metrics']:
                console.print(f"  • {base['asset_id']} ({base['name']}) -> pulls from {base['direct_sources']}")
                
    except Exception as e:
        console.print(f"[red]✗ Lineage tracing error: {str(e)}[/red]")

@app.command()
def impact(asset_id: str = typer.Argument(..., help="Table/Model ID or Metric ID to trace downstream impact")):
    """Analyze downstream impact on metrics and relationships if an asset is modified"""
    console.print(f"[cyan]Analyzing downstream impact for: {asset_id}...[/cyan]\n")
    try:
        engine = get_lineage_engine()
        result = engine.get_downstream_impact(asset_id)
        if not result:
            console.print(f"[red]✗ Asset [{asset_id}] not found in compiled catalog. Build the catalog first.[/red]")
            return
            
        console.print(f"[bold cyan]Impact Analysis Map for [{asset_id}]:[/bold cyan]")
        
        console.print(f"\n[bold red]Affected Metrics ({len(result['affected_metrics'])}):[/bold red]")
        if result['affected_metrics']:
            for m in result['affected_metrics']:
                console.print(f"  • {m['metric_id']} ({m['name']}) [Product: {m['product']}, Status: {m['status']}]")
        else:
            console.print("  • No metrics directly affected.")
            
        console.print(f"\n[bold yellow]Affected Relationships ({len(result['affected_relationships'])}):[/bold yellow]")
        if result['affected_relationships']:
            for rel in result['affected_relationships']:
                console.print(f"  • {rel['relationship_id']} (Joins {rel['left_model']} <-> {rel['right_model']})")
        else:
            console.print("  • No semantic relationships affected.")
                
    except Exception as e:
        console.print(f"[red]✗ Impact analysis error: {str(e)}[/red]")

@app.command()
def doctor():
    """Audit repository configurations and generate production-readiness scorecard"""
    console.print("[cyan]Executing TelemetryIQ Doctor production readiness audit...[/cyan]\n")
    try:
        doctor_engine = get_telemetry_doctor()
        success, report = doctor_engine.run_audit()
        
        # Display overall scorecard
        color = "green" if success else ("yellow" if report["readiness_score"] >= 70.0 else "red")
        console.print(f"[bold {color}]TelemetryIQ Readiness Score: {report['readiness_score']}%[/bold {color}]")
        
        status_text = "READY FOR PRODUCTION" if success else "NEEDS REMEDIATION"
        console.print(f"Status: [bold {color}]{status_text}[/bold {color}]\n")
        
        # Display summary counts
        console.print("[bold cyan]Asset Inventory Summary:[/bold cyan]")
        console.print(f"  Products:      {report['summary']['total_products']}")
        console.print(f"  Metrics:       {report['summary']['total_metrics']}")
        console.print(f"  Relationships: {report['summary']['total_relationships']}")
        console.print(f"  Checks Run:    {report['summary']['passed_checks']}/{report['summary']['total_checks']}")
        
        # Display coverage
        console.print(f"\n[bold cyan]Metadata Quality Coverage:[/bold cyan]")
        console.print(f"  Business Definitions: {report['metric_coverage']['business_definitions']}%")
        console.print(f"  Metric Ownership:     {report['metric_coverage']['owners']}%")
        console.print(f"  Telemetry Grains:     {report['metric_coverage']['grains']}%")
        console.print(f"  Valid SQL Templates:  {report['metric_coverage']['sql_references']}%")
        console.print(f"  Keywords/Tags:        {report['metric_coverage']['tags']}%")
        
        # Display Product maturity breakdown
        console.print(f"\n[bold cyan]Product Domain Maturity Breakdown:[/bold cyan]")
        for p_id, pm in sorted(report["product_maturity"].items()):
            p_color = "green" if pm["score"] >= 80 else ("yellow" if pm["score"] >= 50 else "red")
            console.print(f"  • {p_id:20} Score: [bold {p_color}]{pm['score']}%[/bold {p_color}] ({pm['passed_metrics']}/{pm['metrics_count']} fully-certified metrics)")
            
        if report["critical_risks"]:
            console.print(f"\n[bold red]CRITICAL RISKS ({len(report['critical_risks'])}):[/bold red]")
            for risk in report["critical_risks"]:
                console.print(f"  ✗ {risk}")
                
        if report["high_priority_remediations"]:
            console.print(f"\n[bold yellow]High Priority Remediation Actions ({len(report['high_priority_remediations'])}):[/bold yellow]")
            for rem in report["high_priority_remediations"][:10]:
                console.print(f"  → {rem}")
            if len(report["high_priority_remediations"]) > 10:
                console.print(f"  ... and {len(report['high_priority_remediations']) - 10} more remediation actions.")
                
    except Exception as e:
        console.print(f"[red]✗ Doctor audit failed: {str(e)}[/red]")

@app.command()
def validate(
    product: Optional[str] = typer.Option(None, "--product", "-p", help="Validate specific product"),
):
    """Validate metric definitions and Snowflake availability"""
    
    console.print("[cyan]Validating metrics...[/cyan]\n")
    
    try:
        if product:
            metrics = engine.list_metrics(product)
        else:
            all_metrics = []
            for prod in engine.get_products():
                all_metrics.extend(engine.list_metrics(prod['product_name']))
            metrics = all_metrics
        
        valid_count = 0
        invalid_count = 0
        
        for metric in metrics:
            metric_id = metric.get('id')
            try:
                # Try to get metric (quick validation)
                engine.get_metric_info(metric_id, metric.get('product'))
                valid_count += 1
                console.print(f"[green]✓[/green] {metric_id}")
            except Exception as e:
                invalid_count += 1
                console.print(f"[red]✗[/red] {metric_id}: {str(e)[:60]}")
        
        console.print(f"\n[bold]Validation Summary:[/bold]")
        console.print(f"  ✓ Valid: {valid_count}")
        console.print(f"  ✗ Invalid: {invalid_count}")
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

@app.command()
def audit(
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by user"),
    action: Optional[str] = typer.Option(None, "--action", "-a", help="Filter by action"),
    limit: int = typer.Option(50, "--limit", "-l", help="Number of entries to show"),
):
    """View audit logs"""
    
    try:
        logs = engine.audit_logger.get_logs()
        
        # Apply filters
        if user:
            logs = [log for log in logs if log.get('user_id') == user]
        if action:
            logs = [log for log in logs if log.get('action') == action]
        
        # Sort by timestamp (newest first)
        logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)
        logs = logs[:limit]
        
        from rich.table import Table
        table = Table(title=f"Audit Log ({len(logs)} entries)")
        
        table.add_column("Timestamp", style="dim")
        table.add_column("User", style="cyan")
        table.add_column("Action", style="green")
        table.add_column("Metric", style="magenta")
        table.add_column("Status", style="yellow")
        
        for log in logs:
            table.add_row(
                log.get('timestamp', '')[:19],
                log.get('user_id', ''),
                log.get('action', ''),
                log.get('metric_id', 'N/A'),
                log.get('status', 'unknown')
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")

if __name__ == "__main__":
    app()
