# Install instructions for coding agents

You are setting up Contracko for a user. Contracko is contract management: a workspace of contracts with extracted dates, parties and values. This repository holds agent skills; the workspace itself is reached over a remote MCP server.

There is nothing to build, clone or run locally. Do not look for a package to install, a Dockerfile, or a command to start a process. The server is already hosted.

## Step 1: add the skills

```bash
npx skills@latest add contracko/contracko-skills
```

This installs four skills (`contracko`, `contracko-import`, `contracko-review`, `contracko-create`) into the agent skills directory. It works across Claude Code, Codex, Cursor, Cline, Kilo Code, Gemini CLI, GitHub Copilot, OpenClaw, Hermes and others.

## Step 2: add the connection

The server address is:

```
https://app.contracko.com/mcp
```

It speaks **Streamable HTTP**. Set the transport explicitly where the client offers the choice, because several clients still default to the older SSE transport.

Authentication is **OAuth**. On first use the client opens a browser window where the user signs in to Contracko. A free trial can be started on that screen, so the user does not need an existing account. Do not ask the user for an API key or paste any token unless they specifically want the headless path described below.

Client-specific shapes:

```json
// Cline: ~/.cline/mcp.json, or the Configure tab in the Cline panel
{ "mcpServers": { "contracko": { "type": "streamableHttp", "url": "https://app.contracko.com/mcp" } } }
```

```json
// Cursor: .cursor/mcp.json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

```json
// VS Code and GitHub Copilot: .vscode/mcp.json
{ "servers": { "contracko": { "type": "http", "url": "https://app.contracko.com/mcp" } } }
```

```bash
# Claude Code
claude mcp add --transport http contracko https://app.contracko.com/mcp

# Codex
codex mcp add contracko --url https://app.contracko.com/mcp && codex mcp login contracko
```

## Step 3: scopes

At the sign-in screen the user picks permissions. Recommend **Read** on its own unless the user has said they want the assistant to change data. **Write** is needed to import contracts, edit fields, or set reminders. Read-only is a safe default and can be widened later by reconnecting.

## Verifying it worked

Ask the server for the contract list. If tools are missing rather than failing, the cause is almost always scopes, not a broken connection. If a call returns `"Your Contracko connection needs to be renewed."`, the OAuth session has expired and the user should reconnect from the client's connector settings.

Do not add Contracko twice. Adding the skills and adding the connection are separate steps, and running the connection step again creates a duplicate entry.

## Docs

https://contracko.com/docs/mcp-server
