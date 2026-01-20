"""CLI for label generation."""

import json
from pathlib import Path

import typer

from src.config import OUTPUT_DIR
from src.label_renderer import generate_label, load_sku_data
from src.importers.shopify import import_shopify_csv
from src.importers.shopify_api import import_shopify_api

app = typer.Typer(help="Alliance Chemical Label Generator")


@app.command()
def generate(
    sku: str = typer.Argument(..., help="SKU code (e.g., AC-IPA-99-55)"),
    lot: str = typer.Option("TEST-001", "--lot", "-l", help="Lot number"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
    style: str = typer.Option(
        "organic", "--style", "-s", help="Label style: 'standard', 'scientific', or 'organic'"
    ),
):
    """Generate a label PDF for the given SKU."""
    try:
        output_dir = output or OUTPUT_DIR

        if style == "scientific":
            from src.label_renderer_scientific import generate_scientific_label

            output_path = generate_scientific_label(sku, lot, output_dir)
        elif style == "organic":
            from src.label_renderer_organic import generate_organic_label

            output_path = generate_organic_label(sku, lot, output_dir)
        else:
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


@app.command("import-shopify")
def import_shopify(
    csv_path: Path = typer.Argument(..., help="Shopify product export CSV"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory for SKU JSON"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing JSON files"),
    allow_missing: bool = typer.Option(
        False,
        "--allow-missing",
        help="Write records even if required fields are missing",
    ),
    report: Path = typer.Option(None, "--report", help="Write a JSON report of skipped rows"),
):
    """Import Shopify products into SKU JSON stubs."""
    try:
        created, skipped = import_shopify_csv(
            csv_path=csv_path,
            output_dir=output,
            overwrite=overwrite,
            allow_missing=allow_missing,
        )
        typer.echo(f"✓ Imported {created} SKU records")
        if skipped:
            typer.echo(f"⚠ Skipped {len(skipped)} rows")
        if report:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(
                json.dumps(skipped, indent=2, ensure_ascii=True) + "\n",
                encoding="utf-8",
            )
            typer.echo(f"Report written to: {report}")
    except Exception as e:
        typer.echo(f"✗ Error importing Shopify CSV: {e}", err=True)
        raise typer.Exit(1)


@app.command("import-shopify-api")
def import_shopify_api_command(
    store: str = typer.Option(None, "--store", help="Shopify store domain"),
    api_version: str = typer.Option(None, "--api-version", help="Shopify API version"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory for SKU JSON"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing JSON files"),
    allow_missing: bool = typer.Option(
        False,
        "--allow-missing",
        help="Write records even if required fields are missing",
    ),
    report: Path = typer.Option(None, "--report", help="Write a JSON report of skipped rows"),
):
    """Import Shopify products via API into SKU JSON stubs."""
    try:
        created, skipped = import_shopify_api(
            store=store,
            api_version=api_version,
            output_dir=output,
            overwrite=overwrite,
            allow_missing=allow_missing,
        )
        typer.echo(f"✓ Imported {created} SKU records")
        if skipped:
            typer.echo(f"⚠ Skipped {len(skipped)} rows")
        if report:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(
                json.dumps(skipped, indent=2, ensure_ascii=True) + "\n",
                encoding="utf-8",
            )
            typer.echo(f"Report written to: {report}")
    except Exception as e:
        typer.echo(f"✗ Error importing Shopify API: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
