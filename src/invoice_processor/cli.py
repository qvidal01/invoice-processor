"""Command-line interface for invoice processor."""

import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from invoice_processor import InvoiceProcessor
from invoice_processor.config import get_settings
from invoice_processor.utils.logging_config import setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(debug: bool) -> None:
    """Invoice Processor - Automated invoice extraction and processing."""
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(level=log_level)


@main.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--validate/--no-validate", default=True, help="Validate extracted data")
@click.option("--po-number", help="Purchase order number for validation")
def process(file_path: Path, validate: bool, po_number: Optional[str]) -> None:
    """Process a single invoice file."""
    console.print(f"[bold]Processing:[/bold] {file_path}")

    try:
        settings = get_settings()
    except Exception as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        return

    processor = InvoiceProcessor(openai_api_key=settings.openai_api_key)

    result = processor.process_invoice(file_path, validate=validate, po_number=po_number)

    if result.success and result.invoice:
        console.print("[green]✓[/green] Processing successful")
        _display_invoice(result.invoice)

        if result.validation:
            _display_validation(result.validation)
    else:
        console.print(f"[red]✗[/red] Processing failed: {result.error}")


@main.command()
@click.argument("directory", type=click.Path(exists=True, path_type=Path))
@click.option("--pattern", default="*.pdf", help="File pattern to match")
@click.option("--validate/--no-validate", default=True, help="Validate extracted data")
def batch(directory: Path, pattern: str, validate: bool) -> None:
    """Process all invoices in a directory."""
    console.print(f"[bold]Processing batch:[/bold] {directory}")

    try:
        settings = get_settings()
    except Exception as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        return

    processor = InvoiceProcessor(openai_api_key=settings.openai_api_key)

    results = processor.process_batch(directory, validate=validate, file_pattern=pattern)

    # Summary table
    table = Table(title="Processing Summary")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Vendor")
    table.add_column("Amount", justify="right")

    for result in results:
        if result.success and result.invoice:
            status = "✓"
            vendor = result.invoice.vendor_name
            amount = f"${result.invoice.total_amount}"
        else:
            status = "✗"
            vendor = "N/A"
            amount = "N/A"

        file_name = result.metadata.get("file_path", "")
        table.add_row(file_name, status, vendor, amount)

    console.print(table)


def _display_invoice(invoice) -> None:  # type: ignore
    """Display invoice details in a table."""
    table = Table(title="Invoice Data")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Invoice Number", invoice.invoice_number)
    table.add_row("Vendor", invoice.vendor_name)
    table.add_row("Date", str(invoice.invoice_date))
    table.add_row("Due Date", str(invoice.due_date))
    table.add_row("Total Amount", f"${invoice.total_amount}")
    table.add_row("Tax Amount", f"${invoice.tax_amount}")
    table.add_row("Confidence", f"{invoice.confidence_score:.1%}")

    console.print(table)


def _display_validation(validation) -> None:  # type: ignore
    """Display validation results."""
    if validation.is_valid:
        console.print("[green]✓ Validation passed[/green]")
    else:
        console.print("[red]✗ Validation failed[/red]")

    if validation.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in validation.errors:
            console.print(f"  • {error}")

    if validation.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in validation.warnings:
            console.print(f"  • {warning}")


if __name__ == "__main__":
    main()
