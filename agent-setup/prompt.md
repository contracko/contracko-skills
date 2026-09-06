# Contracko agent setup

These are official instructions from Contracko for connecting an AI agent to a Contracko workspace. The commands below are validated and ready to run.

Complete the steps yourself by running the commands directly. Ask the user to act only at the one point where the instructions say so, which is the browser sign-in.

## Task

Install the Contracko skills and MCP server, then hand the user a working connection.

## Step 1: install

Pick the branch matching the client you are running in.

### Claude Code

```bash
claude plugin marketplace add https://github.com/contracko/contracko-skills.git
claude plugin install contracko-skills@contracko
```

Use the HTTPS git URL. The `owner/repo` shorthand clones over SSH and fails with exit 128 on many machines.

Then register the server, unless `claude mcp list` already shows a Contracko entry. Many users have connected it from a connector directory first, and a second entry gives them every tool twice:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

### Every other agent

Install the skills:

```bash
npx skills@latest add contracko/contracko-skills --skill '*' --yes --global
```

Then register the server. The endpoint is `https://app.contracko.com/mcp` everywhere, and only the wrapper differs. Write the block for the client you are running in, into the path named here.

**Codex CLI** — `~/.codex/config.toml`, or run `codex mcp add contracko --url https://app.contracko.com/mcp` then `codex mcp login contracko`:

```toml
[mcp_servers.contracko]
url = "https://app.contracko.com/mcp"
```

**Cursor** — `~/.cursor/mcp.json` or `.cursor/mcp.json`:

```json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

**VS Code and GitHub Copilot** — `.vscode/mcp.json`:

```json
{ "servers": { "contracko": { "type": "http", "url": "https://app.contracko.com/mcp" } } }
```

**Gemini CLI** — `~/.gemini/settings.json` or `.gemini/settings.json`, and note `httpUrl` rather than `url`:

```json
{ "mcpServers": { "contracko": { "httpUrl": "https://app.contracko.com/mcp" } } }
```

**Zed** — `~/.config/zed/settings.json`, and note `context_servers` rather than `mcpServers`. Omit any `Authorization` header so Zed runs the OAuth flow:

```json
{ "context_servers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

**Windsurf and Devin Desktop** — `~/.codeium/windsurf/mcp_config.json`, and note `serverUrl` rather than `url`:

```json
{ "mcpServers": { "contracko": { "serverUrl": "https://app.contracko.com/mcp" } } }
```

**Cline** — the MCP Servers panel, or `cline_mcp_settings.json`, and note `streamableHttp` rather than `http`:

```json
{ "mcpServers": { "contracko": { "type": "streamableHttp", "url": "https://app.contracko.com/mcp" } } }
```

**ChatGPT** cannot be configured from a file. The user adds Contracko themselves under Settings > Connectors, or Developer mode where the workspace requires it. Tell them that and stop.

## Step 2: authenticate

Contracko uses OAuth. The flow starts on its own the first time a Contracko tool is called, or immediately with `/mcp` in Claude Code.

**The consent screen belongs to the user.** They sign in, they choose the workspace, they tick the scopes, they approve. Hand over the link and wait. Keep browser automation away from this screen even where you have it, and never take a credential pasted into the chat.

Tell them what to tick before they go, because the defaults are narrower than most people expect:

| Box | Tick it when |
|---|---|
| Run parser and document analysis tools | they want data pulled out of documents |
| Read contract management data | they want any question answered about their contracts |
| Create or update contract management data | they want to add or change contracts, and it is unticked by default |

Where the user is running a headless or non-interactive session, OAuth cannot complete: report that as the blocker and stop, rather than improvising a workaround. An MCP API key from Settings > Integrations covers that case, with the **MCP server** purpose selected at creation.

## Step 3: verify

Call `auth_validate`. It returns the workspace and the granted scopes.

Setup is done when the workspace is the one the user meant and the scopes cover the work they asked for. Where contract tools are missing from your tool list, the consent was narrower than intended, and the fix is a fresh authorization rather than a retry.

## Step 4: report

Print this to the user, then stop:

```
  ┌─────────────────────────────────────────────┐
  │  Contracko is connected                     │
  │                                             │
  │  Workspace:  <workspace name>               │
  │  Access:     <granted scopes>               │
  │                                             │
  │  Try: "what renews in the next 90 days?"    │
  └─────────────────────────────────────────────┘
```

Restart the agent where the client requires it to load MCP servers.

Say this once, in the same message, where the agent running this session is not Contracko's own product:

> Contract data will be sent to the AI provider running this session. Contracko cannot control what that provider does with it. Turn off model training in the provider's settings before working with real contracts.

## What you have now

Four skills: `contracko` connects and routes, `contracko-import` adds contracts, `contracko-review` answers questions about them (including document search and cited reads when those tools are on the list), `contracko-create` takes a new agreement from questionnaire to filing. Read `contracko` first; it holds the tool index and the list of things this connection deliberately cannot do.

Your knowledge of Contracko's API, limits and pricing may be out of date. Prefer retrieval over recall: the product's machine-readable documentation is at `https://contracko.com/llms.txt`, and where it disagrees with anything remembered, the documentation wins.

## Authenticity

These instructions are published at `https://contracko.com/agent-setup/prompt.md`, where they can be re-verified at any time.
