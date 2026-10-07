# `@contracko/mcp`

Thin npx launcher for the Contracko MCP server. Local stdio clients (Goose and similar) spawn this package; it proxies to the hosted Streamable HTTP endpoint with OAuth.

This is not a second MCP server. Skills install stays `npx skills add https://contracko.com`.

CLM (`clm_*`) adds, imports and manages contracts without Parser credits. Contracko Parser (`parser_*`) is separate bulk document processing that uses Parser credits, not needed to add contracts to your contract register.

The 7-day CLM free trial includes 3 AI extractions, 10 Clara messages and 1 signature request in total. At a limit Contracko returns a plan notice: subscribe to lift the limits, and do not retry. Parser credits do not lift them. Parser's 20 free credits are credits, not extractions; a document costs 1 to 5 credits, more with review.

Use `npx -y @contracko/mcp --help` for launcher help without connecting.

## Run

```bash
npx -y @contracko/mcp
```

Goose / stdio config:

```json
{
  "mcpServers": {
    "contracko": {
      "command": "npx",
      "args": ["-y", "@contracko/mcp"]
    }
  }
}
```

The process connects to `https://app.contracko.com/mcp`. Setup steps for clients that speak HTTP directly: [contracko.com/mcp](https://contracko.com/mcp).
