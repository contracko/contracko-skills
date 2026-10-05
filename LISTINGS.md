# Directory listings

Where the Contracko MCP server is listed outside the client marketplaces in [DISTRIBUTION.md](DISTRIBUTION.md), and the copy every listing is filled from. Review the shared block once; every entry below is assembled from it.

Two sources propagate on their own. The official MCP Registry entry (published from [server.json](server.json)) is copied by Glama, AllMCPs and mcp.directory. This repo's README is what the GitHub lists and MCP Repository show. Everything else is a one-time submission, so changing the shared block later does not update it.

## Shared block

```
Name            Contracko
Registry name   com.contracko/contracko
Endpoint        https://app.contracko.com/mcp   (remote, Streamable HTTP)
Auth            OAuth 2.0 with dynamic client registration ("OAuth2.1" where a list uses that label)
OAuth scopes    contract:read, contract:write, parser:compute
Local install   npx -y @contracko/mcp   (stdio launcher for the remote server; only where a form demands a package)
Repo            https://github.com/contracko/contracko-skills   (MIT)
Website         https://contracko.com/mcp/contract-management
Docs            https://contracko.com/docs/mcp-server
Install guide   https://contracko.com/mcp/install/prompt.md
Legal/privacy   https://contracko.com/legal
Support         support@contracko.com
Icon            https://app.contracko.com/mcp/icon-512.png   (512x512 PNG)
Pricing         Paid, 7-day free trial, no credit card   ("Freemium" where there is no trial option)
Category        Legal & Compliance; fallback Productivity
Keywords        contracko, contract management, CLM, contracts, renewals, legal, procurement
Clients         Claude, ChatGPT, Codex, Cursor, VS Code, Claude Code, Gemini CLI, Grok
Proof           Listed in Claude's connector directory: https://claude.ai/directory/connectors/contracko
```

**Tagline (45/60)**

> Contract management your AI assistant can use

**Short (84/100).** Identical to the live registry entry, so copied and typed listings match.

> Import, review and track renewals on your business contracts from your AI assistant.

**Medium (156/200).** From the `/mcp/contract-management` meta description.

> Connect your Contracko contract workspace to Claude, ChatGPT, Codex or Cursor. Extract terms, flag risks, review, compare and track renewal dates by asking.

**Long (461).** The `/docs/mcp-server` intro, with the client list limited to clients that work today.

> Contracko's MCP server connects your contract workspace to the AI assistant you already use. Ask Claude, ChatGPT, Codex or Cursor about your contracts and they read the real records: parties, dates, values and the documents themselves. Give them write access and they can import contracts, set reminders and file new agreements for you. You stay in control. Read and write are separate permissions, you choose which to grant, and you can disconnect at any time.

**Second use case.** Add where there is room for tags or a tool list.

> Use parsing MCP to extract contract data in bulk from a pile of files. Same Contracko login for both.

**Trust line.**

> Contracko does not train models on your contracts.

Do not describe Contracko as "AI contract management software". It is contract management software your AI assistant can use.

## Status

As of 2026-10-05. Update the row when a listing changes.

