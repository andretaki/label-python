"""CLI for label generation."""

import typer
from pathlib import Path

from src.config import OUTPUT_DIR
from src.label_renderer import generate_label, load_sku_data

app = typer.Typer(help="Alliance Chemical Label Generator")


@app.command()
def generate(
    sku: str = typer.Argument(..., help="SKU code (e.g., AC-IPA-99-55)"),
    lot: str = typer.Option("TEST-001", "--lot", "-l", help="Lot number"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Generate a label PDF for the given SKU."""
    try:
        output_dir = output or OUTPUT_DIR
        output_path = generate_label(sku, lot, output_dir)
        typer.echo(f"✓ Label generated: {output_path}")
    except FileNotFoundError as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"✗ Error generating label: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def info(
    sku: str = typer.Argument(..., help="SKU code to show info for"),
):
    """Show information about a SKU."""
    try:
        data = load_sku_data(sku)
        typer.echo(f"SKU: {data.sku}")
        typer.echo(f"Product: {data.product_name}")
        typer.echo(f"Grade: {data.grade_or_concentration or 'N/A'}")
        typer.echo(f"Package: {data.package_type.value}")
        typer.echo(f"HazCom: {'Yes' if data.hazcom_applicable else 'No'}")
        if data.hazcom_applicable:
            typer.echo(f"  Pictograms: {', '.join(p.value for p in data.ghs_pictograms)}")
            typer.echo(f"  Signal: {data.signal_word.value if data.signal_word else 'N/A'}")
        typer.echo(f"DOT: {'Yes' if data.dot_regulated else 'No'}")
        if data.dot_regulated:
            typer.echo(f"  UN#: {data.un_number}")
    except FileNotFoundError as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def batch(
    skus: str = typer.Argument(..., help="Comma-separated SKU codes"),
    lot_prefix: str = typer.Option("BATCH", "--lot-prefix", "-p", help="Lot number prefix"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Generate labels for multiple SKUs."""
    sku_list = [s.strip() for s in skus.split(",")]
    output_dir = output or OUTPUT_DIR

    success = 0
    failed = 0

    for i, sku in enumerate(sku_list, 1):
        lot = f"{lot_prefix}-{i:03d}"
        try:
            output_path = generate_label(sku, lot, output_dir)
            typer.echo(f"✓ {sku}: {output_path}")
            success += 1
        except Exception as e:
            typer.echo(f"✗ {sku}: {e}", err=True)
            failed += 1

    typer.echo(f"\nGenerated {success} labels, {failed} failed")


if __name__ == "__main__":
    app()
