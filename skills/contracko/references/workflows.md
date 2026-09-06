# Jobs

User jobs, not tools. Mechanics live in the skill named on each job. The live tool list outranks this file. The app-vs-MCP register is in [tool-index.md](tool-index.md); do not copy it here.

Later MCP phases will move some app steps onto the tool list. Until a tool appears, the app step stands. Never invent a name for a tool you cannot see.

Read this when the request is a job. Then open only the skill that owns the mechanics.

## 1. Bring contracts in

**They say:** import these, onboard us, migrate the archive, look on disk / Google Drive / SharePoint / Box.

**Now (Phase 5):** find files with the agent's own disk or cloud tools (Contracko MCP does not browse those stores). Confirm the set. Import so Contracko extracts types, parties and analysis. Then shape types. [contracko-import](../../contracko-import/SKILL.md) owns finding and filing. [SKILL.md](../SKILL.md) owns types, fields and the folder *proposal*.

**Not on MCP yet:** browsing Drive/SharePoint/Box as a Contracko tool; handing an already-uploaded file into managed import; creating folders or moving contracts into them.

**Done when:** documents are contracts in the workspace the user meant, types cover the questions they ask, pending-review is named, and the folder tree they still click is written down.

## 2. What is coming up

**They say:** notice dates, end dates, renewals, annual review, reminders, notifications.

**Now (Phase 5):** answer *today* from `noticeDate`, `endDate`, `isInNoticePeriod`, `autoRenewing`, and (for annual review) `startDate` or a review custom field. [contracko-review](../../contracko-review/SKILL.md) owns the calendar.

**Not on MCP yet:** events, reminders, notifications that fire later. Those stay in the app.

**Done when:** the user has the urgent bucket, the dates that drive it, and (if they wanted an alert) the app step named.

## 3. Compare these

**They say:** two proposals, vendor A vs B, this redline vs the last draft.

**Now (Phase 5):** both sides as records (import first if needed), then table differences from metadata, analysis and cited text. Related versions can live as documents on one contract. [contracko-review](../../contracko-review/SKILL.md) owns comparison.

**Not on MCP yet:** playbook / clause-library scoring, a redline-diff tool, knowledge-base enrichment.

**Done when:** the user can choose, with quotes.

## 4. Audit for risk

**They say:** risks, liability, caps, indemnity, what could hurt us.

**Now (Phase 5):** `clm_get_contract_analysis` plus liability fields and quoted clauses. Portfolio audits page first, then open the hot contracts. [contracko-review](../../contracko-review/SKILL.md) owns audit.

**Not on MCP yet:** scoring against a house playbook.

**Done when:** each material finding has a quote, a severity, and whether extraction has been reviewed.

## 5. File and type them

**They say:** organise, folders, the right contract type, custom fields.

**Now (Phase 5):** create and update types and fields; `clm_update_contract` / `clm_bulk_update_contracts` for metadata (type, dates, value, parties). Read `folderId`. Describe the tree. [SKILL.md](../SKILL.md) owns this.

**Not on MCP yet:** creating folders, moving contracts, sharing / access. `folderId` is readable, not settable.

**Done when:** types and fields match how the user thinks, contracts point at those types, and they have a folder plan they can click.

## 6. Priorities and gaps

**They say:** report, portfolio, what matters this quarter, what are we missing.

**Now (Phase 5):** page the workspace and bucket it. No server-side list filters. [contracko-review](../../contracko-review/SKILL.md) owns reporting.

**Not on MCP yet:** metadata filters on `clm_list_contracts`; a dedicated export tool.

**Done when:** the user has a ranked list, the gaps named, and a count of how many contracts the list was built from.

## Starting a new agreement

[contracko-create](../../contracko-create/SKILL.md). Questionnaire and filing are yours. Draft and signature are app steps.
