"""
MCP (Model Context Protocol) Server for Invoice Processor.

This server exposes invoice processing capabilities as MCP tools that can be
used by AI assistants like Claude.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server, stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)

from invoice_processor import InvoiceProcessor
from invoice_processor.config import get_settings

logger = logging.getLogger(__name__)

# Create MCP server
app = Server("invoice-processor")

# Global processor instance (will be initialized in main)
processor: Optional[InvoiceProcessor] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="process_invoice",
            description="Extract data from an invoice file (PDF/image) and optionally validate it",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to invoice PDF or image file",
                    },
                    "validate": {
                        "type": "boolean",
                        "description": "Whether to validate against business rules",
                        "default": True,
                    },
                    "po_number": {
                        "type": "string",
                        "description": "Purchase order number for validation (optional)",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="validate_invoice",
            description="Validate extracted invoice data against purchase order and business rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "ID of previously processed invoice",
                    },
                    "po_number": {
                        "type": "string",
                        "description": "Purchase order number to validate against",
                    },
                },
                "required": ["invoice_id"],
            },
        ),
        Tool(
            name="get_processing_status",
            description="Get current status and details of invoice processing",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "ID of invoice to check",
                    }
                },
                "required": ["invoice_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        if name == "process_invoice":
            return await handle_process_invoice(arguments)
        elif name == "validate_invoice":
            return await handle_validate_invoice(arguments)
        elif name == "get_processing_status":
            return await handle_get_status(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]


async def handle_process_invoice(arguments: dict) -> list[TextContent]:
    """
    Handle process_invoice tool call.

    Args:
        arguments: Tool arguments with file_path, validate, po_number

    Returns:
        List of text content with processing results
    """
    if processor is None:
        return [TextContent(type="text", text="Error: Processor not initialized")]

    file_path = Path(arguments["file_path"])
    validate = arguments.get("validate", True)
    po_number = arguments.get("po_number")

    if not file_path.exists():
        return [
            TextContent(
                type="text",
                text=f"Error: File not found: {file_path}",
            )
        ]

    # Process the invoice
    result = processor.process_invoice(file_path, validate=validate, po_number=po_number)

    if result.success and result.invoice:
        # Format successful result
        invoice = result.invoice
        text = f"""✓ Invoice processed successfully

**Invoice Details:**
- Invoice Number: {invoice.invoice_number}
- Vendor: {invoice.vendor_name}
- Date: {invoice.invoice_date}
- Due Date: {invoice.due_date}
- Total Amount: ${invoice.total_amount}
- Tax Amount: ${invoice.tax_amount}
- Currency: {invoice.currency}
- Confidence Score: {invoice.confidence_score:.1%}
- Line Items: {len(invoice.line_items)}

**Processing Time:** {result.processing_time:.2f}s
"""

        if result.validation:
            validation = result.validation
            text += f"\n**Validation:**\n"
            text += f"- Status: {'✓ PASS' if validation.is_valid else '✗ FAIL'}\n"
            text += f"- Confidence: {validation.confidence:.1%}\n"

            if validation.errors:
                text += f"\n**Errors:**\n"
                for error in validation.errors:
                    text += f"  • {error}\n"

            if validation.warnings:
                text += f"\n**Warnings:**\n"
                for warning in validation.warnings:
                    text += f"  • {warning}\n"

        return [TextContent(type="text", text=text)]
    else:
        return [
            TextContent(
                type="text",
                text=f"✗ Processing failed: {result.error}\n\nProcessing time: {result.processing_time:.2f}s",
            )
        ]


async def handle_validate_invoice(arguments: dict) -> list[TextContent]:
    """
    Handle validate_invoice tool call.

    Args:
        arguments: Tool arguments with invoice_id, po_number

    Returns:
        List of text content with validation results
    """
    # TODO: Implement database lookup and validation
    invoice_id = arguments["invoice_id"]
    po_number = arguments.get("po_number")

    return [
        TextContent(
            type="text",
            text=f"Validation not yet implemented for invoice: {invoice_id}",
        )
    ]


async def handle_get_status(arguments: dict) -> list[TextContent]:
    """
    Handle get_processing_status tool call.

    Args:
        arguments: Tool arguments with invoice_id

    Returns:
        List of text content with status information
    """
    # TODO: Implement database lookup
    invoice_id = arguments["invoice_id"]

    return [
        TextContent(
            type="text",
            text=f"Status lookup not yet implemented for invoice: {invoice_id}",
        )
    ]


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available MCP resources."""
    return [
        Resource(
            uri="invoice://",
            name="Invoice Data",
            description="Access to processed invoice data",
            mimeType="application/json",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read MCP resource.

    Args:
        uri: Resource URI (e.g., invoice://INV-123)

    Returns:
        Resource content as JSON string
    """
    if uri.startswith("invoice://"):
        invoice_id = uri.replace("invoice://", "")
        # TODO: Implement database lookup
        return f'{{"error": "Resource lookup not yet implemented for {invoice_id}"}}'

    raise ValueError(f"Unknown resource URI: {uri}")


async def main() -> None:
    """Run the MCP server."""
    global processor

    # Initialize settings and processor
    settings = get_settings()
    processor = InvoiceProcessor(
        openai_api_key=settings.openai_api_key,
        ocr_language=settings.ocr_language,
    )

    logger.info("Starting Invoice Processor MCP Server...")

    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run server
    asyncio.run(main())
