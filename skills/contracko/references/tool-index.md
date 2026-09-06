# Contracko MCP tool index

What each tool is for, and what it costs to get wrong. Parameters, types and limits are in the tool schemas already loaded in your context; this file carries only what those schemas cannot say.

Verified against the Phase 5 catalog in the product app (30 tools when every parser and contract scope is granted). Older credentials stay frozen until a workspace admin confirms new MCP actions.

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
| `clm_list_contracts` | `contract:read` | The whole portfolio, paged. Rich per-contract payload, and no way to filter it: see below. |
| `clm_get_contract` | `contract:read` | One contract in full, with its documents, parties, dates, notice window, liability and custom field values. |
| `clm_get_contract_analysis` | `contract:read` | AI overview, risks with severity and evidence quotes, obligations, key terms. Judgement, not the document itself. |
| `clm_search_contract_documents` | `contract:read` | Cited passages from indexed document text. Prefer this for "what does this say". `hybrid` is the default; `exact` is the only stably paginated mode. Semantic and hybrid results are `partial`. |
| `clm_read_contract_document` | `contract:read` | Bounded document text in cited sections. Follow `nextCursor`. Do not read a whole library this way. |
| `clm_get_contract_document_download_url` | `contract:read` | Short-lived HTTPS URL for original bytes or a preview PDF. Expires in 15 minutes. Never log the URL. |
| `clm_list_contract_comments` | `contract:read` | Comments on one contract. |
| `clm_list_contract_types` | `contract:read` | Types with their full field definitions. |
| `clm_get_contract_type` | `contract:read` | One type. |
| `clm_list_parties` | `contract:read` | Every counterparty. |
| `clm_get_party` | `contract:read` | Contact and address detail for one party. |

**Listing does not filter.** `clm_list_contracts` pages, and offers no filter, sort or metadata search. Document-text search is a different tool: `clm_search_contract_documents` finds clauses, not "renews in 90 days". Portfolio questions still mean paging the workspace and filtering locally. Page to the end, or say you did not. [contracko-review](../../contracko-review/SKILL.md) covers doing this well.

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
| reminders and notifications before a renewal or notice date | app | Answer the deadline question now from `noticeDate`, `endDate` and `isInNoticePeriod`. Contracko's model is event-first, so a reminder hangs off an event. |
| folders, filing, moving contracts into a structure | app | A contract carries a `folderId` you can read, and nothing that sets one. |
| drafting from a template or questionnaire, changing a contract's status | app | The write tools file documents that already exist. |
| sending for signature, chasing a signer, signature status | app | Nothing. File the executed copy once it comes back. |
| playbook and clause-library comparison, deviation reports | app | `clm_get_contract_analysis` judges a contract on its own terms rather than against a playbook. |
| knowledge base and business-context enrichment | app | Nothing yet. |
| handing an uploaded file to the import pipeline | not yet | `clm_create_upload_url` returns a reference only `clm_ingest_contract` accepts, and `clm_import_contracts` cannot take it. So a local file is either base64 through your context with Contracko extracting, or uploaded machine-to-machine with you extracting. [contracko-import](../../contracko-import/SKILL.md) has the decision. |
| filtering the contract list server-side | not yet | Page and filter locally. Document text search exists; metadata filters do not. |
| attaching an existing party to an existing contract | not yet | Import and ingest attach parties as they file a contract. |
| deleting or archiving anything | app, by design | Destructive operations are deliberately kept out of an agent's hands. Cleanup is a web app job, so get creates right the first time rather than waiting for a tool that is not coming. |

Every row except the last is a phase question rather than a decision, so re-read your tool list rather than this file when a user asks whether something is possible.

## Product knowledge

What you remember about Contracko's features, limits and pricing may be out of date. Prefer retrieval over recall: the product's machine-readable documentation is at `https://contracko.com/llms.txt`, with markdown endpoints behind it, and where it disagrees with anything here or anything remembered, the documentation wins.
