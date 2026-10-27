# Distribution

How these skills and the Contracko MCP server reach a user, per client. Working notes, not marketing copy.

The bundle is a GitHub repo with one skill, `skills/contracko/SKILL.md`, and workflow references loaded on demand. Every path below is a different way of moving that folder, or that server, to a user.

## Status

| Path | Mechanism | State |
|---|---|---|
| Public GitHub repo `contracko/contracko-skills` | this directory as the repo root | created; every official directory pins this URL |
| Claude Code | plugin marketplace, `/plugin install contracko@contracko` | ready from this repo; the plugin's `.mcp.json` registers the server, so no `claude mcp add` after it |
| Claude Desktop / claude.ai chat | directory connector first; one `contracko.zip`, uploaded by hand, as the Free-plan skills path | zips build on release |
| Claude Connectors Directory | remote MCP listing in Claude.ai | live (Community) at [claude.ai/directory/connectors/contracko](https://claude.ai/directory/connectors/contracko); the primary path on every Claude surface |
| Claude plugin directory (Cowork + Claude Code) | public GitHub plugin, `claude plugin validate` then Anthropic form | listed; tracks `main`, so a merge to `main` auto-publishes. Paid plans only |
| Codex / ChatGPT | `.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json` for workspace import; `contracko-agent-plugin-chatgpt.zip` for ChatGPT portal upload | workspace import ready; public Plugin Directory needs OpenAI review |
| Cursor Marketplace | [Contracko listing](https://cursor.com/marketplace/contracko) | live; published by the Cursor team on 2026-10-02; manual refresh on request to marketplace-publishing@cursor.com. Updates are not pulled automatically from GitHub; resubmitting creates duplicates. |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` | ready for `copilot plugin marketplace add contracko/contracko-skills` |
| Gemini CLI | install skills from the public GitHub repo | no third-party marketplace; GitHub install only |
| OpenClaw | generated Agent Plugins v1 content bundle | release artifact; native MCP registration and OAuth remain user-owned |
| Hermes | generated Agent Plugins v1 content bundle | release artifact; native MCP registration and OAuth remain user-owned |
| Agent Plugins Directory | `packages/agent-plugin/plugin.json` in the public Git tree | canonical package with skills and an MCP descriptor; nested manifest is crawler-discoverable; native MCP registration and OAuth remain user-owned |
| Other coding agents | `npx skills add https://contracko.com` | ready once production serves `/.well-known/skills/index.json` (site PR [contracko/contracko-site#693](https://github.com/contracko/contracko-site/pull/693) merged) |
| Goose and other stdio MCP clients | `npx -y @contracko/mcp` | launcher in `packages/mcp`; publishes to the public npm registry, not GitHub Packages. Proxies stdio to `https://app.contracko.com/mcp`. Not a second MCP server. First version is a local `npm publish`; later versions `npm stage publish` from `release.yml` (OIDC), then a maintainer `npm stage approve` with 2FA. |

`.mcp.json` is intentional (CTO-791): the Claude plugin registers its server. Client connection and consent steps live in [README.md](README.md#install); [agent-setup/prompt.md](agent-setup/prompt.md) is the copyable installer prompt.

## The two audiences are not the same person

Nearly every published distribution pattern is a developer-tool pattern: `npx`, `claude plugin install`, editing `.cursor/mcp.json`. A contract manager will do none of it. So the docs page splits at the top:

**Path A, the contract manager.** A remote MCP server with OAuth, added through their client's connector UI, ideally from a directory listing so it is a button rather than a URL. Ends with a first prompt to try, because the activation event is an answer, not a config file.

**Path B, the coding agent.** One line: `npx skills add https://contracko.com`. Connection steps live in [README.md](README.md#install).

## Claude chat needs zips, and the repo has to serve them

Uploading to claude.ai and Claude Desktop chat takes **one ZIP, `contracko.zip`**, containing `contracko/SKILL.md` and `contracko/references/`. The folder name matches the frontmatter `name`. `contracko-chat.zip` remains a byte-identical compatibility alias; no retired per-skill ZIPs are built. Users updating from four skills upload this ZIP and delete `contracko-import`, `contracko-review` and `contracko-create`, or reinstall/update the plugin. [.github/workflows/release.yml](.github/workflows/release.yml) builds them on every tag and attaches them, which gives permanent URLs:

```
https://github.com/contracko/contracko-skills/releases/latest/download/contracko.zip
```

`latest` always resolves to the newest release, so a docs page hard-codes those once and never edits them.

Upload and enable steps: [README Claude section](README.md#install).

### Gotchas that will bite users

- **Never GitHub's green "Download ZIP" button.** It wraps everything in `<repo>-main/` and the uploader rejects it. Bold line on the docs page.
- **Code execution must be enabled** at Settings > Capabilities, or Organization settings > Skills for Team and Enterprise. Skills are gated behind it even when, as here, they run no code. This is why the menu looks missing.
- **Uploaded is not enabled**, and a conversation that predates the toggle does not pick the skill up.
- **Updates are manual in chat.** No auto-update, no notification. Nobody has solved this; every vendor routes around it by pushing people to a plugin, or by moving anything that can be server-side to the server. Do not build a version-check into the skill body: the one person who tried it burned tokens on every invocation and abandoned it.

### The 200-character cap is real

Anthropic documents it: **claude.ai limits `description` to 200 characters**, where the spec allows 1024 and Claude Code truncates a combined description at 1,536. The single description here is written to at most 200, which is valid on every surface. Keep it that way, and spend the budget on trigger words rather than prose.

Same constraint on frontmatter: claude.ai, the Skills API and `package_skill.py` accept only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Any Claude-Code-only field is a hard upload error, not a silent ignore. The skill carries `name` and `description` only, deliberately.

## Versioning

Starting with **1.1.0**, every public Contracko skills, plugin, extension, MCP Registry and npm package version uses one value. [`packaging/manifest.json`](packaging/manifest.json) is the source of truth. Dependency pins and schema/protocol versions keep their own versions. Historical releases used separate version lines.

For each release, bump only the source version, copy that value into every public manifest and the npm lockfile's root package fields, then regenerate `packages/agent-plugin/` with `python3 scripts/build_release_artifacts.py --write-directory`. These mirrors have no independent version counters. Run `python3 scripts/check_versions.py --tag vX.Y.Z`: it fails on any public version drift or a mismatched tag. Validation CI, release CI and `build-zips.sh` enforce the rule.

Type the ChatGPT and Claude developer portal version as exactly this value, for example `1.1.3`, without a `v` prefix. The Git release tag is `v1.1.3`. Portal values are manual and cannot be checked by repository CI. The plugin cache is keyed on the version, so bump it for changes users should receive.

The live ChatGPT listing is `plugin_asdk_app_6ac8e9b10f548191ab1ed190c3b0ccab`; its accepted 1.1.0 ZIP uses `.codex-plugin/plugin.json` name `contracko`. The former listing and its `app-...` naming rule are retired. The mapping lives in [`packaging/directory-listings.json`](packaging/directory-listings.json), separate from the standard manifest so it does not enter other packages. The approved listing copy lives in [`packaging/chatgpt/plugin.json`](packaging/chatgpt/plugin.json); this template omits `name` and `version`, which the builder inserts from the mapping and unified version. `check_versions.py` requires both files to parse and rejects malformed mappings or conflicting template names and versions if stored. The ChatGPT ZIP preserves the accepted manifest identity, icon and `.mcp.json` declaration for the existing MCP connection. It embeds corrected review cases and publication release notes. After captain approval to submit, upload `contracko-agent-plugin-chatgpt.zip` to that same portal listing with the unified version. Use `contracko-agent-plugin.zip` for every other directory, where the name remains `contracko`.

### Manual release checklist

After each release, complete the manual steps for these surfaces:

- **Cursor Marketplace:** request a refresh of the [existing listing](https://cursor.com/marketplace/contracko) from Cursor's marketplace team at marketplace-publishing@cursor.com. GitHub updates are not pulled automatically. Do not resubmit: that creates duplicate listings.
- **ChatGPT portal:** after approval to submit, upload `contracko-agent-plugin-chatgpt.zip` to the existing listing with the unified version.
- **npm:** after release CI stages `@contracko/mcp`, a maintainer runs `npm stage approve` with 2FA.

## What Contracko has to do server-side

None of this is in this repo, and all of it gates the good distribution paths.

- **Connectors Directory listing.** Done: live at `https://claude.ai/directory/connectors/contracko`. Keep every tool carrying a `title` plus `readOnlyHint` or `destructiveHint`; a directory reviewer and a model want the same thing, which is to know whether calling a tool changes anything. Directory rank counts distinct accounts using the directory server, so custom-connector installs do not count toward it.
- **Skills discovery at a well-known path.** `https://contracko.com/.well-known/skills/index.json` makes `npx skills add https://contracko.com` work and turns a docs deploy into the release. Stripe does exactly this. Shipped in site PR 693; live after that production deploy.
- **Canonical install prompt.** `https://contracko.com/mcp/install/prompt.md`, plain markdown, no auth, no HTML wrapper. There is no `/agent-setup/prompt.md` on the site; that path 404s and should not be documented.
- **A read-only connection variant.** For contract data, a documented read-only URL is a trust feature rather than a footnote, and it is what an IT team asks for first.
- **Public npm for `@contracko/mcp`.** Goose and other stdio clients run `npx -y @contracko/mcp`. That package lives in `packages/mcp`. The first version is published locally (account 2FA). Later versions are staged from the `v*` release workflow via npm trusted publishing (OIDC, `npm stage publish` only — no long-lived `NPM_TOKEN`), then a maintainer runs `npm stage approve` with 2FA. GitHub Packages is the wrong registry for this: Goose cannot fetch it. The launcher is not a second MCP server.

## Not this

An MCP tool that points at this repo so a model can fetch its own instructions. Raised and rejected: MCP tools carry their own context and must be standalone interpretable. Skills may reference the server; the server does not reference the skills.

That principle has a consequence worth holding Contracko to. Some write tools still ship thin parameter descriptions, and some errors name no constraint. A tool cannot stand alone and say nothing about itself, and the same gap fails the directory's tool-description bar.

## Cross-client landscape, September 2026

Three standards now cover nearly everything, so a vendor shipping from one repo mostly just has to satisfy them.

- **MCP** for tools. Every client supports remote Streamable HTTP; only the wrapper key differs (`url`, `httpUrl`, `serverUrl`, `context_servers`, `streamableHttp`). Verified shapes and config paths per client live in [`https://contracko.com/mcp/install/prompt.md`](https://contracko.com/mcp/install/prompt.md).
- **Agent Skills / `SKILL.md`** became an open standard, and is now read by Codex (`.agents/skills/`), Copilot and VS Code (`.github/skills/`, `.claude/skills/`, `.agents/skills/`), Gemini CLI, Cursor, Cline and Zed. The format here is already the portable one.
- **Agent Plugins 1.0**, announced August 2026 by Amazon, Cursor, Microsoft, OpenAI, Vercel and Google: one directory with `plugin.json` + `skills/` + `mcp.json`, launching in ChatGPT, Codex, Cursor, Copilot, VS Code and Kiro. Anthropic is not a member, so it does not replace the Claude plugin format.

Agent Plugins v1 package layouts and the two directory ZIPs: [directory package](packaging/directory/README.md). OpenClaw/Hermes bundles contain skills only, without MCP descriptors. Native MCP registration, OAuth, credential storage and consent remain host-owned.

The release builder renders the directory package and bundles from `skills/` and `packaging/manifest.json`, using `packaging/chatgpt/plugin.json` for ChatGPT listing copy and `packaging/directory-listings.json` for its name. Only the ChatGPT ZIP overlays the complete skill variants in `packaging/chatgpt/skills/` to remove product commerce and standalone processing instructions. All other platforms retain canonical skill bytes. [ChatGPT submission notes](packaging/chatgpt/README.md) document the embedded review cases, release notes, compatibility baseline and strict scan allowlist. It fixes archive ordering and timestamps, stores entries without compression, and runs in the existing release workflow. Both Agent Plugins ZIPs are deterministic for identical files, config and version. The generic archive also records the source commit in `RELEASE-METADATA.json`, so changing that commit changes its hash. The ChatGPT archive has no source-commit metadata and keeps the same bytes when only the commit changes. PR validation also builds the candidate and uploads the ChatGPT ZIP with its SHA-256 in the job summary. Official packages are built by the release workflow from the tagged main commit. The workflow attaches `dist/*.zip`, including both Agent Plugins assets. No host software, OAuth client, credential store, or background updater is shipped.

`skills/` is canonical; generated mirrors are never hand-edited. Regenerate with `python3 scripts/build_release_artifacts.py --write-directory`. CI and `build-zips.sh` use `--check-directory` to reject missing, extra, changed or symlinked entries, including descriptor drift. The builder's `SKILLS` contains only `contracko`; keep the canonical and generated trees identical. Root `mcp.json` supplies the descriptor; `.mcp.json` is Claude-only.

The generated manifest follows the [Agent Plugins v1 specification](https://agent-plugins.org/specification/). The host flows follow [OpenClaw bundle mapping](https://github.com/openclaw/openclaw/blob/2f8cd215e92320703237b8def415b691f15f3b56/docs/plugins/bundles.md) and [Hermes portable package guidance](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins).

Release assets:

- `https://github.com/contracko/contracko-skills/releases/latest/download/contracko-agent-plugin-chatgpt.zip` (ChatGPT portal upload)
- `https://github.com/contracko/contracko-skills/releases/latest/download/contracko-agent-plugin.zip` (every other directory)
- `https://github.com/contracko/contracko-skills/releases/latest/download/contracko-openclaw.zip`
- `https://github.com/contracko/contracko-skills/releases/latest/download/contracko-hermes.zip`

Two cheap things worth doing when the docs page is built, both MCP-only and neither carrying skills:

```
Cursor:   cursor://anysphere.cursor-deeplink/mcp/install?name=contracko&config=<base64 of the inner server object>
VS Code:  https://vscode.dev/redirect?url=<urlencoded vscode:mcp/install?{"name":"contracko","type":"http","url":"..."}>
```

## While developing

Follow [Versioning](#versioning) and reinstall after changes, or use `claude --plugin-dir .` to read the working tree. Marketplace updates alone do not refresh a version-pinned plugin. Removing its version makes the cache pin permanent.

Check the installed skill bytes with:

```bash
diff -rq skills ~/.claude/plugins/cache/contracko/contracko/<version>/skills
```

No differences means the install matches.
