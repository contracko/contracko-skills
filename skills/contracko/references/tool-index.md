# Contracko MCP tool index

Use live discovery for tool names and schemas. This index records workflow rules that schemas do not express. [workflows.md](workflows.md) maps user jobs to these tools.

This index lists all 52 tools a connection with every scope can see. A narrower connection sees fewer. When you are unsure which tool fits, call `clm_search_tools` instead of guessing from this page.

## Discovery and results

Tools absent from discovery are unavailable to this connection. First refresh discovery or reconnect if the client has cached schemas. If an older credential still omits newly available actions, a workspace admin can enable new MCP actions for its key, or the user can re-consent OAuth. Do not guess a call.

Check `isError` first. On success, use `structuredContent` when present or the legacy JSON text otherwise, never both. Required fields missing from the discovered `outputSchema` are a response mismatch, not empty data. Re-read before retrying an `OUTCOME_UNKNOWN` mutation.

## Connection

| Tool | Scope | Use |
|---|---|---|
| `auth_validate` | any valid credential | Confirm workspace and scopes before work. |
| `clm_search_tools` | any valid credential | Find up to five listed tools, with examples and step sequences, for a task. Reads no workspace data. |

Use `clm_search_tools` when the right tool is unclear, before a multi-step job, and for a first contract in an empty workspace. Results come only from this connection's tool list. Example arguments use synthetic IDs; replace them with real values from the connection.

```json mcp:clm_search_tools
{ "query": "set renewal reminders", "toolset": "events" }
```

CLM tools (`clm_*`) add, import and manage contracts without Parser credits. Parser tools (`parser_*`) are separate Contracko Parser bulk document processing, use Parser credits and are not needed to add contracts to your contract register.

## Contracts and folders

| Tool | Scope | Use |
|---|---|---|
| `clm_list_contracts` | `contract:read` | Page contract records and business filters. |
| `clm_get_contract` | `contract:read` | Read one contract, including filing state. |
| `clm_list_folders` | `contract:read` | Page folders visible to the user. |
| `clm_get_folder` | `contract:read` | Inspect one visible folder: its visible path, visibility, permission, and bounded members. |
| `clm_create_folder` | `contract:write` | Create a root folder or a child of a visible parent. |
| `clm_rename_folder` | `contract:write` | Rename a manageable folder. |
| `clm_move_folder` | `contract:write` | Move a folder to a visible parent or the root. |
| `clm_move_contract` | `contract:write` | File a contract in a visible folder, or unfile it. |
| `clm_get_contract_access` | `contract:read` | Read a contract access overview. |

`clm_list_folders` uses `continuation`, not the contract `cursor`. Omitting `parentFolderId`, or sending `parentFolderId: null`, lists only the visible root. Complete root pages, then list and complete the children of every visible folder recursively to enumerate the visible tree. A completed root page set is not a full-tree result. For each parent, repeat the same parent and limit with the opaque continuation until it is `null`. Returned paths contain visible ancestors only. Omission does not prove a hidden folder exists or does not exist.

Inspect a destination before changing it. Confirm the visible path and every bulk change. `clm_move_contract` accepts `folderId: null` only to unfile. `clm_move_folder` accepts `parentFolderId: null` to move to the root. Folder deletes and all access changes are app work. `clm_get_folder` and `clm_get_contract_access` are read-only and provide no ACL write operation.

```json mcp:clm_list_folders
{ "limit": 50 }
```

Continue a child-folder page with the same parent and limit. The continuation is opaque.

```json mcp:clm_list_folders
{
  "parentFolderId": "11111111-1111-4111-8111-111111111111",
  "limit": 50,
  "continuation": "opaque-folder-page-token"
}
```

```json mcp:clm_get_folder
{ "id": "11111111-1111-4111-8111-111111111111" }
```

```json mcp:clm_create_folder
{ "name": "Legal", "parentFolderId": null }
```

```json mcp:clm_rename_folder
{ "id": "11111111-1111-4111-8111-111111111111", "name": "Legal and compliance" }
```

```json mcp:clm_move_folder
{ "id": "11111111-1111-4111-8111-111111111111", "parentFolderId": null }
```

```json mcp:clm_move_contract
{ "id": "22222222-2222-4222-8222-222222222222", "folderId": "11111111-1111-4111-8111-111111111111" }
```

