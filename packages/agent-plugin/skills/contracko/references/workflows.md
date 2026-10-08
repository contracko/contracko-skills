# Jobs

Use live tool discovery first. These are user jobs, not a substitute for discovered schemas. Mechanics live in the named skill. When a job needs several tools and the order is unclear, `clm_search_tools` returns the listed tools and their step sequences for that task.

Contract-register workflows use CLM (`clm_*`) and never need Parser credits, including bulk imports. Contracko Parser (`parser_*`) is separate bulk document processing using Parser credits, not a step to add contracts to your register.

## Add your first contract

**They say:** I just signed up, the workspace is empty, add this contract, try it with one file.

Contracko's server instructions open with this invitation for a new workspace: ask the user to attach the file or give its path, say you will upload it so Contracko can extract the dates and terms, and ask permission before reading or uploading anything. Connecting imports nothing, and examples are not the user's own contracts; use their own document. Parser credits are not needed to add a contract.

Run `auth_validate`, then `clm_search_tools` with "Add my first contract" to confirm the steps this connection can run. For one local file, prepare, upload, and ingest:

1. `clm_create_upload_url` with the file's `fileName`, `mimeType`, and `fileSize`. Measure the file; do not read it to size it.
2. HTTP `PUT` the bytes to the returned URL with the same `Content-Type`, and expect a 2xx status.
3. `clm_ingest_contract` with the `uploadReference`, the contract details from the document, and its analysis. Send `endDate` or `isOpenEnded: true`.
4. `clm_get_contract` to read back the new record.

To let Contracko extract instead, replace step 3 with `clm_import_contracts` and a `kind: "upload"` file carrying the same `uploadReference`.

After intake is accepted, first tell the user Contracko received their contract and is reading it now; longer contracts take a little while. Send this before any status check. Then call `clm_get_import_status` with `processing.jobId`: it returns a snapshot, and `wait: true` waits at most 25 seconds, so repeat while it is still being read and show the elapsed time. Specific upload errors (`UPLOAD_NOT_RECEIVED`, `INVALID_FILE_CONTENT`) and their recovery are in [contracko-import](../../contracko-import/SKILL.md#upload-errors).

Where you run decides the upload:

| You are in | Do |
|---|---|
| a shell with network access (Claude Code, Codex with network on, Cursor CLI, Claude chat with `app.contracko.com` added under Settings > Capabilities > Code execution and file creation > Additional allowed domains) | the steps above |
| Claude chat (web or desktop) | ask permission, then the sandbox upload; if the network is blocked, inline base64; only if neither works, the upload link |
| ChatGPT | ask for the file as an attachment, then `clm_import_files`; otherwise the upload link |
| an environment with no network | inline import only for a tiny file; otherwise `clm_create_upload_session` and give the user its `uploadPageUrl` |

Upload only to the returned `uploadUrl`, never to a third-party host. If the upload is blocked, stop and tell the user. [contracko-import](../../contracko-import/SKILL.md) owns these paths and their limits. After the first contract lands, list the extracted types and parties before designing anything.

**Done when:** the contract reads back in the intended workspace, and the user knows it is `pending-review` until a person confirms it.

## Bring contracts in

**They say:** import these, onboard us, migrate the archive, look on disk, Google Drive, SharePoint, or Box.

Find the files with the available file or cloud tools, confirm the set, then import them. Contracko extracts types and parties. Review the extracted configuration before adding more. [contracko-import](../../contracko-import/SKILL.md) owns import; [SKILL.md](../SKILL.md) owns types, fields, parties, and folders.

If the user also wants filing, inspect visible folders, confirm the proposed destination and any batch, then create, rename, move, or file through the discovered folder tools. Do not infer a folder from a missing or unavailable filing state.

**Done when:** the documents are contracts in the intended workspace, types cover the user's questions, and each requested filing change has been read back.

## What is coming up

**They say:** notice dates, end dates, renewals, annual review, reminders, notifications.

Get today's date from the environment. Use inclusive end-date or notice-date filters for dated candidates and complete every returned page. `autoRenewing` identifies a renewal; a date window alone does not. For contracts ending OR needing notice, run separate complete queries and deduplicate by contract ID. Use existing system events for renewal or notice notifications. [contracko-review](../../contracko-review/SKILL.md) owns the calendar.

**Done when:** the user has the urgent bucket, its dates, and any requested notification confirmed as created.

## Compare these

**They say:** two proposals, vendor A versus B, or a redline versus a previous draft.

Get both records, analyses, and cited document text for disputed terms. Compare metadata and quotes in a table. Add related versions to the existing contract when the user identifies them as versions of one agreement. [contracko-review](../../contracko-review/SKILL.md) owns comparison.

**Done when:** the user can choose with supporting quotes.

## Audit for risk

**They say:** risks, liability, caps, indemnity, or what could hurt us.

Complete the relevant portfolio page set before opening hot contracts. Use `clm_get_contract_analysis`, contract liability fields, and cited clauses. A null analysis field does not prove no risk. Where a saved value looks wrong, read any completed document re-read with `clm_list_contract_reconciliations` and `clm_get_contract_reconciliation`; reading changes nothing. [contracko-review](../../contracko-review/SKILL.md) owns audit.

**Done when:** every material finding has a quote, a severity, and a clear extraction-review status.

## File and type contracts

**They say:** organise, folders, contract types, custom fields, or filing.

Import before designing a new workspace. Use types and custom fields for the questions the user asks, then propose and confirm any changes. List visible folders with `clm_list_folders`, inspect a chosen destination, confirm the destination and bulk changes, then use the discovered folder and contract move tools. `folderId: null` unfiles only when the user asks. Access reads are informational; access changes and folder deletion are in the app.

To find unfiled contracts, complete the relevant contract pages and inspect `filing.kind`. Do not send `folderId: null` as a list filter. `unavailable` does not identify an unfiled contract or a hidden folder.

**Done when:** types and fields match the user's model, each requested filing change is verified, and any access work is clearly handed to the app.

## Priorities and gaps

**They say:** report, portfolio, what matters this quarter, or what are we missing.

Start with the narrowest supported `clm_list_contracts` filters. Filters combine with AND. Complete each filtered page set. For OR windows, use complete separate queries and deduplicate. For value, currency, missing fields, custom-field gaps, or unfiled audits, evaluate the complete narrowed result locally. Separate monetary totals by currency. [contracko-review](../../contracko-review/SKILL.md) owns reporting.

**Done when:** the user has ranked results, named gaps, and the count of the completed result set.

## Start a new agreement

[contracko-create](../../contracko-create/SKILL.md) owns the questionnaire and filing the executed copy. Drafting and signature stay in the app.
