"""
Basic Invoice Processing Example

This example demonstrates the most common use case: processing a single
invoice file and displaying the results.
"""

from pathlib import Path

from invoice_processor import InvoiceProcessor
from invoice_processor.config import get_settings


def main() -> None:
    """Process a single invoice and display results."""
    # Initialize processor with configuration
    settings = get_settings()
    processor = InvoiceProcessor(
        openai_api_key=settings.openai_api_key,
        ocr_language=settings.ocr_language,
    )

    # Path to invoice file
    invoice_path = Path("sample_invoice.pdf")

    # Check if file exists (for demo purposes)
    if not invoice_path.exists():
        print(f"⚠️  Sample invoice not found at: {invoice_path}")
        print("This example requires a sample invoice file.")
        print("Place a PDF invoice in the current directory as 'sample_invoice.pdf'")
        return

    print(f"📄 Processing invoice: {invoice_path}\n")

    # Process the invoice
    result = processor.process_invoice(
        file_path=invoice_path,
        validate=True,  # Enable validation
    )

    # Check if processing was successful
    if not result.success:
        print(f"❌ Processing failed: {result.error}")
        return

    # Display extracted invoice data
    invoice = result.invoice
    print("✅ Invoice processed successfully!\n")
    print("=" * 60)
    print("INVOICE DETAILS")
    print("=" * 60)
    print(f"Invoice Number:    {invoice.invoice_number}")
    print(f"Vendor:            {invoice.vendor_name}")
    print(f"Invoice Date:      {invoice.invoice_date}")
    print(f"Due Date:          {invoice.due_date}")
    print(f"Total Amount:      ${invoice.total_amount:,.2f}")
    print(f"Tax Amount:        ${invoice.tax_amount:,.2f}")
    print(f"Currency:          {invoice.currency}")
    print(f"Status:            {invoice.status.value}")
    print(f"Confidence Score:  {invoice.confidence_score:.1%}")
    print()

    # Display line items if present
    if invoice.line_items:
        print("LINE ITEMS:")
        print("-" * 60)
        for i, item in enumerate(invoice.line_items, 1):
            print(f"{i}. {item.description}")
            print(f"   Quantity: {item.quantity} × ${item.unit_price} = ${item.amount}")
            if item.account_code:
                print(f"   Account Code: {item.account_code}")
        print()

    # Display validation results if validation was performed
    if result.validation:
        validation = result.validation
        print("=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)

        if validation.is_valid:
            print("✅ All validation checks passed!")
        else:
            print("❌ Validation failed with errors:")
            for error in validation.errors:
                print(f"   • {error}")

        if validation.warnings:
            print("\n⚠️  Warnings:")
            for warning in validation.warnings:
                print(f"   • {warning}")

        print(f"\nValidation Confidence: {validation.confidence:.1%}")
        print(f"Fields Validated: {', '.join(validation.validated_fields)}")
        print()

    # Display processing metadata
    print("=" * 60)
    print("PROCESSING METADATA")
    print("=" * 60)
    print(f"Processing Time:   {result.processing_time:.2f} seconds")
    print(f"File Path:         {result.metadata.get('file_path', 'N/A')}")
    print()


if __name__ == "__main__":
    main()