Unfile only after the user asks to remove the contract from its folder.

```json mcp:clm_move_contract
{ "id": "22222222-2222-4222-8222-222222222222", "folderId": null }
```

```json mcp:clm_get_contract_access
{ "id": "22222222-2222-4222-8222-222222222222" }
```

Use IDs returned by discovery in real calls. The UUIDs above are valid example values only.

### Contract filters and filing state

`clm_list_contracts` supports `status`, `categoryId`, `counterpartyId`, `query`, `endDateFrom`, `endDateTo`, `noticeDateFrom`, `noticeDateTo`, `updatedSince`, and `folderId`. All supplied filters combine with AND. `query` is a literal, trimmed, case-insensitive substring over the title and the assigned Party B display or legal name, including historical names. It is not document search.

The `folderId` list filter must be a valid visible UUID. It cannot be `null`. To audit unfiled contracts, page the applicable contract result and inspect `filing.kind`. A contract has `filing.kind` of `unfiled`, `folder`, or `unavailable`. Every returned contract has `folderId`: it is a visible UUID only for `folder`, otherwise `null`. `filing.folder.id` and `filing.folder.path` are available only for `folder`. Treat `unavailable` as unknown filing, not as unfiled.

Use the narrowest supported filters, then repeat the same normalized filters and opaque `cursor` until `nextCursor` is `null`. Changing any filter starts a new query without a cursor. For an OR question, run separate complete queries and deduplicate by contract ID. For value, currency, null-presence, or custom-field filters, complete the narrowed server result before local filtering. Date windows exclude null dates.

Resolve a vendor with `clm_list_parties` using `query` and `type` before passing its returned ID as `counterpartyId`. When more than one party matches, ask the user to choose.

```json mcp:clm_list_contracts
{
  "endDateFrom": "2026-04-01",
  "endDateTo": "2026-06-30",
  "status": "active",
  "limit": 50
}
```

```json mcp:clm_list_parties
{ "query": "Acme", "type": "company" }
```

## Evidence and review

| Tool | Scope | Use |
|---|---|---|
| `clm_get_contract_analysis` | `contract:read` | Risk, obligations, and key-term analysis. |
| `clm_search_contract_documents` | `contract:read` | Find cited text. `exact` is the stable pagination mode. |
| `clm_read_contract_document` | `contract:read` | Read bounded cited sections. |
| `clm_get_contract_document_download_url` | `contract:read` | Get a short-lived original or preview URL. Do not log it. |
| `clm_list_contract_comments` | `contract:read` | Read comments on one contract. |

## Document re-reads

A re-read runs AI extraction on one contract document again and compares the result with the saved contract. It never changes saved data on its own: it produces per-field findings that a person approves.

| Tool | Scope | Use |
|---|---|---|
| `clm_reprocess_contract_document` | `contract:write` | Start a re-read of one document. Retry with the same `idempotencyKey` to get the original run. |
| `clm_get_contract_reprocess_run` | `contract:read` | Check a re-read's progress. |
| `clm_list_contract_reconciliations` | `contract:read` | List a contract's recent re-reads, including completed ones nobody has reviewed. |
| `clm_get_contract_reconciliation` | `contract:read` | Read the per-field differences a completed re-read found. Reading never applies or dismisses a finding. |
| `clm_apply_contract_reconciliation` | `contract:write` | Write selected findings onto the contract after a person approves that exact selection. |

The reads are safe to call at any time. Apply only works in a client that can ask the person to approve; otherwise send the user to the review in Contracko. A re-read uses the same extraction allowance as an import.
## Import and contract writes

