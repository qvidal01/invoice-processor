"""
Batch Invoice Processing Example

Demonstrates how to process multiple invoices from a directory
and generate a summary report.
"""

from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from invoice_processor import InvoiceProcessor
from invoice_processor.config import get_settings
from invoice_processor.models import ProcessingResult


console = Console()


def process_batch(directory: Path, pattern: str = "*.pdf") -> List[ProcessingResult]:
    """
    Process all invoices in a directory.

    Args:
        directory: Directory containing invoice files
        pattern: Glob pattern for files (default: '*.pdf')

    Returns:
        List of processing results
    """
    # Initialize processor
    settings = get_settings()
    processor = InvoiceProcessor(
        openai_api_key=settings.openai_api_key,
        ocr_language=settings.ocr_language,
    )

    # Find all matching files
    files = list(directory.glob(pattern))
    console.print(f"\n📁 Found {len(files)} files matching pattern: {pattern}\n")

    if not files:
        console.print(
            "[yellow]⚠️  No files found. Create a directory with sample invoices.[/yellow]"
        )
        return []

    # Process each file
    results = []
    with console.status("[bold green]Processing invoices...") as status:
        for i, file_path in enumerate(files, 1):
            status.update(f"[bold green]Processing {i}/{len(files)}: {file_path.name}")
            result = processor.process_invoice(file_path, validate=True)
            results.append(result)

    return results


def display_summary(results: List[ProcessingResult]) -> None:
    """Display summary table of processing results."""
    if not results:
        return

    # Create summary table
    table = Table(title="📊 Batch Processing Summary", show_header=True, header_style="bold")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Vendor", style="green")
    table.add_column("Amount", justify="right", style="yellow")
    table.add_column("Validation", justify="center")
    table.add_column("Time", justify="right")

    # Calculate statistics
    total_amount = 0
    successful = 0
    validated = 0

    # Add rows
    for result in results:
        file_name = Path(result.metadata.get("file_path", "")).name

        if result.success and result.invoice:
            status = "✅"
            vendor = result.invoice.vendor_name[:30]
            amount = f"${result.invoice.total_amount:,.2f}"
            total_amount += float(result.invoice.total_amount)
            successful += 1

            if result.validation:
                if result.validation.is_valid:
                    validation_status = "✅"
                    validated += 1
                else:
                    validation_status = f"❌ ({len(result.validation.errors)})"
            else:
                validation_status = "—"
        else:
            status = "❌"
            vendor = "Error"
            amount = "—"
            validation_status = "—"

        processing_time = f"{result.processing_time:.1f}s"

        table.add_row(file_name, status, vendor, amount, validation_status, processing_time)

    console.print(table)

    # Display statistics
    console.print("\n" + "=" * 60)
    console.print("[bold]SUMMARY STATISTICS[/bold]")
    console.print("=" * 60)
    console.print(f"Total Files:           {len(results)}")
    console.print(f"Successfully Processed: {successful} ({successful/len(results)*100:.1f}%)")
    console.print(f"Validation Passed:     {validated} ({validated/len(results)*100:.1f}%)")
    console.print(f"Total Invoice Value:   ${total_amount:,.2f}")

    # Show failed invoices if any
    failed = [r for r in results if not r.success]
    if failed:
        console.print("\n[bold red]❌ Failed Invoices:[/bold red]")
        for result in failed:
            file_name = Path(result.metadata.get("file_path", "")).name
            console.print(f"  • {file_name}: {result.error}")

    # Show validation errors
    validation_errors = [
        r for r in results if r.success and r.validation and not r.validation.is_valid
    ]
    if validation_errors:
        console.print("\n[bold yellow]⚠️  Validation Issues:[/bold yellow]")
        for result in validation_errors:
            file_name = Path(result.metadata.get("file_path", "")).name
            console.print(f"\n  {file_name}:")
            for error in result.validation.errors:
                console.print(f"    • {error}")


def main() -> None:
    """Main function to run batch processing example."""
    # Directory containing invoices
    invoice_dir = Path("sample_invoices")

    if not invoice_dir.exists():
        console.print("[yellow]⚠️  Sample invoices directory not found[/yellow]")
        console.print(f"Please create a directory at: {invoice_dir}")
        console.print("And add some sample invoice PDF files")
        return

    console.print("[bold]📦 Batch Invoice Processing Example[/bold]")
    console.print(f"Directory: {invoice_dir.absolute()}\n")

    # Process all invoices
    results = process_batch(invoice_dir)

    # Display summary
    if results:
        display_summary(results)
    else:
        console.print("[yellow]No results to display[/yellow]")


if __name__ == "__main__":
    main()
