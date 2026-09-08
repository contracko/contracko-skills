# Contracko MCP tool index

What each tool is for, and what it costs to get wrong. Parameters, types and limits are in the tool schemas already loaded in your context; this file carries only what those schemas cannot say.

Verified against the Phase 5 catalog in the product app (37 tools when every parser and contract scope is granted). That count includes seven event and reminder tools that existing Phase 5 credentials already have. New tools are gated by capability phase. Improvements to an existing tool, including filters and output schemas, apply to that tool without a Phase 5 upgrade.

User jobs (bring in, calendar, compare, audit, file, report) live in [workflows.md](workflows.md). This file is tools, not jobs.

## Your tool list is the truth

Contracko decides which tools a credential may see and omits the rest. Absence is normal, not an error, and never a reason to guess at a call.

Three causes, in order of likelihood: the scope was not granted (see the scope table in [SKILL.md](../SKILL.md)), the workspace is not entitled to the feature, or the credential predates an action that a workspace admin has not confirmed yet in Settings > Integrations. A key does not gain new abilities on its own.

So: read your tool list, work with what is in it, and treat everything below that you cannot see as unavailable rather than broken.

## Connection

| Tool | Scope | What it is for |
|---|---|---|
| `auth_validate` | any valid credential | Workspace, key and granted scopes. First call of every session. |

## Reading contracts

| Tool | Scope | What it is for |
|---|---|---|
| `clm_list_contracts` | `contract:read` | Paged contracts. Filter first with supported metadata criteria, then page to `nextCursor: null`: see below. |
| `clm_get_contract` | `contract:read` | One contract in full, with its documents, parties, dates, notice window, liability and custom field values. |
| `clm_get_contract_analysis` | `contract:read` | AI overview, risks with severity and evidence quotes, obligations, key terms. Judgement, not the document itself. |
| `clm_search_contract_documents` | `contract:read` | Cited passages from indexed document text. Prefer this for "what does this say". `hybrid` is the default; `exact` is the only stably paginated mode. Semantic and hybrid results are `partial`. |
| `clm_read_contract_document` | `contract:read` | Bounded document text in cited sections. Follow `nextCursor`. Do not read a whole library this way. |
| `clm_get_contract_document_download_url` | `contract:read` | Short-lived HTTPS URL for original bytes or a preview PDF. Expires in 15 minutes. Never log the URL. |
| `clm_list_contract_comments` | `contract:read` | Comments on one contract. |
| `clm_list_contract_types` | `contract:read` | Types with their full field definitions. |
| `clm_get_contract_type` | `contract:read` | One type. |
| `clm_list_parties` | `contract:read` | Resolve a vendor by `query` and `type` before filtering contracts by its returned id. |
| `clm_get_party` | `contract:read` | Contact and address detail for one party. |

## Filter contracts first, then page

`clm_list_contracts` supports `status`, `categoryId`, `counterpartyId`, `query`, `endDateFrom`, `endDateTo`, `noticeDateFrom`, and `noticeDateTo`. Filters combine with AND. `query` is a literal, trimmed, case-insensitive substring over the title, assigned Party B effective display name, or live legal name. It is not semantic search.

Use the narrowest supported criteria. Page until `nextCursor` is `null`, repeating the same normalized filters and `updatedSince` when it is used. `limit` can change. Treat cursors as opaque and never edit them. Change any filter, then restart with no cursor. `updatedSince` can combine with business filters. An `updatedSince`-only legacy sync remains unbound, and it is not an end-date filter or renewal window.

Date windows are inclusive `YYYY-MM-DD` values. For unsupported value, currency, null-presence, or custom-field filtering, narrow by supported criteria and page the complete result before applying the local filter. A full-workspace audit pages every contract. Do not use a date window to audit missing dates, because null dates are excluded.

Resolve a vendor through `clm_list_parties` with `query` and `type`. If more than one party matches, confirm the selection. Then call contracts with the selected `counterpartyId`.

Illustrative examples only. Use the actual date for a real question.

```json mcp:clm_list_contracts
{
  "endDateFrom": "2026-04-01",
  "endDateTo": "2026-06-30",
  "status": "active",
  "limit": 50
}
```

```json mcp:clm_list_contracts
{
  "noticeDateFrom": "2026-04-01",
  "noticeDateTo": "2026-04-30",
  "limit": 50
}
```

```json mcp:clm_list_parties
{
  "query": "Acme",
  "type": "company"
}
```

After the party lookup returns the vendor's actual id, use that id as `counterpartyId`. This illustrative UUID stands for the id returned by that lookup:

```json mcp:clm_list_contracts
{ "counterpartyId": "11111111-1111-4111-8111-111111111111", "limit": 50 }
```

Document-text search is a different tool: `clm_search_contract_documents` finds clauses, not "renews in 90 days". [contracko-review](../../contracko-review/SKILL.md) covers applying these rules to calendar, audit, and report jobs.

## Writing contracts

