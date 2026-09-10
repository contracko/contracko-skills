# `@contracko/mcp`

Thin npx launcher for the Contracko MCP server. Local stdio clients (Goose and similar) spawn this package; it proxies to the hosted Streamable HTTP endpoint with OAuth.

This is not a second MCP server. Skills install stays `npx skills add https://contracko.com`.

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
