# Contracko Skills

Agent skills for [Contracko](https://contracko.com) contract management over MCP.

Contracko exposes an MCP server, and a connected agent can already read and write a workspace with it. What it cannot do on its own is know which of the 30 tools answers a given question, which scope silently hid half of them, or which of the schema's optional fields is required in practice. These skills carry that.

## Install

Hand your agent one line and let it do the rest:

> Fetch and execute the setup instructions at https://contracko.com/agent-setup/prompt.md

Or do it yourself. Claude Code, from a session:

```
/plugin marketplace add contracko/contracko-skills
/plugin install contracko-skills
```

Other agents:

```bash
npx skills@latest add contracko/contracko-skills
```

Codex / ChatGPT (workspace): **Workspace settings > Plugins > Add > Import marketplace** and paste `contracko/contracko-skills`.

GitHub Copilot CLI:

```bash
copilot plugin marketplace add contracko/contracko-skills
copilot plugin install contracko-skills@contracko
```

Gemini CLI: install the skills from this GitHub repo. There is no third-party Gemini marketplace.

Then connect the server, once, in whichever client you use. In Claude Code:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

Run `/mcp` and authenticate; OAuth takes you through sign-in, workspace choice and scopes in the browser. In Claude Desktop or claude.ai, add Contracko from the connector directory instead. The plugin deliberately does not register the server for you, since anyone who already connected it would end up with the same server twice.

For a headless client that cannot run OAuth, use an MCP key from **Settings > Integrations > API keys** (key purpose: **MCP server**):

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp \
  --header "Authorization: Bearer YOUR_MCP_KEY"
```

## The skills

| Skill | What it does |
|---|---|
| [`contracko`](skills/contracko/SKILL.md) | Connects and verifies the server, explains what each scope unlocks, organises the workspace (contract types, custom fields worth having, counterparties, folders, reminders, registers), routes the rest, and holds the [tool index](skills/contracko/references/tool-index.md). |
| [`contracko-import`](skills/contracko-import/SKILL.md) | Gets documents in. Managed import versus prepare-and-file, polling, idempotency, and the rules that are not in the schema. |
| [`contracko-review`](skills/contracko-review/SKILL.md) | Gets answers out. Renewal and notice deadlines, risk and liability, vendor exposure, and an honest account of what the read tools cannot filter. |
| [`contracko-create`](skills/contracko-create/SKILL.md) | Takes a new agreement from questionnaire to drafted, signed and filed, reconciling what was extracted against what was agreed. |

Start with `contracko`. It is the entry point and the router.

## Before you connect real contracts

Connecting Contracko to an AI product sends contract data to that product's AI provider. Contracko cannot control what a third-party provider does with it. Turn off model training in the provider's settings before working with real contracts.

## Workflows outrun the tool list, on purpose

The MCP surface is rolling out in phases, so parts of these workflows are done in the Contracko app today: reminders, folders, drafting and signature among them. The skills describe the whole flow and mark those steps rather than pretending they do not exist, because the failure mode otherwise is an agent inventing a plausible tool call and reporting a result that never happened. The register is in the [tool index](skills/contracko/references/tool-index.md#steps-that-happen-in-the-app-today), and a live tool list always outranks it.

## Contributing

Skills live at `skills/<name>/SKILL.md` with YAML frontmatter carrying `name` and `description`. The description is what an agent reads to decide whether the skill applies, so it should carry the phrases a user would actually say. Longer material goes in `references/` next to the skill rather than inflating `SKILL.md`.

MIT licensed.
