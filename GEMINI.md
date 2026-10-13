# Contracko

Contracko is contract management: a repository of contracts (PDF and Word) with extracted dates, values, parties and AI analysis on top. This extension connects the Contracko MCP server at `https://app.contracko.com/mcp`.

CLM tools (`clm_*`) add, import and manage contracts without Parser credits. Contracko Parser (`parser_*`) is separate bulk document processing using Parser credits, not needed to add contracts to your contract register.

On first use a browser opens for OAuth sign-in. A 7-day free trial can be started on that screen (no credit card). Sign in or start the trial, choose your workspace, then review and approve access. The permissions are **View contracts** for questions and reviews, and **Add and edit contracts** for imports or changes. Requested permissions start selected; untick **Add and edit contracts** unless you want imports or changes. It is offered only when your workspace role allows it. Each permission has an info button with details. When write access is requested, the screen offers a copyable prompt to add a contract; select **Add and edit contracts** to copy it.

Detailed guidance lives in the skills under `skills/`:

- `skills/contracko/SKILL.md`: connect, verify, and organise the workspace (types, fields, counterparties, folders); routes all other jobs.
- `skills/contracko-import/SKILL.md`: bring contracts in.
- `skills/contracko-review/SKILL.md`: review terms, renewals, risk and vendor questions.
- `skills/contracko-create/SKILL.md`: create and file new agreements.

Read the relevant skill before acting on a Contracko task. Note the workspace's characteristic failure mode described there: scopes hide tools rather than refusing them, so verify a write actually landed rather than trusting a silent success.
