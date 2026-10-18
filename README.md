# Contracko skills

**AI contract management MCP server by Contracko.** Manage your business contracts with Claude, ChatGPT, Codex, Gemini, Copilot, Cursor, Grok, and other AI tools.

[Contracko](https://contracko.com) is AI contract management software, a contract lifecycle management (CLM) workspace for PDFs and Word files with dates, values, parties, and AI analysis on top. This plugin connects Claude and other assistants to that workspace so they can:

- **Review and analyse contracts with AI.** Surface risks, liabilities and obligations, compare two agreements clause by clause, and quote the sentence behind each finding.
- **Import contracts with CLM, without Parser credits.** Add PDF and Word contracts to your register and extract dates, parties and terms, including bulk imports.
- **Process documents in bulk with Contracko Parser.** The separate Parser product uses Parser credits for standalone extraction and exports. It is not needed to add contracts to your contract register.
- **Set automated reminders.** Add notifications to contract events so the right person hears about them in time.
- **Track renewal and notice deadlines.** List what ends, auto-renews, or needs notice in a given window, across the whole portfolio.

These skills teach the assistant how to import, review, organise, and file that work. The MCP server is the live connection to your workspace.

**No account yet?** Start a [7-day free trial](https://contracko.com) (no credit card). You can also create the trial account on the OAuth screen the first time you connect the server.

[Billing and allowances](skills/contracko/SKILL.md#billing-and-allowances) covers CLM and Parser.

## Usage

Once connected, talk to the assistant the way you would a colleague. These are the jobs people actually run:

| Try asking | What it does |
|---|---|
| I just signed up. Add this contract to Contracko. | Finds the right steps for a first contract, uploads the file, files it, and reads the new record back. |
| We are onboarding. Pull every PDF from this folder, and from our Drive / SharePoint / Box contracts library, into Contracko. | Finds the files (on disk or in cloud storage you already have connected), checks the set with you, downloads or fetches cloud files, imports them, and lets Contracko extract dates, parties, and types. |
| I do not want silent renewals. What needs notice, ends, or auto-renews in the next quarter? Set reminders for all of it. | Lists the dates that matter today, then creates notifications on those contracts so you are notified in time. |
| Compare Acme's MSA to Beta's. Who has the better liability cap, termination, and data-processing terms? | Puts both records side by side, with quoted clauses, so you can choose. |
| Audit our vendor contracts for uncapped liability, one-sided indemnities, and missing notice periods. | Walks the portfolio, flags the risk language, and quotes the sentence behind each finding. |
| Our filing is a mess. Set up MSA, NDA, SOW, and DPA with the fields we actually use, then put each contract in the right folder. | Shapes types and fields, shows visible folders, confirms the destination, then creates folders or files contracts as requested. |
| What should we look at this month? What is urgent, and what are we missing? | Ranks the workspace by urgency and gaps, with a count of how much it looked at. |
| Walk me through a new NDA, send it for signature, and file the signed PDF when it comes back. | Runs the questionnaire, then files the executed copy. Drafting and signing still happen in Contracko. |

## Security

Contracko does not train models on your contracts. Analysis inside the product runs under commercial API terms, with Zero Data Retention where we have it, and we work to get ZDR with every AI subprocessor. See [Security](https://contracko.com/features/security).

Connecting this plugin is different: when Claude, ChatGPT, Codex, or another assistant calls Contracko, contract text is sent to *that* product. Contracko cannot control what they do with it. Turn off model training in that product before using real contracts.

### Local upload policy

Local uploads and client network settings: [import skill](skills/contracko-import/SKILL.md#working-the-upload-path).

## Install

**Using Claude?** Add Contracko from Claude's connector directory: [claude.ai/directory/connectors/contracko](https://claude.ai/directory/connectors/contracko). Open the **Claude** or **Claude Code** section below for the details.

For every other assistant, you connect to Contracko in two steps:

1. **Add the skills** (this repo) so it knows how to help with contracts.
2. **Add the connection** so it can reach your workspace. Paste this address when asked:

```
https://app.contracko.com/mcp
```

A browser opens. Sign in or start the free trial, choose your workspace, then review and approve access. Adding skills alone does not connect the workspace. Reuse an existing Contracko connection.

The consent screen offers **View contracts** for questions and reviews, and **Add and edit contracts** for imports or changes. Requested permissions start selected. Untick **Add and edit contracts** unless you want imports or changes; it is offered only when your workspace role allows it. Each permission has an info button with details. When write access is requested, the screen offers a copyable prompt to add a contract in any workspace; select **Add and edit contracts** to copy it.

OAuth prefers Client ID Metadata Documents (CIMD) for HTTPS metadata-document client IDs, with Dynamic Client Registration (DCR) as fallback. This is transparent to users; connection steps stay the same.

Clients without OAuth can use a workspace-bound key created in Contracko for purpose **MCP server**, stored in the client's secret settings. Never paste the credential into chat, source code or logs.

Release bundles and directory submissions: [Distribution](DISTRIBUTION.md).

Open the section for the product you use.

<details>
<summary><strong>Claude</strong> (web, desktop, mobile, Cowork)</summary>

1. Open [https://claude.ai/directory/connectors/contracko](https://claude.ai/directory/connectors/contracko), choose **Connect to Claude** and sign in to Contracko.
2. On Pro and above you can also install the **Contracko** plugin (**Customize, Plugins**) for the four contract skills, then connect from its **Connectors** tab.

The directory connector works on every Claude plan, including Free. On Team and Enterprise, an Owner enables it first. Once connected on web or desktop, it also works in the Claude mobile app.

Added Contracko as a custom connector before? Remove that one, or you will see every tool twice.

Contract uploads: [import skill](skills/contracko-import/SKILL.md#getting-the-bytes-there).

On the Free plan you can still add the skills by hand: download them from [Releases](https://github.com/contracko/contracko-skills/releases/latest) and upload each one under **Customize, Skills**.

</details>

<details>
<summary><strong>Claude Code</strong></summary>

Signed in with your Claude account? A connector added in Claude is already available here.

For the skills, install the plugin, which also registers the connection:

```
/plugin marketplace add https://github.com/contracko/contracko-skills.git
/plugin install contracko@contracko
```

Paste that full GitHub address (not a short `owner/repo` name). Run `/mcp`, then follow the [sign-in and consent steps](#install).

Using an API key without the plugin? Run this only if `claude mcp list` shows no Contracko entry:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

If you installed the older `contracko-skills` plugin, remove that plugin and install `contracko@contracko` after updating the marketplace. The GitHub repository remains `contracko/contracko-skills`; the MCP connection remains `contracko`.

Contract uploads: [import skill](skills/contracko-import/SKILL.md#getting-the-bytes-there).

</details>

<details>
<summary><strong>ChatGPT</strong></summary>

1. In the workspace, go to **Settings → Plugins → Import marketplace** and enter `contracko/contracko-skills`.
2. Turn on **Developer mode**.
3. Go to **Settings → Apps → Create** and paste `https://app.contracko.com/mcp`.
4. Follow the [sign-in and consent steps](#install).

ChatGPT has no settings file for this. Use the screens above.

Contract uploads: [import skill](skills/contracko-import/SKILL.md#getting-the-bytes-there).

</details>

<details>
<summary><strong>Grok</strong> (grok.com)</summary>

1. Open [grok.com/connectors](https://grok.com/connectors).
2. Add `https://app.contracko.com/mcp`.
3. Follow the [sign-in and consent steps](#install).

For Grok in the terminal, see **Any other assistant** below.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
codex mcp add contracko --url https://app.contracko.com/mcp
codex mcp login contracko
```

Follow the [sign-in and consent steps](#install).

</details>

<details>
<summary><strong>Cursor</strong></summary>

The Cursor plugin is not yet listed in the public Marketplace. [Distribution status](DISTRIBUTION.md#status).

To test the plugin locally, clone this repository into `~/.cursor/plugins/local/contracko-skills`, reload Cursor, and check **Customize**. Follow the [sign-in and consent steps](#install).

For manual installation without the plugin:

```bash
npx skills@latest add contracko/contracko-skills
```

Then add this to `.cursor/mcp.json` in your project (create the file if it is not there):

```json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

Restart Cursor if it does not pick up the connection, then follow the [sign-in and consent steps](#install).

</details>

<details>
<summary><strong>Cline</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
```

Then open the Cline panel, go to the **Configure** tab, and add this to the MCP settings JSON (the CLI reads `~/.cline/mcp.json`):

```json
{ "mcpServers": { "contracko": { "type": "streamableHttp", "url": "https://app.contracko.com/mcp" } } }
```

Follow the [sign-in and consent steps](#install). Set `"type": "streamableHttp"`; omitting it selects the older SSE transport.

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

Follow the [sign-in and consent steps](#install).

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

Follow the [sign-in and consent steps](#install).

</details>

<details>
<summary><strong>OpenClaw</strong></summary>

Use the [OpenClaw setup](packaging/openclaw/README.md) for its native MCP commands. Follow the [sign-in and consent steps](#install).

</details>

<details>
<summary><strong>Hermes</strong></summary>

Use the [Hermes setup](packaging/hermes/README.md) for its native configuration and login command. Follow the [sign-in and consent steps](#install).

</details>

<details>
<summary><strong>Goose and other stdio clients</strong></summary>

These clients spawn a local process instead of opening the HTTP endpoint themselves:

```bash
npx -y @contracko/mcp
```

That package only launches the hosted server at `https://app.contracko.com/mcp`. It is not a second MCP implementation. Skills still install with `npx skills add https://contracko.com`.

</details>

<details>
<summary><strong>Any other assistant</strong></summary>

For agents, use the [hosted setup prompt](https://contracko.com/mcp/install/prompt.md). Human connection steps are above.

</details>

## Skills

Four playbooks. You do not have to pick one; asking in plain language is enough.

| Skill | Use it for |
|---|---|
| [contracko](skills/contracko/SKILL.md) | Connecting, then organising types, fields, and counterparties |
| [contracko-import](skills/contracko-import/SKILL.md) | Bringing PDFs and Word files in from disk, Drive, SharePoint, Box, or a link |
| [contracko-review](skills/contracko-review/SKILL.md) | Notice dates, notifications, comparisons, risk language, and what to look at next |
| [contracko-create](skills/contracko-create/SKILL.md) | A new agreement, from questions through filing the signed PDF |

## Get help

Want guidance on Contracko? Read the [docs](https://contracko.com/docs) or [contact us](https://contracko.com/contact). That covers the product, your workspace, and anything else you want to talk through.

Policies: [privacy policy](https://contracko.com/legal/privacy-policy) and [terms of service](https://contracko.com/legal/terms-of-service).

Have a question about these skills, a suggestion, or an improvement? [Open a GitHub issue](https://github.com/contracko/contracko-skills/issues).

## Contributing

Before publishing skill changes, run `python3 -m unittest discover -s tests -v`.
See [validation and catalog refresh](tests/README.md) and the [workflow regression cases](tests/workflow-cases.md).

### Release sync

After each MCP release reaches production, check the app's `main`, sync the skills, follow [Versioning](DISTRIBUTION.md#versioning), add [release notes](CHANGELOG.md), and run the checks above. The app checklist is tracked in CTD-5544.

MIT licensed.
