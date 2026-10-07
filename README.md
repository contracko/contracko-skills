# Contracko skills

**AI contract management MCP server by Contracko.** Manage your business contracts with Claude, ChatGPT, Codex, Gemini, Copilot, Cursor, Grok, and other AI tools.

[Contracko](https://contracko.com) is AI contract management software, a contract lifecycle management (CLM) workspace for PDFs and Word files with dates, values, parties, and AI analysis on top. This plugin connects Claude and other assistants to that workspace so they can:

- **Review and analyse contracts with AI.** Surface risks, liabilities and obligations, compare two agreements clause by clause, and quote the sentence behind each finding.
- **Extract and parse contract data.** Import PDF and Word contracts and let Contracko extract dates, parties, renewal and notice terms, governing law and liability terms, or parse a document without filing it.
- **Set automated reminders.** Add notifications to contract events so the right person hears about them in time.
- **Track renewal and notice deadlines.** List what ends, auto-renews, or needs notice in a given window, across the whole portfolio.

These skills teach the assistant how to import, review, organise, and file that work. The MCP server is the live connection to your workspace.

**No account yet?** Start a [7-day free trial](https://contracko.com) (no credit card). You can also create the trial account on the OAuth screen the first time you connect the server.

## Usage

Once connected, talk to the assistant the way you would a colleague. These are the jobs people actually run:

| Try asking | What it does |
|---|---|
| I just signed up. Add this contract to Contracko. | Finds the right steps for a first contract, uploads the file, files it, and reads the new record back. |
| We are onboarding. Pull every PDF from this folder, and from our Drive / SharePoint / Box contracts library, into Contracko. | Finds the files (on disk or in cloud storage you already have connected), checks the set with you, imports them, and lets Contracko extract dates, parties, and types. |
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

Upload contract bytes **only to the `uploadUrl` returned by `clm_create_upload_url`**, unchanged, after checking HTTPS, the exact host `app.contracko.com`, and the `/mcp/files/v1.` path prefix. Never send a contract to a third-party host or file-sharing service to work around an upload failure or a policy block.

For a PDF, the assistant must execute one literal command:

```bash
curl -T "<file>" -H "Content-Type: application/pdf" "<uploadUrl>"
```

At execution, substitute the local path and real returned URL directly inside the quotes. The `Content-Type` header is required by the server; use the declared MIME type for non-PDF files. Run it as one command, with no chaining, subshell, URL file, variable, extra destination, or added curl options. Do not follow redirects. This plain curl command does not display HTTP status, and exit code zero alone does not prove the bytes arrived. A completed command with no transport error or upload-error response permits the next intake call, not a success claim. Contracko validates the stored bytes at intake; confirm filing only from a successful tool result and read-back. If intake returns `UPLOAD_NOT_RECEIVED`, stop and tell the user or use an offered fallback.

If curl fails or execution policy blocks it, stop and tell the user. Offer inline import only for files <=35 MiB that also fit the live tool's file and encoded-payload limits, or the `clm_create_upload_session` upload link. The [import skill](skills/contracko-import/SKILL.md#managed-import) lists the pinned release's smaller limits. Keep policy intact and do not try another host.

For **Cursor**, allow only this shell entry:

```text
Shell(curl:*https://app.contracko.com/mcp/files/v1.*)
```

Pair it with network egress restricted to **`app.contracko.com` only** and command denials. Apply the same host-only network restriction and command validation in **Codex** and **Claude** execution environments where local uploads run. Do not enable general egress or broadly allow `curl`. If the client cannot enforce these restrictions, keep uploads approval-gated or use the fallback above.

Deny commands containing a second `://`, even when one URL matches the allow entry. Deny the standalone flag arguments `-x`, `--proxy`, `--resolve`, `--connect-to`, `-k`, `--insecure`, `-K`, and `--config`. The one-command shape also excludes other options and attached option forms. Match flags as arguments, not as arbitrary substrings: base64url upload tokens can legitimately contain `-K`-like text. A host string inside a command is not proof of its destination; the shell glob must not stand alone as the security boundary.

## Install

**Using Claude?** Add Contracko from Claude's connector directory: [claude.ai/directory/connectors/contracko](https://claude.ai/directory/connectors/contracko). Open the **Claude** or **Claude Code** section below for the details.

For every other assistant, you connect to Contracko in two steps:

1. **Add the skills** (this repo) so it knows how to help with contracts.
2. **Add the connection** so it can reach your workspace. Paste this address when asked:

```
https://app.contracko.com/mcp
```

A browser window will open. Sign in to Contracko, or start the free trial there, then approve access on the consent screen. That is the whole flow. Adding the skills does not connect the workspace on its own. If Contracko is already listed in that assistant, skip step 2.

On the consent screen, tick **Read** so it can answer questions. Tick **Write** only if it should add or change contracts. Leave **Write** off unless you want that.

Once connected, the assistant can see up to 52 Contracko tools, depending on what you approved. It can search them itself, so you do not need to know any tool names. Most assistants stay signed in; if one asks you to sign in again, repeat the browser step.

The canonical Agent Plugins v1 skills package is generated at [`packages/agent-plugin/`](packages/agent-plugin/). It is skills-only. Connect `https://app.contracko.com/mcp` through the host client's native MCP and OAuth flow.

Open the section for the product you use.

<details>
<summary><strong>Claude</strong> (web, desktop, mobile, Cowork)</summary>

1. Open [https://claude.ai/directory/connectors/contracko](https://claude.ai/directory/connectors/contracko), choose **Connect to Claude** and sign in to Contracko.
2. On Pro and above you can also install the **Contracko** plugin (**Customize, Plugins**) for the four contract skills, then connect from its **Connectors** tab.

The directory connector works on every Claude plan, including Free. On Team and Enterprise, an Owner enables it first. Once connected on web or desktop, it also works in the Claude mobile app.

Added Contracko as a custom connector before? Remove that one, or you will see every tool twice.

To add a contract in claude.ai, Claude Desktop chat, Cowork, or the mobile app, attach the file to the chat. It lands in Claude's code-execution sandbox, which blocks outbound hosts by default, so allow Contracko once:

1. Open **Settings > Capabilities**.
2. Under **Code execution and file creation**, allow network egress, if available.
3. Add `app.contracko.com` under **Additional allowed domains**.

Claude then uploads the attached contract itself through Contracko's prepared upload URL. On Team and Enterprise, an Owner opens **Organization settings > Capabilities > Package managers + specific domains** and adds `app.contracko.com` once for all members. Without it, Claude sends only a tiny file inline, or gives you an upload link to add the file in your browser.

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

Paste that full GitHub address (not a short `owner/repo` name). Then run `/mcp` and sign in in the browser.

Using an API key without the plugin? Run this only if `claude mcp list` shows no Contracko entry:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

If you installed the older `contracko-skills` plugin, remove that plugin and install `contracko@contracko` after updating the marketplace. The GitHub repository remains `contracko/contracko-skills`; the MCP connection remains `contracko`.

To add a contract, give Claude Code the file's path. It uploads the file from your own shell, so the bytes never pass through the chat. Approve the upload command when Claude Code asks. If a strict sandbox blocks network access, allow `app.contracko.com` in its sandbox or network settings.

</details>

<details>
<summary><strong>ChatGPT</strong></summary>

1. In the workspace, go to **Settings → Plugins → Import marketplace** and enter `contracko/contracko-skills`.
2. Turn on **Developer mode**.
3. Go to **Settings → Apps → Create** and paste `https://app.contracko.com/mcp`.
4. Sign in in the browser that opens.

ChatGPT has no settings file for this. Use the screens above.

To add a contract, attach the file to the chat and ask ChatGPT to import it. If the attachment does not reach Contracko, ChatGPT gives you an upload link where you add the file in your browser.

</details>

<details>
<summary><strong>Grok</strong> (grok.com)</summary>

1. Open [grok.com/connectors](https://grok.com/connectors).
2. Add `https://app.contracko.com/mcp`.
3. Sign in in the browser that opens.

For Grok in the terminal, see **Any other assistant** below.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
npx skills@latest add contracko/contracko-skills
codex mcp add contracko --url https://app.contracko.com/mcp
codex mcp login contracko
```

Sign in in the browser that opens. For local uploads, apply the [host-only upload policy](#local-upload-policy) rather than enabling general network access.

</details>

<details>
<summary><strong>Cursor</strong></summary>

This repository includes a Cursor plugin manifest at `.cursor-plugin/plugin.json`. It bundles the four existing skills and the MCP connection in `mcp.json`; no API key is included. The plugin is not yet listed in the public Cursor Marketplace.

To test the plugin locally, clone this repository into `~/.cursor/plugins/local/contracko-skills`, reload Cursor, and check **Customize** for the skills and MCP server. Connect Contracko and complete OAuth in the browser. Approve **Read** by default and **Write** only when needed. If you already added the same server manually, use one connection rather than enabling both.

For manual installation without the plugin:

```bash
npx skills@latest add contracko/contracko-skills
```

Then add this to `.cursor/mcp.json` in your project (create the file if it is not there):

```json
{ "mcpServers": { "contracko": { "url": "https://app.contracko.com/mcp" } } }
```

Restart Cursor if it does not pick up the connection, then sign in in the browser. For local uploads, apply the [narrow shell allow entry and host-only upload policy](#local-upload-policy).

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

Sign in in the browser that opens. Set `"type": "streamableHttp"`, because leaving it out falls back to the older SSE transport.

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

For the thin wrapper, download [contracko-openclaw.zip](https://github.com/contracko/contracko-skills/releases/latest/download/contracko-openclaw.zip), extract it, and install the directory through OpenClaw's normal bundle flow. The archive contains the four skills only. It does not register or authenticate an MCP server.

For a skills-only install, run `npx skills@latest add contracko/contracko-skills`.

If you already have the skills, use the native setup below. Check for an existing `contracko` entry first and do not add a second connection:

```bash
openclaw mcp set contracko '{"url":"https://app.contracko.com/mcp","transport":"streamable-http"}'
openclaw mcp configure contracko --auth oauth
openclaw mcp login contracko
```

Run those commands only after explicitly approving the new central entry. Sign in in the browser that opens and choose **Read** or **Write** scopes yourself.

</details>

<details>
<summary><strong>Hermes</strong></summary>

For the thin wrapper, download [contracko-hermes.zip](https://github.com/contracko/contracko-skills/releases/latest/download/contracko-hermes.zip), extract it, and install the directory through Hermes's normal plugin flow. Review and enable the package explicitly. The archive contains the four skills only. It does not write MCP configuration or credentials.

For a skills-only install, run `npx skills@latest add contracko/contracko-skills`.

If you already have the skills, check `~/.hermes/config.yaml` for an existing `mcp_servers.contracko` entry first. If none exists, explicitly approve adding this entry while preserving the rest of the file:

```yaml
mcp_servers:
  contracko:
    url: "https://app.contracko.com/mcp"
    auth: oauth
```

Run `hermes mcp login contracko` and sign in in the browser. Choose **Read** or **Write** scopes yourself.

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

Paste this into the assistant and let it follow the file:

```
Fetch and follow https://contracko.com/mcp/install/prompt.md
```

If you are adding the connection yourself, the address is still `https://app.contracko.com/mcp`. Sign in in a browser. Do not add Contracko twice if it is already connected.

Step-by-step recipes: [agent-setup/prompt.md](agent-setup/prompt.md).

</details>

### Adding contract files from Codex and Cursor

- **Codex CLI:** the default sandbox has no network, so set `sandbox_workspace_write.network_access = true` for the upload, with egress limited to `app.contracko.com` where possible. Non-interactive runs need approval for the import tool.
- **Cursor CLI:** allow one plain `curl -T "<file>" -H "Content-Type: <mimeType>" "<uploadUrl>"` command and network access to `app.contracko.com` only.
- **Cursor web:** attachments are limited to 4 MB, so the assistant gives you an upload link instead.

Contract files go only to Contracko's own upload address, never to a third-party host. If an upload is blocked, the assistant stops and tells you.

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

After each Contracko MCP release reaches production, open a skills-bundle sync PR for that release's agent-facing changes. Check what is live on the app's `main` (not staging or open PRs), update the skills to match, bump the version, add a changelog entry, and run the checks above. The checklist step on the app side is tracked in CTD-5544.

MIT licensed.
