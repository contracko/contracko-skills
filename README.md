# Contracko skills

These skills teach an AI assistant to work in your [Contracko](https://contracko.com) workspace: bring contracts in, keep dates and types in order, and answer questions from the records.

The assistant talks to Contracko over MCP. Some steps still happen in the Contracko app. The skills say which is which, so the assistant does not invent a button that is not there.

## Before you start

Connecting Contracko to an AI product sends contract data to that product's AI provider. Contracko cannot control what that provider does with it. Turn off model training in the provider's settings before working with real contracts.

## What you can ask

### 1. Bring contracts in

Ask: "Import the PDFs in this folder." "Onboard us from Google Drive / SharePoint / Box."

**Now.** The assistant finds files with whatever disk or cloud access it already has (Contracko does not browse Drive or SharePoint itself), confirms the set with you, and imports them so Contracko extracts dates, parties, types and analysis.

**In the app.** You confirm extractions that land as pending review. Putting contracts into folders is still a click in Contracko.

### 2. What is coming up

Ask: "What needs notice in the next 90 days?" "Which contracts end this quarter?" "What is due for annual review?"

**Now.** The assistant reads notice dates, end dates and renewal flags and gives you the list today.

**In the app.** Reminders and notifications that should fire on their own, when nobody is asking.

### 3. Compare these

Ask: "Compare these two vendor proposals." "What changed between this draft and the last redline?"

**Now.** The assistant puts both sides next to each other from the records, the AI analysis, and quoted clauses.

**In the app.** Playbook / clause-library scoring against your house positions. There is no automatic redline-diff button over this connection.

### 4. Audit for risk

Ask: "Where is liability uncapped?" "What are the material risks in this MSA?"

**Now.** The assistant uses Contracko's analysis plus the sentence in the document that supports it.

**In the app.** Measuring a contract against a playbook you maintain in Contracko.

### 5. File and type them

Ask: "Set up proper contract types." "How should we folder these?"

**Now.** The assistant shapes contract types and custom fields, and corrects metadata (type, dates, parties, value). It can *read* which folder a contract is in. It cannot move it.

**In the app.** Creating the folder tree and dragging contracts into it.

### 6. Priorities and gaps

Ask: "What should we look at this month?" "Where is the portfolio thin?"

**Now.** The assistant pages the whole workspace and ranks what is urgent, what is missing (dates, types, review, value), and where vendor spend sits.

**In the app.** Saved reports and list filters you click yourself. The assistant cannot filter the contract list on the server yet, so large workspaces take a full pass.

### Starting a new agreement

Ask: "Help me draft an NDA and file it when it is signed."

**Now.** The assistant runs the questionnaire and files the executed copy.

**In the app.** Template drafting and sending for signature.

## Connect

Hand your assistant one line:

> Fetch and execute the setup instructions at https://contracko.com/agent-setup/prompt.md

Or in Claude Code:

```
/plugin marketplace add https://github.com/contracko/contracko-skills.git
/plugin install contracko-skills@contracko
```

Use the HTTPS URL. The `owner/repo` shorthand clones over SSH and fails on many machines.

Then connect the Contracko MCP server once. In Claude Code:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

Run `/mcp` and authenticate. The plugin does not register the server for you, so anyone who already connected Contracko from a connector directory does not get it twice.

Other agents: `npx skills@latest add contracko/contracko-skills`. Codex/ChatGPT: import marketplace `contracko/contracko-skills`. Copilot CLI: `copilot plugin marketplace add contracko/contracko-skills`. Headless clients use an MCP key from **Settings > Integrations > API keys** (purpose: **MCP server**).

## For agents

| Skill | Owns |
|---|---|
| [`contracko`](skills/contracko/SKILL.md) | Connect, scopes, types, fields, counterparties, folder *plan*. Router. [Jobs](skills/contracko/references/workflows.md). [Tool index](skills/contracko/references/tool-index.md). |
| [`contracko-import`](skills/contracko-import/SKILL.md) | Find files, import, ingest, extra documents. |
| [`contracko-review`](skills/contracko-review/SKILL.md) | Calendar, compare, audit, portfolio. |
| [`contracko-create`](skills/contracko-create/SKILL.md) | New agreement: questionnaire, then file the signed copy. |

Your tool list is the truth. Later MCP phases move some app steps onto that list. Until a tool appears, the app step stands.

MIT licensed.
