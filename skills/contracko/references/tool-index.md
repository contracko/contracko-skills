# Contracko MCP tool index

60 definitions: 58 normal tools plus two Claude-chat upload-panel tools. Availability depends on scopes, capability policy and client. [Readiness and tool choice](../SKILL.md#connect-and-discover), [imports](../../contracko-import/SKILL.md), and [review](../../contracko-review/SKILL.md) own the instructions.

## Connection

| Tool | Scope | Facts |
|---|---|---|
| `auth_validate` | any valid credential | Reports workspace, scopes and Contract Management refusals, even with credential `status: "ok"`. |
| `clm_search_tools` | any valid credential | Searches listed tools; up to five results with purpose, scopes, examples, related tools and sequences. Optional `toolset`: contracts, parties, folders, events, imports, parser, connection. Reads no workspace data and calls nothing. |

## Contracts and folders

| Tool | Scope | Facts |
|---|---|---|
| `clm_list_contracts` | `contract:read` | Paginated records with business filters and filing state. |
| `clm_get_contract` | `contract:read` | One contract, including filing state. |
| `clm_list_folders` | `contract:read` | Visible folders; `continuation` pagination, separate from contract cursors. |
| `clm_get_folder` | `contract:read` | Visible path, visibility, permission and bounded members. |
| `clm_create_folder` | `contract:write` | Creates a root folder or child of a visible parent. |
| `clm_rename_folder` | `contract:write` | Renames a manageable folder. |
| `clm_move_folder` | `contract:write` | Moves to a visible parent or root. |
| `clm_move_contract` | `contract:write` | Files in a visible folder, or unfiles. |
| `clm_get_contract_access` | `contract:read` | Informational access overview; no ACL writes. |

## Evidence and review

| Tool | Scope | Facts |
|---|---|---|
| `clm_get_contract_analysis` | `contract:read` | Risks, obligations and key terms. |
| `clm_search_contract_documents` | `contract:read` | Cited text; exact search has stable pagination. Semantic/hybrid queries use an external embedding provider. |
| `clm_read_contract_document` | `contract:read` | Bounded cited sections. |
| `clm_get_contract_document_download_url` | `contract:read` | Original or preview URL, expiring in 15 minutes. |
| `clm_list_contract_comments` | `contract:read` | Comments on one contract. |

## Document re-reads

| Tool | Scope | Facts |
|---|---|---|
| `clm_reprocess_contract_document` | `contract:write` | External AI extraction replaces the saved snapshot/status; costs one extraction. Same-key retries return the original run. Successful extraction records a Bento setup milestone when enabled. |
| `clm_get_contract_reprocess_run` | `contract:read` | Progress; settles unconfirmed queue handoffs in saved state. Annotated as a write. |
| `clm_list_contract_reconciliations` | `contract:read` | Recent re-reads, including unreviewed completed runs; list-only read. |
| `clm_get_contract_reconciliation` | `contract:read` | Persists review list, refreshes comparison values and approval version; applies/dismisses nothing. Annotated as a write. |
| `clm_apply_contract_reconciliation` | `contract:write` | Applies selected findings; requires human approval in a capable client. |

## Import and contract writes

| Tool | Scope | Facts |
|---|---|---|
| `clm_import_contracts` | `contract:write` | Managed extraction from prepared upload, inline bytes or remote URL. |
| `clm_import_files` | `contract:write` | Managed import from ChatGPT's attachment service. |
| `clm_create_upload_session` | `contract:write` | One-hour browser upload link for the signed-in person. |
| `clm_show_upload_widget` | no required scope; Claude chat only | Opens the panel, uploads nothing itself. Panel import needs write access and reports a processing job. Not available in Claude Code. |
| `clm_prepare_widget_upload` | `contract:write`; Claude chat panel only | Panel-internal, not a direct agent call; single-use document destination expires within five minutes. |
| `clm_get_import_status` | `contract:read` | Import/ingest snapshot; `wait: true` waits at most 25 seconds. |
| `clm_create_upload_url` | `contract:write` | Short-lived upload destination; `ifUploadUrlUnreachable` supplies a fallback. |
| `clm_ingest_contract` | `contract:write` | Files documents with supplied metadata/analysis; records a Bento setup milestone when enabled. |
| `clm_add_contract_documents` | `contract:write` | Adds drafts or related documents, or replaces the primary. |
| `clm_update_contract` | `contract:write` | Partial update with latest `updatedAt`. |
| `clm_bulk_update_contracts` | `contract:write` | Up to 100 independent updates. |
| `clm_add_contract_comment` | `contract:write` | Adds a comment and emails followers. |
| `clm_create_contract_type` | `contract:write` | Creates definitions, not AI fields or re-extractions; records a Bento setup milestone when enabled. |
| `clm_update_contract_type` | `contract:write` | Supplied `fields` replace the whole field set. |
| `clm_list_contract_types` | `contract:read` | Type definitions. |
| `clm_get_contract_type` | `contract:read` | Current type and field definitions. |
| `clm_create_party` | `contract:write` | Creates a counterparty. |
| `clm_update_party` | `contract:write` | Partial party update. |
| `clm_list_parties` | `contract:read` | Party resolution by query and type. |
| `clm_get_party` | `contract:read` | One party. |

## Type generation and type re-reads

| Tool | Scope | Facts |
|---|---|---|
| `clm_create_type_generation_upload_url` | `contract:write` | Example-document upload without filing a contract. |
| `clm_start_type_generation` | `contract:write` | Spends generation allowance; repeated starts are not idempotent. Saves a new type immediately for review, leaves matching types unchanged, returns failed runs' trial slots. |
| `clm_get_type_generation` | `contract:read` | Background generation run started by the connected user. |
| `clm_get_type_generation_draft` | `contract:read` | Created type ID with read-only field examples/quotes, or existing-type verdict; creates nothing. Saving in the normal editor marks the type reviewed. |
| `clm_reread_contract_type` | `contract:write` | One external-AI extraction per contract with a primary document; replaces an open batch, cancelling unstarted reads. Idempotent same-key retries. Human approval required; saved contract fields remain unchanged pending approval. |
| `clm_get_contract_type_reread` | `contract:read` | Runs/proposal counts; can retry lost reads or stop stuck batches, update saved status and cancel unstarted items. Annotated as a write. |

## CLM events and notifications

| Tool | Scope | Facts |
|---|---|---|
| `clm_list_contract_events` | `contract:read` | Custom and supported system events with notifications. |
| `clm_create_contract_events` | `contract:write` | Creates custom events. |
| `clm_update_contract_events` | `contract:write` | Updates custom events. |
| `clm_delete_contract_events` | `contract:write` | Deletes custom events and their notifications. |
| `clm_create_event_reminders` | `contract:write` | Schedules notification emails on events. |
| `clm_update_event_reminders` | `contract:write` | Changes scheduled notifications. |
| `clm_delete_event_reminders` | `contract:write` | Stops notification emails; leaves the event. |

## Contracko Parser: separate bulk document processing

| Tool | Scope | Facts |
|---|---|---|
| `parser_get_credits` | `parser:compute` | Balance/availability; initializes a missing credit ledger, spends no credits. Annotated as a write. |
| `parser_preflight` | `parser:compute` | Credit estimate/file validation; initializes a missing ledger, spends no credits. Annotated as a write. |
| `parser_create_upload_url` | `parser:compute` | Prepares a Parser document; spends no credits. |
| `parser_create_job` | `parser:compute` | External-AI bulk processing; completed processing consumes Parser credits. |
| `parser_get_job` | `parser:compute` | Job/results; no additional credits. |
| `parser_list_jobs` | `parser:compute` | Jobs; no additional credits. |
