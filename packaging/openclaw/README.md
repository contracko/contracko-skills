# Contracko for OpenClaw

This is a content-only OpenClaw bundle. It carries the four canonical Contracko skills and no executable bridge, token, or duplicate MCP declaration.

OpenClaw's portable bundle format does not carry Contracko's interactive OAuth configuration. Keep connection setup in OpenClaw so it can preserve its own MCP registry, browser flow, token storage, and tool policy.

## Setup

1. Extract this archive, then install the package directory with `openclaw plugins install ./contracko-openclaw`.
2. Enable the bundle if OpenClaw asks, then restart the Gateway when prompted.
3. Check whether a server named `contracko` already exists. If it does, reuse that entry rather than adding a second connection.
4. If it does not exist, explicitly approve adding this server to the central MCP registry, then run:

   ```bash
   openclaw mcp set contracko '{"url":"https://app.contracko.com/mcp","transport":"streamable-http"}'
   openclaw mcp configure contracko --auth oauth
   openclaw mcp login contracko
   ```

5. A browser opens for Contracko sign-in and consent. Select the workspace yourself. Approve **Read** for questions and reviews. Approve **Write** only when you want the assistant to import or change contracts.

The login command is an explicit user action. Do not put a bearer token in this package, a command, or a log. Do not assume that installing the bundle registers or authenticates the server.
