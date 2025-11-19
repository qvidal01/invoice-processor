# Invoice Processor MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for Invoice Processor, enabling AI assistants like Claude to process invoices directly.

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) (MCP) is an open protocol that standardizes how applications provide context to LLMs. MCP servers expose tools, resources, and prompts that AI assistants can use.

## Features

The Invoice Processor MCP server provides:

### Tools

1. **process_invoice** - Extract and validate data from invoice files
   - Supports PDF and image formats
   - Performs OCR and AI-based extraction
   - Optional validation against business rules
   - Returns structured invoice data

2. **validate_invoice** - Validate invoice against PO and rules
   - Checks data completeness
   - Verifies amounts and calculations
   - Applies business rules
   - Returns validation errors and warnings

3. **get_processing_status** - Check invoice processing status
   - Query by invoice ID
   - Returns current status and details

### Resources

- **invoice://{invoice_id}** - Access processed invoice data as JSON

## Installation

The MCP server is included with the invoice-processor package:

```bash
pip install invoice-processor[mcp]
```

Or with Poetry:

```bash
poetry install --extras mcp
```

## Usage

### Running the Server

```bash
# Run MCP server
invoice-mcp-server

# Or using Python module
python -m invoice_processor.mcp_server.server
```

### Configuration with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "invoice-processor": {
      "command": "invoice-mcp-server",
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Using with Claude

Once configured, you can ask Claude to process invoices:

```
User: Process the invoice at /path/to/invoice.pdf

Claude: [Uses process_invoice tool]
I've processed the invoice. Here are the details:
- Invoice Number: INV-12345
- Vendor: Acme Corp
- Total Amount: $1,250.00
- Status: Validated ✓

The invoice passed all validation checks.
```

## Example Workflows

### Basic Invoice Processing

```
User: I have an invoice from a vendor. Can you extract the data?

Claude: I'll process that invoice for you. What's the file path?

User: /invoices/2024/vendor_invoice_jan.pdf

Claude: [Calls process_invoice tool]
I've successfully extracted the invoice data:

Invoice Details:
- Vendor: Acme Supplies Inc.
- Invoice #: INV-2024-0123
- Date: 2024-01-15
- Due Date: 2024-02-15
- Total: $2,450.00
- Tax: $180.00
- Confidence: 95%

The invoice contains 5 line items and passed all validation checks.
```

### Invoice with Validation

```
User: Process this invoice and validate against PO-5678

Claude: [Calls process_invoice with po_number="PO-5678"]
I've processed the invoice and validated it against PO-5678.

⚠️ Validation Issues Found:

Errors:
• Amount exceeds PO by $500.00
• Line item "Premium Widget" not found on PO

Warnings:
• Vendor address differs from PO

The invoice should be flagged for manual review before approval.
```

### Batch Processing Workflow

```
User: I have 10 invoices in /invoices/batch/ - can you process them all?

Claude: I'll process each invoice in that directory. Let me work through them...

[Processes each file using process_invoice]

Summary of 10 invoices:
✓ 7 passed validation
⚠️ 2 have warnings (reviewed and acceptable)
✗ 1 failed (amount mismatch with PO)

Total value: $25,430.00

Would you like me to sync the approved invoices to your accounting system?
```

## Development

### Adding New Tools

To add a new MCP tool:

1. Define the tool schema in `list_tools()`
2. Add a handler function (e.g., `handle_new_tool()`)
3. Register the handler in `call_tool()`
4. Add tests in `tests/test_mcp_server.py`

Example:

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ... existing tools ...
        Tool(
            name="generate_report",
            description="Generate processing report for date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                },
                "required": ["start_date", "end_date"],
            },
        ),
    ]

async def handle_generate_report(arguments: dict) -> list[TextContent]:
    # Implementation here
    pass
```

### Testing the Server

```bash
# Test MCP server
pytest tests/test_mcp_server.py

# Test with MCP inspector
npx @modelcontextprotocol/inspector invoice-mcp-server
```

## Architecture

```
┌─────────────────────────────────────┐
│      Claude Desktop / Client        │
└──────────────┬──────────────────────┘
               │ MCP Protocol (stdio)
┌──────────────▼──────────────────────┐
│     Invoice MCP Server (this)       │
│  ┌──────────────────────────────┐   │
│  │  Tools                       │   │
│  │  - process_invoice           │   │
│  │  - validate_invoice          │   │
│  │  - get_status                │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Resources                   │   │
│  │  - invoice://                │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Invoice Processor Core          │
│  - OCR Engine                       │
│  - Data Extractor (GPT-4)           │
│  - Validator                        │
│  - Integrations                     │
└─────────────────────────────────────┘
```

## Troubleshooting

### Server won't start

- Check that OpenAI API key is set in environment
- Verify all dependencies are installed: `poetry install --extras mcp`
- Check logs for specific error messages

### Tools not appearing in Claude

- Verify Claude Desktop config is valid JSON
- Restart Claude Desktop after config changes
- Check server is running: `ps aux | grep invoice-mcp-server`

### Processing errors

- Ensure invoice files are readable and valid formats
- Check OCR dependencies are installed (Tesseract, Poppler)
- Verify API quotas and rate limits

## Security Considerations

- **API Keys**: Never commit API keys. Use environment variables.
- **File Access**: MCP server can only access files the user has permission to read.
- **Rate Limiting**: OpenAI API calls are subject to rate limits.
- **Data Privacy**: Invoice data is processed locally; only text is sent to OpenAI for extraction.

## Learn More

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## Support

- GitHub Issues: Report bugs or request features
- Discussions: Ask questions and share use cases
- Email: contact@aiqso.io for security issues
