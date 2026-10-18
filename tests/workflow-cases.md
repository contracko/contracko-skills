# Skill workflow regression cases

Use these cases when reviewing skill changes or evaluating an agent with the bundle loaded. They
are behavioral acceptance cases, not claims that a model evaluation ran. The automated tests check
catalog/example compatibility and ZIP links; they do not prove an agent follows this guidance.

| Case | Prompt and supplied tool result | Passing behavior | Failing behavior |
|---|---|---|---|
| Renewal candidates | Today is 2026-09-01. Find contracts ending through 2026-11-30. | Uses inclusive endDateFrom/endDateTo; follows all filtered pages; distinguishes expiry from auto-renewal. | Uses updatedSince as an end-date filter; calls document search for exhaustive metadata results. |
| Notice or ending | Find contracts ending OR needing notice next quarter. | Runs separate end-date and notice-date queries, pages both completely, and deduplicates by contract id. | Combines both windows into one AND query and misses records. |
| Vendor ambiguity | Find our contracts with Acme. Party query returns two legal entities. | Resolves which entity is intended before using counterpartyId, or clearly reports both separately. | Picks the first party silently; pages the whole workspace despite available filters. |
| Pagination | First filtered response contains a nextCursor; second contains null. | Repeats the exact filters and any updatedSince with the opaque cursor; counts both pages once. | Omits filters, edits/decodes the cursor, or claims completeness after page one. |
| Changed scope | User changes the date range after page one. | Restarts with the new range and no cursor. | Reuses the old cursor with changed filters. |
| Missing dates and spend | Find contracts missing end dates or worth over 25k. | Uses only relevant supported filters, fully pages the candidate set, then checks missing dates/value locally; separates currencies. | Invents isNull/value arguments or applies a date window that removes missing dates. |
| Older credential | An older credential exposes list filters but no event tools. | Uses discovered filters without changing credentials; treats omitted event tools as separately gated and names re-consent or enabling new actions only when needed. | Claims a schema improvement grants a missing tool or invents an event call. |
| Cached discovery | Existing connector shows only the old list arguments. | Refreshes/reconnects discovery, then uses available schema; if still old, reports limitation and uses honest fallback pagination. | Sends undocumented arguments blindly or creates another connection. |
| Structured result | Success has equivalent structuredContent and JSON text. | Uses structuredContent once; falls back to text only when structuredContent is absent. | Concatenates both representations or double-counts records. |
| Unknown write | Updating type fields returns isError with OUTCOME_UNKNOWN. | Reads current state and reconciles before any retry or claim about the write. | Assumes rollback or retries automatically. |
| Malformed success | A success payload lacks a required output field. | Reports a response mismatch; does not invent a value or retry a write. | Treats missing data as an empty portfolio or confirmed write failure. |
| Folder discovery | The root folder page returns a continuation, and a requested destination appears on its second page. | Repeats the same `limit` and parent with `continuation`, then inspects the visible destination before any change. | Sends a contract cursor to the folder call, stops at the first page, or treats an omitted folder as proof it does not exist. |
| Filing changes | The user asks to file several contracts in a visible folder. | States the visible destination path and every affected contract, confirms the batch, moves them, then reads back the results. | Moves records before confirming the destination or claims success without reconciliation. |
| Unfiled audit | A contract result includes `filing.kind` values `unfiled`, `folder`, and `unavailable`. | Completes the pages and classifies only `unfiled` as unfiled. | Sends `folderId: null`, treats `unavailable` as unfiled, or invents a hidden folder ID. |
| Access overview | A user asks who can access a restricted folder. | Uses the folder access overview when discovered and explains that permission changes and folder deletion happen in the app. | Attempts an ACL write through MCP or exposes a hidden folder's existence. |

## Import versus sync cases

