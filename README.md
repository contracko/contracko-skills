# Contracko skills

**AI contract management MCP server by Contracko.** Manage your business contracts with Claude, ChatGPT, Codex, Gemini, Copilot, Cursor, Grok, and other AI tools.

[Contracko](https://contracko.com) is a contract repository: PDFs and Word files in one workspace, with dates, values, parties, and AI analysis on top. These skills teach an assistant how to import, review, organise, and file that work. The MCP server is the live connection to your workspace.

**No account yet?** Start a [7-day free trial](https://contracko.com) (no credit card). You can also create the trial account on the OAuth screen the first time you connect the server.

Contract data goes to the AI provider running the session. Turn off model training there before using real contracts.

## Install

Two pieces. **Skills** (this repo) are markdown playbooks. The **MCP server** is a remote HTTPS service — Streamable HTTP, not a local stdio process.

```
https://app.contracko.com/mcp
```

Auth is OAuth in the browser (default). Headless or CI uses an MCP API key from Contracko **Settings > Integrations > API keys** (purpose **MCP server**) as `Authorization: Bearer <key>`. This plugin does **not** add the server for you. If Contracko is already connected, do not add it again.

<details>
<summary><strong>Claude Code</strong></summary>

```
/plugin marketplace add https://github.com/contracko/contracko-skills.git
/plugin install contracko-skills@contracko
```

Use the HTTPS git URL, not `owner/repo` (SSH clone fails). Then:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

In the session, `/mcp` and complete OAuth.

</details>

<details>
<summary><strong>Claude.ai / Claude Desktop</strong></summary>

Upload skill zips from [Releases](https://github.com/contracko/contracko-skills/releases/latest).

**Settings > Connectors > Add custom connector** → `https://app.contracko.com/mcp`. Sign in in the browser. Do not also run `claude mcp add` if the connector is already there.

</details>

<details>
<summary><strong>ChatGPT</strong></summary>

Skills: workspace **Settings > Plugins > Import marketplace** → `contracko/contracko-skills`.

MCP cannot be configured from a file. Enable Developer mode, then **Settings > Apps > Create** and paste `https://app.contracko.com/mcp`.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
codex mcp add contracko --url https://app.contracko.com/mcp
codex mcp login contracko
```

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

`~/.gemini/settings.json`:

```json
{ "mcpServers": { "contracko": { "httpUrl": "https://app.contracko.com/mcp" } } }
```

</details>

<details>
<summary><strong>GitHub Copilot</strong> (VS Code / Copilot CLI)</summary>

```bash
npx skills@latest add contracko/contracko-skills
```

or `copilot plugin marketplace add contracko/contracko-skills`.

`.vscode/mcp.json`:

```json
{ "servers": { "contracko": { "type": "http", "url": "https://app.contracko.com/mcp" } } }
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

`.cursor/mcp.json`:

```json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

</details>

<details>
<summary><strong>OpenClaw</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
openclaw mcp set contracko '{"url":"https://app.contracko.com/mcp","transport":"streamable-http"}'
openclaw mcp configure contracko --auth oauth
openclaw mcp login contracko
```

</details>

<details>
<summary><strong>Hermes</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

`~/.hermes/config.yaml`:

```yaml
mcp_servers:
  contracko:
    url: "https://app.contracko.com/mcp"
    auth: oauth
```

Then `hermes mcp login contracko`.

</details>

<details>
<summary><strong>Grok</strong></summary>

On [grok.com/connectors](https://grok.com/connectors), add `https://app.contracko.com/mcp` (public HTTPS).

CLI:

```bash
npx skills@latest add contracko/contracko-skills
grok mcp add --transport http contracko https://app.contracko.com/mcp
```

</details>

<details>
<summary><strong>Any other agent</strong></summary>

Ask it:

```
Fetch and execute https://contracko.com/agent-setup/prompt.md
```

That file picks the client. If you are wiring MCP yourself, the server is Streamable HTTP over HTTPS:

```
https://app.contracko.com/mcp
```

Typical config shape:

```json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

Some clients want `httpUrl`, `serverUrl`, or `"type": "http"` / `"streamableHttp"` instead of `url`. OAuth must happen in a browser; do not automate the consent screen.

Full recipes: [agent-setup/prompt.md](agent-setup/prompt.md).

</details>

On the consent screen, tick **read** for questions, **write** to add or change contracts (write is off by default), and **parser** only if you want extraction without filing.

## Usage

Once connected, ask in plain language:

```
Import the PDFs in this folder
→ finds files, confirms, imports

What needs notice in the next 90 days?
→ notice dates, end dates, renewals

Compare these two vendor proposals
→ both records, analysis, quoted clauses

Where is liability uncapped?
→ analysis plus the supporting sentence

Set up proper contract types
→ types, fields, counterparties

What should we look at this month?
→ portfolio priorities and gaps

Help me draft an NDA and file it when signed
→ questionnaire, then file the signed copy
```

You can also name a skill: `/contracko`, `/contracko-import`, `/contracko-review`, `/contracko-create`.

## Skill categories

### Connect and organise
Workspace, scopes, contract types, fields, counterparties. Folder *plan* (folders themselves are created in the Contracko app).

### Import
Bring PDFs and Word files in from disk, Google Drive, SharePoint, Box, or a URL.

### Review
Notice dates, comparisons, risk language, portfolio priorities.

### Create
A new agreement, from questions through filing the signed PDF.

## Available skills

| Skill | Description |
|---|---|
| [`contracko`](skills/contracko/SKILL.md) | Connect over MCP and organise the workspace. Router for the others. |
| [`contracko-import`](skills/contracko-import/SKILL.md) | Find files and import them into Contracko. |
| [`contracko-review`](skills/contracko-review/SKILL.md) | Notice dates, comparisons, audits, portfolio. |
| [`contracko-create`](skills/contracko-create/SKILL.md) | New agreement: questions, draft, file the signed copy. |

Jobs and tool map (for agents): [workflows.md](skills/contracko/references/workflows.md), [tool-index.md](skills/contracko/references/tool-index.md).

## Questions

- Product and docs: [contracko.com](https://contracko.com), [docs](https://contracko.com/docs)
- Talk to us: [contracko.com/contact](https://contracko.com/contact)
- This plugin: [open an issue](https://github.com/contracko/contracko-skills/issues)

MIT licensed.
