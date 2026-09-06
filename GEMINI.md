# Contracko

Contracko is contract management: a repository of contracts (PDF and Word) with extracted dates, values, parties and AI analysis on top. This extension connects the Contracko MCP server at `https://app.contracko.com/mcp`.

On first use a browser opens for OAuth sign-in. A 7-day free trial can be started on that screen (no credit card). Users choose Read and optionally Write scope at consent; Write is required to import or change contracts, Read is enough to answer questions.

Detailed guidance lives in the skills under `skills/`:

- `skills/contracko/SKILL.md`: connect, verify, and organise the workspace (types, fields, counterparties, folders); routes all other jobs.
- `skills/contracko-import/SKILL.md`: bring contracts in.
- `skills/contracko-review/SKILL.md`: review terms, renewals, risk and vendor questions.
- `skills/contracko-create/SKILL.md`: create and file new agreements.

Read the relevant skill before acting on a Contracko task. Note the workspace's characteristic failure mode described there: scopes hide tools rather than refusing them, so verify a write actually landed rather than trusting a silent success.
