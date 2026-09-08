# Contracko skills

**AI contract management MCP server by Contracko.** Manage your business contracts with Claude, ChatGPT, Codex, Gemini, Copilot, Cursor, Grok, and other AI tools.

[Contracko](https://contracko.com) is a contract repository: PDFs and Word files in one workspace, with dates, values, parties, and AI analysis on top. These skills teach an assistant how to import, review, organise, and file that work. The MCP server is the live connection to your workspace.

**No account yet?** Start a [7-day free trial](https://contracko.com) (no credit card). You can also create the trial account on the OAuth screen the first time you connect the server.

## Security

Contracko does not train models on your contracts. Analysis inside the product runs under commercial API terms, with Zero Data Retention where we have it, and we work to get ZDR with every AI subprocessor. See [Security](https://contracko.com/features/security).

Connecting this plugin is different: when Claude, ChatGPT, Codex, or another assistant calls Contracko, contract text is sent to *that* product. Contracko cannot control what they do with it. Turn off model training in that product before using real contracts.

## Install

You connect your assistant to Contracko in two steps:

1. **Add the skills** (this repo) so it knows how to help with contracts.
2. **Add the connection** so it can reach your workspace. Paste this address when asked:

```
https://app.contracko.com/mcp
```

A browser window will open. Sign in to Contracko (or start the free trial there). Adding the skills does not connect the workspace on its own. If Contracko is already listed in that assistant, skip step 2.

When you sign in, tick **Read** so it can answer questions. Tick **Write** only if it should add or change contracts. Leave **Write** off unless you want that.

Open the section for the product you use.

<details>
<summary><strong>Claude</strong> (claude.ai or Claude Desktop)</summary>

1. Download the skill files from [Releases](https://github.com/contracko/contracko-skills/releases/latest) and add them in Claude.
2. Go to **Settings → Connectors → Add custom connector**.
3. Paste `https://app.contracko.com/mcp`.
4. Sign in in the browser that opens.

If Contracko already appears under Connectors, do not add it a second time.

</details>

<details>
<summary><strong>ChatGPT</strong></summary>

1. In the workspace, go to **Settings → Plugins → Import marketplace** and enter `contracko/contracko-skills`.
2. Turn on **Developer mode**.
3. Go to **Settings → Apps → Create** and paste `https://app.contracko.com/mcp`.
4. Sign in in the browser that opens.

ChatGPT has no settings file for this. Use the screens above.

</details>

<details>
<summary><strong>Grok</strong> (grok.com)</summary>

1. Open [grok.com/connectors](https://grok.com/connectors).
2. Add `https://app.contracko.com/mcp`.
3. Sign in in the browser that opens.

For Grok in the terminal, see **Any other assistant** below.

</details>

<details>
<summary><strong>Claude Code</strong></summary>

In Claude Code, run:

```
/plugin marketplace add https://github.com/contracko/contracko-skills.git
/plugin install contracko-skills@contracko
```

Paste that full GitHub address (not a short `owner/repo` name). Then connect:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

Type `/mcp` in the session and sign in in the browser.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
codex mcp add contracko --url https://app.contracko.com/mcp
codex mcp login contracko
```

Sign in in the browser that opens.

</details>

<details>
<summary><strong>Cursor</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

Then add this to `.cursor/mcp.json` in your project (create the file if it is not there):

```json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

Restart Cursor if it does not pick up the connection, then sign in in the browser.

</details>

<details>
<summary><strong>GitHub Copilot</strong> (VS Code)</summary>

```bash
npx skills@latest add contracko/contracko-skills
```

Then add this to `.vscode/mcp.json` in your project:

```json
{ "servers": { "contracko": { "type": "http", "url": "https://app.contracko.com/mcp" } } }
```

Sign in in the browser that opens.

</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

Then add this to `~/.gemini/settings.json`:

```json
{ "mcpServers": { "contracko": { "httpUrl": "https://app.contracko.com/mcp" } } }
```

Sign in in the browser that opens.

</details>

<details>
<summary><strong>OpenClaw</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
openclaw mcp set contracko '{"url":"https://app.contracko.com/mcp","transport":"streamable-http"}'
openclaw mcp configure contracko --auth oauth
openclaw mcp login contracko
```

Sign in in the browser that opens.

</details>

<details>
<summary><strong>Hermes</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

Then add this to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  contracko:
    url: "https://app.contracko.com/mcp"
    auth: oauth
```

Run `hermes mcp login contracko` and sign in in the browser.

</details>

<details>
<summary><strong>Any other assistant</strong></summary>

Paste this into the assistant and let it follow the file:

```
Fetch and execute https://app.contracko.com/agent-setup/prompt.md
```

If you are adding the connection yourself, the address is still `https://app.contracko.com/mcp`. Sign in in a browser. Do not add Contracko twice if it is already connected.

Step-by-step recipes: [agent-setup/prompt.md](agent-setup/prompt.md).

</details>

## Usage

Once connected, talk to the assistant the way you would a colleague. These are the jobs people actually run:

| Try asking | What it does |
|---|---|
| We are onboarding. Pull every PDF from this folder, and from our Drive / SharePoint / Box contracts library, into Contracko. | Finds the files (on disk or in cloud storage you already have connected), checks the set with you, imports them, and lets Contracko extract dates, parties, and types. |
| I do not want silent renewals. What needs notice, ends, or auto-renews in the next quarter? Set reminders for all of it. | Lists the dates that matter today, then creates reminders on those contracts so you are notified in time. |
| Compare Acme's MSA to Beta's. Who has the better liability cap, termination, and data-processing terms? | Puts both records side by side, with quoted clauses, so you can choose. |
| Audit our vendor contracts for uncapped liability, one-sided indemnities, and missing notice periods. | Walks the portfolio, flags the risk language, and quotes the sentence behind each finding. |
| Our filing is a mess. Set up MSA, NDA, SOW, and DPA with the fields we actually use, then put each contract in the right folder. | Shapes types and fields, shows visible folders, confirms the destination, then creates folders or files contracts as requested. |
| What should we look at this month? What is urgent, and what are we missing? | Ranks the workspace by urgency and gaps, with a count of how much it looked at. |
| Walk me through a new NDA, send it for signature, and file the signed PDF when it comes back. | Runs the questionnaire, then files the executed copy. Drafting and signing still happen in Contracko. |

## Skills

Four playbooks. You do not have to pick one; asking in plain language is enough.

| Skill | Use it for |
|---|---|
| [contracko](skills/contracko/SKILL.md) | Connecting, then organising types, fields, and counterparties |
| [contracko-import](skills/contracko-import/SKILL.md) | Bringing PDFs and Word files in from disk, Drive, SharePoint, Box, or a link |
| [contracko-review](skills/contracko-review/SKILL.md) | Notice dates, reminders, comparisons, risk language, and what to look at next |
| [contracko-create](skills/contracko-create/SKILL.md) | A new agreement, from questions through filing the signed PDF |

## Get help

Want guidance on Contracko? Read the [docs](https://contracko.com/docs) or [contact us](https://contracko.com/contact). That covers the product, your workspace, and anything else you want to talk through.

Have a question about these skills, a suggestion, or an improvement? [Open a GitHub issue](https://github.com/contracko/contracko-skills/issues).

## Contributing

Before publishing skill changes, run `python3 -m unittest discover -s tests -v`.
See [validation and catalog refresh](tests/README.md) and the [workflow regression cases](tests/workflow-cases.md).

MIT licensed.