| Directory | Fit | State | Next action |
|---|---|---|---|
| [Official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=contracko) | fit | live, v0.7.3 | publish the current `server.json` (see below) |
| [Glama](https://glama.ai/mcp/connectors/com.contracko/contracko) | fit | live, **Unhealthy** | claim, add a test profile |
| [AllMCPs](https://allmcps.com/api/v1/search?q=contracko) | fit | live, unclaimed, no remote URL | claim, add the endpoint |
| [xAI plugin marketplace](https://github.com/xai-org/plugin-marketplace/pull/594) | fit | PR #594 open since 2026-09-07, unreviewed | re-pin and ask for review |
| [mcpservers.org](https://mcpservers.org/submit) | fit | not listed | form |
| [MobinX/awesome-mcp-list](https://github.com/MobinX/awesome-mcp-list) | fit | not listed | one-line PR |
| [jaw9c/awesome-remote-mcp-servers](https://github.com/jaw9c/awesome-remote-mcp-servers) | fit | not listed | one-row PR; maintainer rarely merges |
| [TensorBlock/awesome-mcp-servers](https://github.com/TensorBlock/awesome-mcp-servers) | fit | not listed | issue form |
| [mcp.directory](https://mcp.directory) | weak | not listed, crawls the registry | recheck 2026-10-12, then submit |
| [MCP Market](https://mcpmarket.com/submit) | weak | not listed | free form, 4-6 week queue |
| [mcp.so](https://mcp.so/submit) | weak | not listed | account + form |
| [MCP Repository](https://mcprepository.com/submit) | weak | not listed | one URL |
| [toolsdk-ai/toolsdk-mcp-registry](https://github.com/toolsdk-ai/toolsdk-mcp-registry) | weak | not listed | JSON PR |
| [collabnix/awesome-mcp-lists](https://github.com/collabnix/awesome-mcp-lists) | weak | not listed | one-row PR, slow merges |
| [AI Indigo](https://aiindigo.com/submit) | skip | not listed | none: a general AI-tools ad directory |

Skip the paid fast lanes (mcpservers.org $39, mcp.so $39, MCP Market $29). They buy a badge and queue position, not reach.

## Per directory

### Official MCP Registry

Live as `com.contracko/contracko` v0.7.3. `server.json` here is ahead of it (0.7.9) and carries a different description. Publishing it changes the text Glama, AllMCPs and mcp.directory show, so settle the description first.

1. `mcp-publisher login dns` (or `http`) for the `contracko.com` namespace, with the key already used for earlier versions.
2. `mcp-publisher publish` from the repo root. Versions are immutable; bump for every change.

### Glama

Auto-listed from the registry, verified, category legal-and-compliance, but shown as **Unhealthy, uptime 0**: its health check cannot get past OAuth. An unhealthy badge costs more credibility than no listing.

1. Sign in to Glama, open the listing, choose **Claim ownership**.
2. Verify with the HTTP challenge: serve the `glama_claim_...` token Glama issues at `https://app.contracko.com/.well-known/glama.json`. That is a change in the app repo, not here. A DNS TXT record also works.
3. **Admin > Test Profile**: give the health check a dedicated test workspace account with Read only. Keep the credentials in Glama and the password manager, never in this repo.
4. Leave registry sync on, so the registry stays the source of truth.

### AllMCPs

Listed from the registry with category Legal, but unclaimed, `remoteUrl` empty, and only the npx install shown.

1. Open the listing, claim it with `support@contracko.com`. Verify by README badge, site badge or DNS.
2. Set: hosted endpoint `https://app.contracko.com/mcp`, auth OAuth, pricing Paid (trial), license MIT, compatible clients from the shared block, description = Short.

### xAI plugin marketplace

[PR #594](https://github.com/xai-org/plugin-marketplace/pull/594) (Budi) adds Contracko to `.grok-plugin/marketplace.json` for Grok Build. CI is green; it has had no review since 2026-09-11 behind a backlog of about 700 items.

1. Re-pin `sha` to current `main` of this repo and rerun `python3 scripts/generate-plugin-index.py` so the index check passes.
2. Comment on the PR: the plugin is skills plus a remote OAuth MCP connection at `https://app.contracko.com/mcp`, its only network endpoint; no local code runs and no credentials are stored. Their CONTRIBUTING says a note like this speeds review.

grok.com/connectors is a separate, curated catalog with no public application. Users can already add Contracko there as a custom connector.

### mcpservers.org

Web form, no account, free review within about two weeks.

| Field | Value |
|---|---|
| Server Name | Contracko |
| Category | Productivity |
| Short Description | Short |
| Repository / Website | https://contracko.com/mcp/contract-management |
| Official MCP Registry Name | com.contracko/contracko |
| Supports remote connections | yes |
| Contact Email | support@contracko.com |

### MobinX/awesome-mcp-list

PR touching only `README.md`, one bullet appended to **⚖️ Legal & Compliance**. Title: `Add contracko/contracko-skills to Legal & Compliance`. Merges usually within a day. The list wants a public repo; this repo holds the skills rather than the server, the same setup as the accepted `Built-AI/prism-mcp` entry.

```markdown
-   **[contracko/contracko-skills](https://github.com/contracko/contracko-skills)** [![GitHub stars](https://img.shields.io/github/stars/contracko/contracko-skills?style=social)](https://github.com/contracko/contracko-skills): Contract management your AI assistant can use: find contracts, read extracted dates, values and parties, review risk and set renewal reminders. Remote server (streamable HTTP, OAuth).
```

### jaw9c/awesome-remote-mcp-servers

One table row in alphabetical position among the C rows (after Carbon Voice). Remote OAuth servers only, which is exactly Contracko. The maintainer has merged one PR since June, so expect a long wait.

```markdown
| Contracko | Document Management | `https://app.contracko.com/mcp` | OAuth2.1 | [Contracko](https://contracko.com) |
```

### TensorBlock/awesome-mcp-servers

Use the [Add MCP server issue form](https://github.com/TensorBlock/awesome-mcp-servers/issues/new?template=add-mcp-server.yml). Merges within hours; afterwards claim the profile with the `claim-profile.yml` form.

| Field | Value |
|---|---|
| Server name | Contracko |
| Project URL | https://github.com/contracko/contracko-skills |
| Best category | Content Management Systems (CMS), the closest to documents; there is no legal category |
| What can an agent do with this server? | Long, plus Second use case |
| Install or connection instructions | Remote endpoint `https://app.contracko.com/mcp`, no environment variables. Setup per client: https://contracko.com/mcp/install/prompt.md. Local clients: `npx -y @contracko/mcp` |
| Transport | Streamable HTTP |
| Auth requirements | OAuth 2.0 with dynamic client registration; scopes `contract:read`, `contract:write`, `parser:compute`. Contracko account required (7-day free trial) |
| Known supported clients | Clients line |
| License | MIT (skills and launcher); the hosted server is proprietary |

### mcp.directory

Imports from the official registry. If Contracko is still missing on 2026-10-12, submit https://github.com/contracko/contracko-skills at [mcp.directory/submit](https://mcp.directory/submit) with the Short description and `support@contracko.com`, then email them to claim it.

### MCP Market

[Submit](https://mcpmarket.com/submit) twice, free:

1. **MCP Server** tab, Remote toggle on, repo https://github.com/contracko/contracko-skills, Try Now link https://contracko.com/mcp/contract-management.
2. **Agent Skill** tab, same repo, for the four skills.

### mcp.so

Needs an account. **Remote Server** tab: repository https://github.com/contracko/contracko-skills, name Contracko, endpoint and auth from the shared block, description Medium.

### MCP Repository

Paste https://github.com/contracko/contracko-skills at [mcprepository.com/submit](https://mcprepository.com/submit). The listing is built from this repo's README.

### toolsdk-ai/toolsdk-mcp-registry

PR adding only `packages/other-tools-and-integrations/contracko.json`. Passes their `node scripts/validate-registry.mjs` with 0 errors, 0 warnings (checked 2026-10-05). Merges come in batches weeks apart.

```json
{
  "type": "mcp-server",
  "name": "Contracko",
  "packageName": "@toolsdk-remote/contracko",
  "description": "Hosted Contracko MCP (OAuth) at https://app.contracko.com/mcp. Connects your contract workspace to your AI assistant: find contracts, read extracted dates, values and parties, review risk, compare agreements, import contracts and set renewal reminders. Requires a Contracko account (7-day free trial).",
  "url": "https://github.com/contracko/contracko-skills",
  "readme": "https://contracko.com/docs/mcp-server",
  "runtime": "node",
  "license": "MIT",
  "logo": "https://app.contracko.com/mcp/icon-512.png",
  "author": "Contracko",
  "env": {},
  "remotes": [
    {
      "type": "streamable-http",
      "url": "https://app.contracko.com/mcp",
      "auth": {
        "type": "oauth2",
        "scopes": ["contract:read", "contract:write", "parser:compute"]
      }
    }
  ]
}
```

### collabnix/awesome-mcp-lists

Optional. One numbered row at the end of **Integrations & APIs**; replace `N` with the next number. One maintainer merges in batches weeks apart.

```markdown
| N | **Contracko** | Hosted remote MCP server for contract management: find contracts, track renewal and notice dates, review risk and import agreements. Streamable HTTP at https://app.contracko.com/mcp, OAuth, Contracko account required. | [GitHub](https://github.com/contracko/contracko-skills) |
```
