"""CLI for label generation."""

import json
from pathlib import Path

import typer

from src.config import DATA_DIR, OUTPUT_DIR
from src.label_renderer import generate_label, load_sku_data
from src.importers.shopify import import_shopify_csv
from src.importers.shopify_api import import_shopify_api

app = typer.Typer(help="Alliance Chemical Label Generator")

# Sub-apps for database management
db_app = typer.Typer(help="Chemical database management")
app.add_typer(db_app, name="db")


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


# =============================================================================
# DATABASE MANAGEMENT COMMANDS
# =============================================================================


@db_app.command("sync")
def db_sync(
    sku_dir: Path = typer.Option(None, "--sku-dir", help="SKU stubs directory"),
    chemicals_dir: Path = typer.Option(None, "--chemicals-dir", help="Chemicals database directory"),
    mappings_file: Path = typer.Option(None, "--mappings", help="SKU mappings file"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing complete records"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without writing"),
):
    """Sync Shopify SKU stubs with chemical hazard data.

    This merges product info from Shopify (name, size, UPC) with chemical
    data (GHS, NFPA, DOT) to create complete label records.
    """
    from src.database import (
        load_chemical_database,
        load_sku_mapper,
        sync_shopify_to_labels,
    )

    try:
        chemical_db = load_chemical_database(chemicals_dir)
        sku_mapper = load_sku_mapper(mappings_file)

        typer.echo(f"Loaded {len(chemical_db)} chemicals, {len(sku_mapper)} mappings")

        if dry_run:
            typer.echo("DRY RUN - no files will be written")

        successful, failed = sync_shopify_to_labels(
            sku_dir=sku_dir,
            chemical_db=chemical_db,
            sku_mapper=sku_mapper,
            overwrite=overwrite,
            dry_run=dry_run,
        )

        updated = [r for r in successful if r.was_updated]
        skipped = [r for r in successful if not r.was_updated]

        typer.echo(f"\n✓ Synced {len(updated)} SKUs")
        if skipped:
            typer.echo(f"  Skipped {len(skipped)} already complete")
        if failed:
            typer.echo(f"✗ Failed {len(failed)} SKUs:")
            for result in failed[:10]:
                typer.echo(f"  - {result.sku}: {result.error}")
            if len(failed) > 10:
                typer.echo(f"  ... and {len(failed) - 10} more")

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


@db_app.command("status")
def db_status(
    sku_dir: Path = typer.Option(None, "--sku-dir", help="SKU stubs directory"),
    chemicals_dir: Path = typer.Option(None, "--chemicals-dir", help="Chemicals database directory"),
    mappings_file: Path = typer.Option(None, "--mappings", help="SKU mappings file"),
):
    """Show mapping status for all SKUs."""
    from src.database import (
        load_chemical_database,
        load_sku_mapper,
    )
    from src.database.merger import generate_mapping_report

    try:
        chemical_db = load_chemical_database(chemicals_dir)
        sku_mapper = load_sku_mapper(mappings_file)

        report = generate_mapping_report(
            sku_dir=sku_dir,
            chemical_db=chemical_db,
            sku_mapper=sku_mapper,
        )

        typer.echo(f"Total SKUs: {report['total_skus']}")
        typer.echo(f"  Complete:         {len(report['complete'])}")
        typer.echo(f"  Mapped (ready):   {len(report['mapped'])}")
        typer.echo(f"  Unmapped:         {len(report['unmapped'])}")
        typer.echo(f"  Missing chemical: {len(report['missing_chemical'])}")

        if report['unmapped']:
            typer.echo("\nUnmapped SKUs (need mapping rules):")
            for sku in report['unmapped'][:10]:
                typer.echo(f"  - {sku}")
            if len(report['unmapped']) > 10:
                typer.echo(f"  ... and {len(report['unmapped']) - 10} more")

        if report['missing_chemical']:
            typer.echo("\nMissing chemicals (need database entries):")
            for item in report['missing_chemical'][:10]:
                typer.echo(f"  - {item['sku']} -> {item['chemical_id']}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


@db_app.command("add-chemical")
def db_add_chemical(
    chemical_id: str = typer.Argument(..., help="Unique chemical ID (e.g., isopropyl-alcohol-99)"),
    name: str = typer.Argument(..., help="Chemical display name"),
    cas: str = typer.Option(None, "--cas", help="CAS number"),
    family: str = typer.Option(None, "--family", help="Product family for styling"),
    chemicals_dir: Path = typer.Option(None, "--chemicals-dir", help="Chemicals database directory"),
):
    """Add a new chemical to the database (creates a stub for editing)."""
    from src.database import ChemicalData, load_chemical_database

    try:
        db = load_chemical_database(chemicals_dir)

        if chemical_id in db:
            typer.echo(f"✗ Chemical {chemical_id} already exists", err=True)
            raise typer.Exit(1)

        chemical = ChemicalData(
            chemical_id=chemical_id,
            chemical_name=name,
            cas_number=cas,
            product_family=family,
        )

        db.add(chemical)
        output_path = db.chemicals_dir / f"{chemical_id}.json"
        typer.echo(f"✓ Created chemical stub: {output_path}")
        typer.echo("  Edit this file to add GHS, NFPA, and DOT data.")

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


@db_app.command("add-mapping")
def db_add_mapping(
    sku: str = typer.Argument(..., help="SKU or SKU prefix to map"),
    chemical_id: str = typer.Argument(..., help="Chemical ID to link to"),
    is_prefix: bool = typer.Option(False, "--prefix", help="Treat SKU as a prefix rule"),
    mappings_file: Path = typer.Option(None, "--mappings", help="SKU mappings file"),
):
    """Add a SKU-to-chemical mapping."""
    from src.database import SKUMapping, load_sku_mapper
    from src.database.sku_mapper import SKUMappingRule

    try:
        mapper = load_sku_mapper(mappings_file)

        if is_prefix:
            rule = SKUMappingRule(prefix=sku, chemical_id=chemical_id)
            mapper.add_prefix_rule(rule)
            typer.echo(f"✓ Added prefix rule: {sku}* -> {chemical_id}")
        else:
            mapping = SKUMapping(sku_pattern=sku, chemical_id=chemical_id)
            mapper.add_mapping(mapping)
            typer.echo(f"✓ Added mapping: {sku} -> {chemical_id}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


@db_app.command("list-chemicals")
def db_list_chemicals(
    chemicals_dir: Path = typer.Option(None, "--chemicals-dir", help="Chemicals database directory"),
):
    """List all chemicals in the database."""
    from src.database import load_chemical_database

    try:
        db = load_chemical_database(chemicals_dir)

        if not db:
            typer.echo("No chemicals in database.")
            typer.echo(f"Add chemicals to: {db.chemicals_dir}")
            return

        typer.echo(f"Chemicals ({len(db)}):\n")
        for chemical in sorted(db.list_all(), key=lambda c: c.chemical_id):
            hazcom = "GHS" if chemical.hazcom_applicable else "---"
            dot = "DOT" if chemical.dot_regulated else "---"
            nfpa = "NFPA" if chemical.nfpa_health is not None else "----"
            typer.echo(f"  {chemical.chemical_id:<30} [{hazcom}] [{dot}] [{nfpa}]")
            typer.echo(f"    {chemical.chemical_name}")
            if chemical.cas_number:
                typer.echo(f"    CAS: {chemical.cas_number}")

    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
