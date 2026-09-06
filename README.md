# Contracko skills

**AI contract management MCP server by Contracko.** Manage your business contracts with Claude, ChatGPT, Codex, Gemini, Copilot, Cursor, Grok, and other AI tools.

[Contracko](https://contracko.com) is a contract repository: PDFs and Word files in one workspace, with dates, values, parties, and AI analysis on top. These skills teach an assistant how to import, review, organise, and file that work. The MCP server is the live connection to your workspace.

**No account yet?** Start a [7-day free trial](https://contracko.com) (no credit card). You can also create the trial account on the OAuth screen the first time you connect the server.

## Security

Contracko does not train models on your contracts. Analysis inside the product runs under commercial API terms, with Zero Data Retention where we have it, and we work to get ZDR with every AI subprocessor. See [Security](https://contracko.com/features/security).

Connecting this plugin is different: when Claude, ChatGPT, Codex, or another assistant calls Contracko, contract text is sent to *that* product. Contracko cannot control what they do with it. Turn off model training in that product before using real contracts.

## Install

Two pieces. **Skills** (this repo) are markdown playbooks. The **MCP server** is a remote HTTPS service — Streamable HTTP, not a local stdio process.

```
https://app.contracko.com/mcp
```

Auth is OAuth. Terminal agents open a browser the same way desktop apps do. This plugin does **not** add the server for you. If Contracko is already connected, do not add it again.

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

Once connected, talk to the assistant the way you would a colleague.

| Try asking | What it does |
|---|---|
| Import the PDFs in this folder | Finds the files, checks with you, and brings them into Contracko |
| What needs notice in the next 90 days? | Lists contracts coming up for notice, end, or renewal |
| Compare these two vendor proposals | Puts both side by side, with the clauses that matter |
| Where is liability uncapped? | Finds the risk language and quotes the contract |
| Set up proper contract types | Helps you define types, fields, and counterparties |
| What should we look at this month? | Ranks what is urgent and what is missing |
| Help me draft an NDA and file it when signed | Walks through the questions, then files the signed copy |

## Skills

Four playbooks. You do not have to pick one; asking in plain language is enough.

| Skill | Use it for |
|---|---|
| [contracko](skills/contracko/SKILL.md) | Connecting, then organising types, fields, and counterparties |
| [contracko-import](skills/contracko-import/SKILL.md) | Bringing PDFs and Word files in from disk, Drive, SharePoint, Box, or a link |
| [contracko-review](skills/contracko-review/SKILL.md) | Notice dates, comparisons, risk language, and what to look at next |
| [contracko-create](skills/contracko-create/SKILL.md) | A new agreement, from questions through filing the signed PDF |

## Get help

- **How Contracko works** (contracts, billing, your workspace) — [docs](https://contracko.com/docs) or [contact us](https://contracko.com/contact)
- **Something wrong with installing these skills** — [open a GitHub issue](https://github.com/contracko/contracko-skills/issues)

MIT licensed.
