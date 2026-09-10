# Distribution

How these skills and the Contracko MCP server reach a user, per client. Working notes, not marketing copy.

The bundle is a GitHub repo with one folder per skill, `SKILL.md` at each folder root. Every path below is a different way of moving that folder, or that server, to a user.

## Status

| Path | Mechanism | State |
|---|---|---|
| Public GitHub repo `contracko/contracko-skills` | this directory as the repo root | created; every official directory pins this URL |
| Claude Code | plugin marketplace, `claude plugin install` | ready from this repo; skills-only, no MCP double-register |
| Claude Desktop / claude.ai chat | one zip per skill, uploaded by hand | zips build on release |
| Claude Connectors Directory | remote MCP listing in Claude.ai | blocked on a Team or Enterprise [claude.ai](https://claude.ai) org (Owners submit from org settings). Tool `title`s and `serverInfo` branding already ship |
| Claude plugin directory (Cowork + Claude Code) | public GitHub plugin, `claude plugin validate` then Anthropic form | skills-only submit is unblocked; connector listing is preferred, not required |
| Codex / ChatGPT workspace import | `.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json` | ready for workspace import; public Plugin Directory needs OpenAI review |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` | ready for `copilot plugin marketplace add contracko/contracko-skills` |
| Gemini CLI | install skills from the public GitHub repo | no third-party marketplace; GitHub install only |
| OpenClaw | generated Agent Plugins v1 content bundle | release artifact; native MCP registration and OAuth remain user-owned |
| Hermes | generated Agent Plugins v1 content bundle | release artifact; native MCP registration and OAuth remain user-owned |
| Agent Plugins Directory | `packages/agent-plugin/plugin.json` in the public Git tree | canonical skills-only package; nested manifest is crawler-discoverable; native MCP registration and OAuth remain user-owned |
| Other coding agents | `npx skills add https://contracko.com` | ready once production serves `/.well-known/skills/index.json` (site PR [contracko/contracko-site#693](https://github.com/contracko/contracko-site/pull/693) merged) |
| Goose and other stdio MCP clients | `npx -y @contracko/mcp` | launcher in `packages/mcp`; publishes to the public npm registry, not GitHub Packages. Proxies stdio to `https://app.contracko.com/mcp`. Not a second MCP server. First publish needs the `NPM_TOKEN` secret on this repo. |

Do **not** add `.mcp.json` to this plugin. Users who already connected Contracko from a connector directory would get the same server twice. ChatGPT may also mark a plugin with `.mcp.json` as Desktop-only.

## The two audiences are not the same person

Nearly every published distribution pattern is a developer-tool pattern: `npx`, `claude plugin install`, editing `.cursor/mcp.json`. A contract manager will do none of it. So the docs page splits at the top:

**Path A, the contract manager.** A remote MCP server with OAuth, added through their client's connector UI, ideally from a directory listing so it is a button rather than a URL. Ends with a first prompt to try, because the activation event is an answer, not a config file.

**Path B, the coding agent.** One line: `npx skills add https://contracko.com`. The MCP connection steps live at [`https://contracko.com/mcp/install/prompt.md`](https://contracko.com/mcp/install/prompt.md); do not add a `/agent-setup/prompt.md` alias.

## Claude chat needs zips, and the repo has to serve them

Uploading to claude.ai and Claude Desktop chat takes **one zip per skill**, with the skill folder at the archive root and the folder name matching the frontmatter `name`. [.github/workflows/release.yml](.github/workflows/release.yml) builds them on every tag and attaches them, which gives permanent URLs:

```
https://github.com/contracko/contracko-skills/releases/latest/download/contracko.zip
```

`latest` always resolves to the newest release, so a docs page hard-codes those once and never edits them.

User flow: click the link, then **Customize > Skills > Add > Upload**, pick the zip, toggle it on, start a new conversation. Team and Enterprise owners can instead push skills to everyone from **Organization settings > Skills**, where they arrive enabled by default, which is the fastest route into a customer with an IT function.

### Gotchas that will bite users

- **Never GitHub's green "Download ZIP" button.** It wraps everything in `<repo>-main/` and the uploader rejects it. Bold line on the docs page.
- **Code execution must be enabled** at Settings > Capabilities, or Organization settings > Skills for Team and Enterprise. Skills are gated behind it even when, as here, they run no code. This is why the menu looks missing.
- **Uploaded is not enabled**, and a conversation that predates the toggle does not pick the skill up.
- **Updates are manual in chat.** No auto-update, no notification. Nobody has solved this; every vendor routes around it by pushing people to a plugin, or by moving anything that can be server-side to the server. Do not build a version-check into the skill body: the one person who tried it burned tokens on every invocation and abandoned it.

### The 200-character cap is real

Anthropic documents it: **claude.ai limits `description` to 200 characters**, where the spec allows 1024 and Claude Code truncates a combined description at 1,536. All four descriptions here are now written to 200, which is valid on every surface. Keep them that way, and spend the budget on trigger words rather than prose.

Same constraint on frontmatter: claude.ai, the Skills API and `package_skill.py` accept only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`. Any Claude-Code-only field is a hard upload error, not a silent ignore. These skills carry `name` and `description` only, deliberately.

## Versioning

`plugin.json` carries a `version`, and it has to be bumped on every change users should receive: the plugin cache is keyed on that string, and an unchanged version means an unchanged install. Omitting the field does not make installs track the latest commit for a directory-sourced marketplace; it pins them permanently instead. Tried that, reverted it.

## What Contracko has to do server-side

None of this is in this repo, and all of it gates the good distribution paths.

- **Connectors Directory submission** needs: a Team or Enterprise claude.ai org to submit from, OAuth 2.0 (have it), a published privacy policy URL, an icon, a support contact, a test account, and every tool carrying a `title` plus `readOnlyHint` or `destructiveHint`. That last one is real work across 22 tools and it is also just good hygiene: a directory reviewer and a model want the same thing, which is to know whether calling a tool changes anything.
- **Skills discovery at a well-known path.** `https://contracko.com/.well-known/skills/index.json` makes `npx skills add https://contracko.com` work and turns a docs deploy into the release. Stripe does exactly this. Shipped in site PR 693; live after that production deploy.
- **Canonical install prompt.** `https://contracko.com/mcp/install/prompt.md`, plain markdown, no auth, no HTML wrapper. There is no `/agent-setup/prompt.md` on the site; that path 404s and should not be documented.
- **A read-only connection variant.** For contract data, a documented read-only URL is a trust feature rather than a footnote, and it is what an IT team asks for first.
- **Public npm for `@contracko/mcp`.** Goose and other stdio clients run `npx -y @contracko/mcp`. That package lives in `packages/mcp` and publishes from the `v*` release workflow when `NPM_TOKEN` is set. GitHub Packages is the wrong registry for this: Goose cannot fetch it. The launcher is not a second MCP server.

## Not this

An MCP tool that points at this repo so a model can fetch its own instructions. Raised and rejected: MCP tools carry their own context and must be standalone interpretable. Skills may reference the server; the server does not reference the skills.

That principle has a consequence worth holding Contracko to. Some write tools still ship thin parameter descriptions, and some errors name no constraint. A tool cannot stand alone and say nothing about itself, and the same gap fails the directory's tool-description bar.

## Cross-client landscape, September 2026

Three standards now cover nearly everything, so a vendor shipping from one repo mostly just has to satisfy them.

- **MCP** for tools. Every client supports remote Streamable HTTP; only the wrapper key differs (`url`, `httpUrl`, `serverUrl`, `context_servers`, `streamableHttp`). Verified shapes and config paths per client live in [`https://contracko.com/mcp/install/prompt.md`](https://contracko.com/mcp/install/prompt.md).
- **Agent Skills / `SKILL.md`** became an open standard, and is now read by Codex (`.agents/skills/`), Copilot and VS Code (`.github/skills/`, `.claude/skills/`, `.agents/skills/`), Gemini CLI, Cursor, Cline and Zed. The format here is already the portable one.
- **Agent Plugins 1.0**, announced August 2026 by Amazon, Cursor, Microsoft, OpenAI, Vercel and Google: one directory with `plugin.json` + `skills/` + `mcp.json`, launching in ChatGPT, Codex, Cursor, Copilot, VS Code and Kiro. Anthropic is not a member, so it does not replace the Claude plugin format.

**Agent Plugins v1 is used for the canonical directory package and the OpenClaw/Hermes release bundles.** The directory package at `packages/agent-plugin/` contains a standard `plugin.json` and the four canonical skills as generated files. It is the public Git-tree package for the directory crawler, which records its nested manifest path. The release bundles use the same generated content. All Agent Plugins packages intentionally omit `mcp.json`: the portable format has no OAuth field, and an unauthenticated duplicate server would be misleading. Existing Claude, Codex, Cursor, Gemini, and other client manifests remain unchanged for compatibility.

The release builder renders the directory package and both bundles from `skills/` and `packaging/manifest.json`. It records the source commit in bundle `RELEASE-METADATA.json`, fixes archive ordering and timestamps, and runs in the existing release workflow. No host software, OAuth client, credential store, or background updater is shipped.

The committed directory package is not hand-maintained. Regenerate it with `python3 scripts/build_release_artifacts.py --write-directory`; CI and `build-zips.sh` run `--check-directory` and fail on missing, extra, or changed files. Keep the repository-root `mcp.json` and `.mcp.json` outside this package because they serve existing client integrations, including Cursor's format.

The generated manifest follows the [Agent Plugins v1 specification](https://agent-plugins.org/specification/). The host flows follow [OpenClaw bundle mapping](https://github.com/openclaw/openclaw/blob/2f8cd215e92320703237b8def415b691f15f3b56/docs/plugins/bundles.md) and [Hermes portable package guidance](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins).

Release assets:

- `https://github.com/contracko/contracko-skills/releases/latest/download/contracko-openclaw.zip`
- `https://github.com/contracko/contracko-skills/releases/latest/download/contracko-hermes.zip`

Two cheap things worth doing when the docs page is built, both MCP-only and neither carrying skills:

```
Cursor:   cursor://anysphere.cursor-deeplink/mcp/install?name=contracko&config=<base64 of the inner server object>
VS Code:  https://vscode.dev/redirect?url=<urlencoded vscode:mcp/install?{"name":"contracko","type":"http","url":"..."}>
```

**ChatGPT is the one client where shipping from a repo does not work at all.** No file-based instruction loading, no way to point it at GitHub. Skills arrive only inside a plugin installed from OpenAI's directory. Its auth constraint is also the strictest: an MCP server that expects an API key header cannot be connected from ChatGPT at all, so real OAuth with dynamic client registration is the price of entry. Contracko has that already.

## While developing: bump the version or the install goes stale

The plugin cache is keyed on `plugin.json`'s `version`. Editing a skill in the source directory changes nothing for anyone who has it installed, including you: `claude plugin marketplace update` refreshes the marketplace, not the plugin, and the installed copy stays pinned at whatever version it was fetched under.

Removing `version` does not fix this. It makes the cache pin permanent, since there is no new string to compare against.

So during development, either bump `version` and reinstall, or run `claude --plugin-dir .` for a session that reads the working tree live. Verify with:

```bash
diff -rq skills ~/.claude/plugins/cache/contracko/contracko/<version>/skills
```

Silence means the install matches. This is worth checking before any test run, because a stale install fails in the most confusing way available: the skills are there, they trigger, and they are the wrong ones.
