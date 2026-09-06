# Contracko skills

Teach an AI assistant to work in a [Contracko](https://contracko.com) workspace over MCP.

**Endpoint (all products):** `https://app.contracko.com/mcp`

Contract data goes to the AI provider running the session. Turn off model training there before using real contracts. The plugin does **not** register the MCP server for you — if Contracko is already connected, do not add it again.

Agents: install skills, add the server for *this* product, then call `auth_validate`. Do not automate the browser sign-in. Full client recipes: [agent-setup/prompt.md](agent-setup/prompt.md).

## Connect

| Product | Skills | MCP server |
|---|---|---|
| **Any agent** | `Fetch and execute https://contracko.com/agent-setup/prompt.md` | Same file picks the client |
| **Claude Code** | `/plugin marketplace add https://github.com/contracko/contracko-skills.git` then `/plugin install contracko-skills@contracko` (HTTPS URL, not `owner/repo`) | `claude mcp add --transport http contracko https://app.contracko.com/mcp` then `/mcp` |
| **Claude.ai / Claude Desktop** | Upload skill zips from [Releases](https://github.com/contracko/contracko-skills/releases/latest), or wait for the plugin directory | **Settings > Connectors > Add custom connector** → paste the endpoint. OAuth in the browser |
| **ChatGPT** | Workspace **Settings > Plugins > Import marketplace** → `contracko/contracko-skills` | Enable Developer mode, then **Settings > Apps > Create** and paste the endpoint. ChatGPT cannot be configured from a file |
| **Codex** | Same GitHub marketplace import, or `npx skills@latest add contracko/contracko-skills` | `codex mcp add contracko --url https://app.contracko.com/mcp` then `codex mcp login contracko` |
| **Gemini CLI** | `npx skills@latest add contracko/contracko-skills` | `~/.gemini/settings.json`: `{ "mcpServers": { "contracko": { "httpUrl": "https://app.contracko.com/mcp" } } }` |
| **GitHub Copilot** (VS Code) | `copilot plugin marketplace add contracko/contracko-skills` | `.vscode/mcp.json`: `{ "servers": { "contracko": { "type": "http", "url": "https://app.contracko.com/mcp" } } }` |
| **Cursor** | `npx skills@latest add contracko/contracko-skills` | `.cursor/mcp.json`: `{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }` |
| **OpenClaw** | `npx skills@latest add contracko/contracko-skills` | `openclaw mcp set contracko '{"url":"https://app.contracko.com/mcp","transport":"streamable-http"}'` then `openclaw mcp configure contracko --auth oauth` and `openclaw mcp login contracko` |
| **Hermes** | `npx skills@latest add contracko/contracko-skills` (or `hermes import-agent` from Claude Code) | `~/.hermes/config.yaml`: `mcp_servers.contracko.url: https://app.contracko.com/mcp` and `auth: oauth`, then `hermes mcp login contracko` |
| **Grok** (grok.com) | Skills from this GitHub repo if the client supports `SKILL.md` | [grok.com/connectors](https://grok.com/connectors) → add the endpoint (must be public HTTPS) |
| **Grok CLI** | `npx skills@latest add contracko/contracko-skills` | `grok mcp add --transport http contracko https://app.contracko.com/mcp` |

Headless / CI: MCP API key from Contracko **Settings > Integrations > API keys**, purpose **MCP server**. Pass `Authorization: Bearer <key>`. OAuth needs a browser; do not improvise around it.

Tick **read** for questions, **write** to add or change contracts (write is off by default), **parser** only if you want extraction without filing.

## What you can ask

| Ask | Assistant does now | You still do in Contracko |
|---|---|---|
| "Import the PDFs in this folder / Drive / SharePoint / Box" | Finds files with *its* disk or cloud tools, confirms, imports. Contracko extracts dates, parties, types | Confirm pending-review extractions. Folders |
| "What needs notice in the next 90 days?" | Reads notice dates, end dates, renewal flags | Reminders that should fire later |
| "Compare these two vendor proposals" | Tables both sides from records, analysis, quoted clauses | Playbook scoring. No automatic redline-diff |
| "Where is liability uncapped?" | Analysis plus the sentence that supports it | Measuring against a house playbook |
| "Set up proper contract types / how should we folder these?" | Types, fields, metadata. Can *see* `folderId` | Create folders and move contracts |
| "What should we look at this month?" | Pages the workspace; ranks urgency and gaps | Saved reports and list filters |
| "Help me draft an NDA and file it when signed" | Questionnaire, then files the signed copy | Template draft and signature |

## Skills included

| Skill | Use when |
|---|---|
| [`contracko`](skills/contracko/SKILL.md) | Connecting, scopes, contract types, fields, counterparties, folder *plan*. Router. Jobs: [workflows.md](skills/contracko/references/workflows.md). Tools: [tool-index.md](skills/contracko/references/tool-index.md) |
| [`contracko-import`](skills/contracko-import/SKILL.md) | Finding files and getting them into Contracko |
| [`contracko-review`](skills/contracko-review/SKILL.md) | Notice dates, comparisons, risk audits, portfolio |
| [`contracko-create`](skills/contracko-create/SKILL.md) | A new agreement, from questions to filing the signed PDF |

The assistant's live tool list outranks these files. Steps with no tool yet are done in the app — never invent a tool name.

MIT licensed.