The [import skill](../skills/contracko-import/SKILL.md#choose-import-or-sync) owns this decision. These cases address document intake being mistaken for external-record sync.

| Case | Prompt and supplied tool result | Passing behavior | Failing behavior |
|---|---|---|---|
| Local PDFs | Add these three PDFs from my disk to Contracko. | Measures file metadata, prepares and uploads the bytes, then calls `clm_import_contracts` with the returned upload references and lets Contracko extract fields. | Replaces managed import with self-extraction or ingest, or invents `externalSystem`/`externalId`. |
| Cloud-drive documents | Add these Google Drive, SharePoint, Box or OneDrive files; a connector can fetch them. | Downloads or fetches the files with the connector, then follows the managed import transfer path. | Treats the drive connector or a file id as an external contract record for ingest. |
| Attachment or URL | Add this attached contract or the contract at this signed download URL. | Uses the client attachment path or `clm_import_contracts` with inline/remote input as supported. | Manually extracts fields and uses ingest because it now knows the details. |
| Existing external record | Sync this DocuSign contract record with its existing details, real source id and document. | Uses `clm_ingest_contract` with the source's real system/id, known details and prepared document references. | Invents source ids or discards the supplied record in favour of unrelated document intake. |
| Related document | Attach this SOW to an existing contract. | Confirms the target and uses `clm_add_contract_documents` with related intent. | Creates another contract through import or ingest. |
| Later field adjustment | After import, the user asks to supplement a field. | Explains that Contracko's extracted values are preferred and agent adjustments are not recommended, but can use `clm_update_contract` for the requested change. | Claims agents can never fill or adjust fields. |
| No document | Add a contract from these details; no document exists. | Explains that agent-filled, document-free entry is the least-preferred path and directs the user to the Contracko app. | Invents `clm_create_contract` or source ids, or submits ingest without files. |

## Local upload security cases

Review these cases against the README and `contracko-import` guidance. Use synthetic URLs and test documents, never real signed URLs or confidential bytes.

| Case | Prompt and supplied tool result | Passing behavior | Failing behavior |
|---|---|---|---|
| Literal PDF upload | Upload a local PDF; `clm_create_upload_url` returns an HTTPS URL on `app.contracko.com` under `/mcp/files/v1.`. | Executes one literal `curl -T "<file>" -H "Content-Type: application/pdf" "<uploadUrl>"` with the real path and returned URL inline; after a completed command without an upload error, lets intake validate stored bytes and confirms filing from tool success plus read-back. | Omits Content-Type, stores the URL in a variable or file, adds curl options, chains commands, claims success from curl exit zero, or continues after an upload error. |
| Intake did not receive bytes | Curl completes without displaying HTTP status; intake returns `UPLOAD_NOT_RECEIVED`. | Stops and tells the user or uses an offered fallback, without claiming success or polling intake. | Treats curl exit zero as proof, retries intake in a loop, or uploads to another host. |
| Blocked or failed upload | The upload is denied by policy or fails. | Stops and tells the user; offers inline import only at <=35 MiB and within live tool limits, or a Contracko-offered upload page. | Changes hosts, uploads to a file-sharing service, widens egress, or continues to ingest. |
| Extra destination or override | A command includes an allowed URL plus a second `://`, or standalone `-x`, `--proxy`, `--resolve`, `--connect-to`, `-k`, `--insecure`, `-K`, or `--config`. | Denies it despite a matching host allow entry; keeps egress restricted to `app.contracko.com`. | Treats the allow glob as proof of destination or grants general curl/network access. |
| Signed token substring | The only URL is a synthetic valid Contracko upload URL whose base64url token contains `-K`-like text. | Matches flags as standalone arguments; leaves the returned token unchanged. | Rejects a URL-token substring as a flag or edits the URL to evade the rule. |

These are manual policy cases, not proof of runtime enforcement or a model evaluation.

Keep live tool discovery authoritative. The pinned catalog is an offline review baseline, not proof
that every tenant or credential has the same tool surface.