| Tool | Scope | Use |
|---|---|---|
| `clm_import_contracts` | `contract:write` | Managed import from a prepared upload (`kind: "upload"`), inline bytes, or a remote URL. Contracko extracts. |
| `clm_import_files` | `contract:write` | Managed import of files attached in a ChatGPT chat. Contracko downloads them from ChatGPT's file service. |
| `clm_create_upload_session` | `contract:write` | Create a one-hour upload link (`uploadPageUrl`) where the signed-in person adds files in their browser. The fallback when you cannot send the bytes. |
| `clm_get_import_status` | `contract:read` | Poll import progress and honour `pollAfterMs`. |
| `clm_create_upload_url` | `contract:write` | Create a short-lived upload destination for import or ingest. `ifUploadUrlUnreachable` names the fallback. |
| `clm_ingest_contract` | `contract:write` | File uploaded documents with agent-supplied metadata and analysis. |
| `clm_add_contract_documents` | `contract:write` | Add draft or related documents, or replace the primary document. |
| `clm_update_contract` | `contract:write` | Partially update one contract with its latest `updatedAt`. |
| `clm_bulk_update_contracts` | `contract:write` | Independently update up to 100 contracts. Confirm the batch. |
| `clm_add_contract_comment` | `contract:write` | Add a comment. Contracko emails the contract's followers. After an unknown outcome, list comments before retrying. |
| `clm_create_contract_type` / `clm_update_contract_type` | `contract:write` | Create types and fields, or replace a supplied field set. |
| `clm_list_contract_types` / `clm_get_contract_type` | `contract:read` | Inspect types and fields. |
| `clm_create_party` / `clm_update_party` | `contract:write` | Create or partially update parties. |
| `clm_list_parties` / `clm_get_party` | `contract:read` | Resolve and inspect parties. |

`taxId` and `registrationNumber` are for organisations only (`company`, `non-profit`, `government`), never for an `individual` or a personal identifier. Changing a party to `individual` needs both cleared in the same update.

### Add your first contract

For a single local file in an empty workspace, `clm_search_tools` with "Add my first contract" returns this sequence. [workflows.md](workflows.md#add-your-first-contract) has the full job.

1. `clm_create_upload_url` with `fileName`, `mimeType`, and `fileSize`.
2. HTTP `PUT` the bytes to the returned URL with the same `Content-Type`. This is a plain request, not a tool call.
3. `clm_ingest_contract` with the returned `uploadReference` and the contract details you read from the document.
4. `clm_get_contract` to verify the new record.

```json mcp:clm_create_upload_url
{ "fileName": "acme-msa.pdf", "mimeType": "application/pdf", "fileSize": 182044 }
```

After the PUT, `clm_import_contracts` with a `kind: "upload"` file lets Contracko extract instead of you. In ChatGPT, use `clm_import_files` for attached files. Without network access, send only a tiny file inline; otherwise create an upload link with `clm_create_upload_session`. Upload only to the returned `uploadUrl`, never to a third-party host. Never publish a confidential contract to make a remote URL work. [contracko-import](../../contracko-import/SKILL.md) defines these paths.

## CLM events and notifications

Events and notifications need `contract:read` to list and `contract:write` to change. List before a change, use the latest `expectedUpdatedAt` for updates or deletes, and confirm a bulk write. Renewal notifications attach to the existing `end` system event.

Contracko emails each notification to its recipient when it falls due. Creating or changing events and notifications therefore schedules email to real people; say who will receive what before writing. Deleting an event or notification stops those emails.

| Tool family | Scope | Use |
|---|---|---|
| `clm_list_contract_events` | `contract:read` | List custom and supported system events with notifications. |
| `clm_create_contract_events`, `clm_update_contract_events`, `clm_delete_contract_events` | `contract:write` | Manage custom events. |
| `clm_create_event_reminders`, `clm_update_event_reminders`, `clm_delete_event_reminders` | `contract:write` | Manage notifications on events. |

## Contracko Parser: separate bulk document processing

Uses Parser credits; not needed to add contracts to your contract register. Only use this workflow for requested standalone processing, not contract intake or a CLM plan refusal.

| Tool | Scope | Use |
|---|---|---|
| `parser_get_credits` | `parser:compute` | Check Parser balance and availability; spends no credits. |
| `parser_preflight` | `parser:compute` | Estimate Parser credits and validate files; spends no credits. |
| `parser_create_upload_url` | `parser:compute` | Prepare a document for a Parser job; spends no credits. |
| `parser_create_job` | `parser:compute` | Start bulk document processing; spends Parser credits. |
| `parser_get_job` | `parser:compute` | Read a Parser job and retrieve results; spends no additional credits. |
| `parser_list_jobs` | `parser:compute` | List Parser jobs; spends no additional credits. |

Preflight before starting a Parser job, confirm the estimated Parser credit cost, and retrieve exports before their retention window ends. Parser credit refusals affect this product, not CLM contract intake.