| Tool | Scope | What it is for |
|---|---|---|
| `clm_import_contracts` | `contract:write` | The default way in. One managed contract per document, extraction starts automatically, idempotency key required. |
| `clm_get_import_status` | `contract:read` | Aggregate and per-document progress. Honour `pollAfterMs`. |
| `clm_create_upload_url` | `contract:write` | Signed destination for one file. Step 1 of the manual path. |
| `clm_ingest_contract` | `contract:write` | Files one contract from uploaded documents using metadata you supply. Step 2. `endDate` is required unless `isOpenEnded` is true, which the schema does not say. |
| `clm_create_party` | `contract:write` | `isOwned` marks your own entity rather than the counterparty. |
| `clm_update_party` | `contract:write` | Partial: omitted fields keep their value. |
| `clm_update_contract` | `contract:write` | Partial metadata on one contract. Send the exact `updatedAt` from the latest read as `expectedUpdatedAt`. A stale value conflicts instead of overwriting. |
| `clm_bulk_update_contracts` | `contract:write` | Independent partial updates, 1–100 contracts. One failure does not roll back the rest. Confirm before a bulk write. |
| `clm_add_contract_documents` | `contract:write` | Add draft or related files, or replace the primary, on an existing contract. Needs an idempotency key. |
| `clm_add_contract_comment` | `contract:write` | Not idempotent. After a timeout, list comments before retrying. |
| `clm_create_contract_type` | `contract:write` | Type plus fields. `select` choices go in `config.options`. |
| `clm_update_contract_type` | `contract:write` | Replaces the whole field set when `fields` is sent. Send every field you want to keep. |

[contracko-import](../../contracko-import/SKILL.md) covers the two paths and the rules that are not in the schema.

## Events and reminders

A reminder hangs off an event. List first. Mutations need `contract:write`, an idempotency key, and (for update or delete) `expectedUpdatedAt` from the latest list. [contracko-review](../../contracko-review/SKILL.md) owns the calendar.

| Tool | Scope | What it is for |
|---|---|---|
| `clm_list_contract_events` | `contract:read` | Dated custom events and supported system events (`notice`, `end`, `open_ended_review`) with their reminder schedules. |
| `clm_create_contract_events` | `contract:write` | Custom events, optionally with nested reminders. You do not create system events. |
| `clm_update_contract_events` | `contract:write` | Custom events. Sending `reminders` replaces that event's reminder set. Relist first. |
| `clm_delete_contract_events` | `contract:write` | Custom events and every reminder linked to them. |
| `clm_create_event_reminders` | `contract:write` | Linked reminders on a custom event or a supported system event. Renewal alerts target `end`. |
| `clm_update_event_reminders` | `contract:write` | Timing, recipient, or message of an existing reminder. |
| `clm_delete_event_reminders` | `contract:write` | The reminder only. The event stays. |

## Parser

Extracts structured data from documents without filing them as managed contracts. Spends credits, where the contract tools do not.

| Tool | Scope | What it is for |
|---|---|---|
| `parser_get_credits` | `parser:compute` | Remaining credits, plan, concurrency. |
| `parser_preflight` | `parser:compute` | Free, and returns the exact cost per file. Run it before every job. |
| `parser_create_upload_url` | `parser:compute` | Signed destination, returns the reference a job takes. |
| `parser_create_job` | `parser:compute` | Spends. `runKind: "extraction"` is fields only; `"review"` adds analysis at roughly double. |
| `parser_get_job` | `parser:compute` | Status, an inline preview per file, and a download URL for the full export. |
| `parser_list_jobs` | `parser:compute` | Recent jobs, newest first. |

Results expire on the job's `retentionExpiresAt`, after which the export is gone. Where the user needs it kept, download during the window.

## Steps that happen in the app today

The skills in this bundle describe complete workflows, because that is how the work is actually done. Parts of those workflows do not have a tool yet, and the MCP surface is rolling out in phases, so the set below shrinks over time.

**The rule that keeps this safe: your tool list decides, not this table.** Where a tool exists for a step, use it. Where the step is named here and no tool answers to it, that step is the user's to do in the app: say which step, say where, and carry on with the rest of the flow. Never improvise a call for a tool you cannot see, and never quote this table as proof a feature is missing from the product.

| The workflow step | Where it is today | The nearest thing over MCP |
|---|---|---|
| folders, filing, moving contracts into a structure | app | A contract carries a `folderId` you can read, and nothing that sets one. |
| drafting from a template or questionnaire, changing a contract's status | app | The write tools file documents that already exist. |
| sending for signature, chasing a signer, signature status | app | Nothing. File the executed copy once it comes back. |
| playbook and clause-library comparison, deviation reports | app | `clm_get_contract_analysis` judges a contract on its own terms rather than against a playbook. |
| knowledge base and business-context enrichment | app | Nothing yet. |
| handing an uploaded file to the import pipeline | not yet | `clm_create_upload_url` returns a reference only `clm_ingest_contract` accepts, and `clm_import_contracts` cannot take it. So a local file is either base64 through your context with Contracko extracting, or uploaded machine-to-machine with you extracting. [contracko-import](../../contracko-import/SKILL.md) has the decision. |
| filtering by value, currency, null presence, or custom fields | local after a complete filtered page-through | First narrow with supported server criteria, then page that complete result before applying the local condition. |
| attaching an existing party to an existing contract | not yet | Import and ingest attach parties as they file a contract. |
| deleting or archiving anything | app, by design | Destructive operations are deliberately kept out of an agent's hands. Cleanup is a web app job, so get creates right the first time rather than waiting for a tool that is not coming. |

Every row except the last is a phase question rather than a decision, so re-read your tool list rather than this file when a user asks whether something is possible.

## Product knowledge

What you remember about Contracko's features, limits and pricing may be out of date. Prefer retrieval over recall: the product's machine-readable documentation is at `https://contracko.com/llms.txt`, with markdown endpoints behind it, and where it disagrees with anything here or anything remembered, the documentation wins.
