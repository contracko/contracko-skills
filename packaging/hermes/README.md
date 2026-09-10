# Contracko for Hermes

This is a content-only Hermes Agent Plugins v1 bundle. It carries the four canonical Contracko skills and no executable bridge, token, or duplicate MCP declaration.

Hermes keeps portable skills namespaced and keeps MCP OAuth in its native configuration and token store. The package does not write either one for you.

## Setup

1. Extract this archive, then install the package directory with `hermes plugins install ./contracko-hermes --no-enable`.
2. Review the package, then explicitly enable the `contracko` package.
3. Check `~/.hermes/config.yaml` for an existing `mcp_servers.contracko` entry. Reuse it when present. Otherwise, after explicit approval, add only this entry while preserving the rest of the file:

   ```yaml
   mcp_servers:
     contracko:
       url: "https://app.contracko.com/mcp"
       auth: oauth
   ```

4. Run `hermes mcp login contracko`. A browser opens for Contracko sign-in and consent. Select the workspace yourself. Approve **Read** for questions and reviews. Approve **Write** only when you want the assistant to import or change contracts.
5. Reload MCP or restart Hermes using the host's normal command when the connection is ready.

The login command is an explicit user action. Do not put a bearer token in this package, a command, or a log. Do not assume that installing or enabling the bundle registers or authenticates the server.
