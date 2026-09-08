# Set up Contracko

This repository contains agent skills, not an MCP server to build or run locally. The Contracko MCP server is already hosted at `https://app.contracko.com/mcp` and uses Streamable HTTP.

## Follow the official setup guide

Fetch and follow **https://contracko.com/mcp/install/prompt.md**. It covers skill installation, client configuration, OAuth sign-in, dedicated MCP bearer credentials when OAuth is unavailable, workspace selection, privacy, and read-only verification. Do not ask for a credential in chat or create a duplicate connection.

For Cline, explicitly select Streamable HTTP (`"type": "streamableHttp"`); see the Cline section of [README.md](README.md). Do not start a local server process.

## After setup

Follow the installed `contracko` skill for contract search, folder filing, and other workflows. Tool names and input/output schemas come from the connection's live MCP discovery, not a copied inventory. Do not broaden permissions simply because an action is missing.

Human-readable documentation: https://contracko.com/docs/mcp-server
