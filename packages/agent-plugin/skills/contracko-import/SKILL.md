---
name: contracko-import
description: Imports contracts into Contracko from disk, Google Drive, SharePoint, Box or a URL. Use to onboard, migrate, bulk-upload, or file a signed PDF.
---

# Importing contracts into Contracko

For readiness, product choice and refusals, follow [contracko](../contracko/SKILL.md#connect-and-discover). Imports need `contract:write`. This skill owns transfer and intake; shape types after extraction.

## Choose import or sync

**User-provided documents go to `clm_import_contracts`, never `clm_ingest_contract`.** This includes files from the user's disk, Google Drive or any cloud drive, chat attachments, and URLs. Let Contracko extract the details; do not read the document and extract fields yourself. Follow the [client transfer path](#getting-the-bytes-there): prepare with `clm_create_upload_url`, upload the bytes, then import with `kind: "upload"` and the returned `uploadReference`, or use `kind: "inline"` or `kind: "remote"` for a reachable URL. Client attachment and upload-panel flows below also use managed import, not sync.

Use `clm_ingest_contract` only to sync a record that already exists in another system (DocuSign, a CRM, Zapier), with that system's existing contract details and real record id. Never invent `externalSystem` or `externalId` to file a document. Follow [sync submission](#sync-a-record-from-another-system).

For related documents on an existing contract, use `clm_add_contract_documents`; follow [Add contract documents](#add-contract-documents).

## Find the files first

Contracko MCP does not browse disks or cloud drives. Use the file, Google Drive, SharePoint, Box or OneDrive tools *you already have*. For a cloud-drive file, download or fetch its bytes with those tools, then follow the import transfer path below. A drive connector is a file source, not an external contract record for sync. If you have none, ask the user to share the folder, attach files, or paste a signed download link.

Ask where the contracts live and list supported documents, skipping noise and duplicates. Group related versions, an MSA with its SOWs, and signed with unsigned copies before filing them as unrelated records. Confirm the grouping with the user.

## Getting the bytes there

MCP has no file transfer, so where you run decides how a document reaches Contracko. Decide this first, before anything else.

| You are | Use | Why |
|---|---|---|
| in a shell with network access | [Working the upload path](#working-the-upload-path), then [managed import](#managed-import) | the bytes go machine-to-machine and never touch your context |
| in ChatGPT with the file attached | `clm_import_files` with the attached files | Contracko downloads them from ChatGPT's file service. Ask for an attachment if there is none. |
| in Claude chat (web, desktop, Cowork or mobile) | follow [Claude chat transfer order](#claude-chat-transfer-order) | the panel lets the person choose documents without reading sandbox bytes |
| without network, and the file is tiny | `clm_import_contracts` with `kind: "inline"` | base64 travels through your context: roughly 1.4x the file size, so a 50 KB PDF costs around 17k tokens. The cap is 35 MiB per file, but clients manage only tens of KB in practice. |
| unable to send the bytes at all | `clm_create_upload_session`, then give the user its `uploadPageUrl` | the user adds the files in their browser, signed in to Contracko, within the hour |
| pointing at a URL Contracko can fetch | `clm_import_contracts` with `kind: "remote"` | Contracko downloads it directly. |

### Claude chat transfer order

Show `clm_show_upload_widget` first when available. Ask the person to choose documents there. Sandbox PUT is allowed only if they say they allowed `app.contracko.com`, or the panel is unavailable; ask permission before reading or uploading a sandbox file.

After blocked PUT, stop and tell the user, then return to the panel when available. If the panel is unavailable or fails, try inline bytes within the live file, encoded-payload and client limits, then an upload link only when earlier paths cannot work or fail.

For optional sandbox access, use **Settings > Capabilities > Code execution and file creation**, enable network egress if available, and add only `app.contracko.com` under **Additional allowed domains**. On Team and Enterprise, an Owner uses **Organization settings > Capabilities > Package managers + specific domains**.

### Other client limits

- **Claude Code:** approve the shell command; strict sandboxes need host-only access to `app.contracko.com`.
- **Codex CLI:** PUT needs `sandbox_workspace_write.network_access = true`, with egress limited to that host. Non-interactive imports need tool approval.
- **Cursor CLI:** use the literal upload command in [Working the upload path](#working-the-upload-path). **Cursor web:** attachments are limited to 4 MB, so use the upload link.
- **ChatGPT:** its sandbox has no internet. If the connector cannot pass attachments to `clm_import_files`, use the upload link.

Follow `ifUploadUrlUnreachable` if PUT cannot reach Contracko. Use only returned upload destinations. Never publish a contract to a public URL to make remote import work; use a signed or authenticated link from the user's own store.

If the document is already associated with a contract the user can see, import and ingest return a duplicate conflict instead of a second copy. Tell them which contract holds it. Only retry with `allowDuplicate: true` if they insist on another copy.

### Add contract documents

For an existing contract, read it with `clm_get_contract` and confirm the target before calling `clm_add_contract_documents`. Send its `id`, a new `idempotencyKey` and `documents` with `intent: "related"`, `"draft"` or `"replace"` (at most one replacement per request). Sources are inline bytes or a reachable signed download URL, not prepared upload references. If neither source works, report the transfer blocked rather than importing a new contract. Read the contract back to confirm the document change.

## Confirm before writing

Nothing here can be undone. Contracko deliberately keeps delete and archive out of an agent's hands, so a batch sent to the wrong workspace is cleaned up by hand in the web app, one record at a time.

Before a bulk import, put three things in front of the user and wait: the workspace `auth_validate` reports, how many documents you are about to send, and what they are. A single file the user just handed you needs no ceremony. Fifty files out of a shared drive does.

## Managed import

For a first contract, ask the user to attach their own file or give its path, explain that Contracko will extract dates and terms, and ask permission before reading or uploading. Connecting imports nothing.

One call per batch, up to 100 documents, one managed contract per document.

```json
{
  "idempotencyKey": "migration-2026-09-batch-01",
  "files": [
    {"kind": "inline", "fileName": "vendor-msa.pdf", "mimeType": "application/pdf", "dataBase64": "..."}
  ]
}
```

Files are `upload` (the `uploadReference`, `fileName`, `mimeType` and `fileSize` from `clm_create_upload_url`, up to 50 MiB), `inline` base64 (up to 35 MiB per file), or `remote` with a `downloadUrl` and `fileSize` (up to 50 MiB).

The `idempotencyKey` is bound to the payload. Replaying it with the same files returns the original import; replaying it with different files returns a 409, which says the key is spent rather than that the import failed. One key per batch, named so a human can recognise it later.

### After intake is accepted

1. **Say it first.** Before any status check or wait, tell the user Contracko received their contract and is reading it now. For several files, say how many contracts were received. Longer contracts can take a little while; do not promise a duration. Send this message even when the files arrived through an upload link.
2. **Check with the job id.** Pass `processing.jobId` from the import or ingest result to `clm_get_import_status`. A legacy `importId` or an upload link's `uploadSessionId` also works; supply exactly one handle.
3. **Snapshot or wait.** A plain call returns an immediate snapshot. `wait: true` waits until the job finishes or at most 25 seconds, so use it only after the message in step 1. No call can wait longer.
4. **Report progress.** If the result says the contract is still being read, tell the user, show the elapsed time (and, for several files, how many are read), and check again. Repeat until it finishes. Hold the success message until the documents are actually filed, then summarize the extracted fields in the same conversation.

The wording follows the count: one contract reads "Your contract is still being read", several read "Your contracts are still being read" with "N of M contracts read". Read each item's `intakeOutcome`.

### Upload errors

| Code | Meaning | Do |
|---|---|---|
| `UPLOAD_NOT_RECEIVED` | The file never reached the prepared destination. | Follow the returned hint and [transfer order](#getting-the-bytes-there); do not poll intake to check an upload. |
| `UPLOAD_EXPIRED` | The prepared upload passed its hour. | Prepare the file again, upload to the new URL, and use the new reference. |
| `INVALID_FILE_CONTENT` | The content is not valid base64 or not a supported document. | Ask the user for the file again. Do not resend the same bytes. |

Per document you get `status`, a `contractId` as soon as the record exists, and on failure an `errorCode` with a `retryable` flag. Retry what is marked retryable, under a new key, and treat the rest as documents that need a human.

### What extraction gives you for free

Worth telling the user, because it changes what they should do first. On a plain NDA, in a workspace with no configuration at all, the import produced:

- title, start and end dates, renewal and notice terms
- both parties, created as counterparty records and linked with roles
- a new contract type, with custom fields inferred from the document
- governing law, jurisdiction, liability summary, notice instructions
- a full analysis with obligations and risks, through `clm_get_contract_analysis`

So for a first-time user with a folder of contracts: import first, configure after. Hand-built contract types are work the extraction was going to do, and then has to reconcile against. After the batch lands, list types and make them comprehensive — [contracko](../contracko/SKILL.md) owns that half.

New contracts land as `entityStatus: "pending-review"`. Say so. A human is expected to confirm the extraction, and nothing about a successful import marks the data as verified.

Once documents are in, the questions start: renewals, notice dates, risk, and what the workspace now holds. That is [contracko-review](../contracko-review/SKILL.md). If the user also asks to place imported contracts in folders, use the confirmed filing workflow in [contracko](../contracko/SKILL.md).

## Sync a record from another system

For `clm_ingest_contract` ("Sync contract from another system"), first apply [Choose import or sync](#choose-import-or-sync).

Prepare and upload the documents through [Working the upload path](#working-the-upload-path), or reuse their existing references. Submit `externalSystem`, `externalId`, the source's `contract` details, and `files` containing each unchanged `uploadReference`, `fileName`, `mimeType` and `fileSize`; mark the main document `isPrimary`. Discovery requires `uploadReference`; legacy `r2Key` is accepted only for compatibility and is hidden from discovery. Never derive either reference from a storage key.

Reusing the same source id with identical details and document references returns the same contract; keep those inputs unchanged on retry. Follow [accepted intake](#after-intake-is-accepted) and read the resulting contract back.

Send `contract.endDate`, or `contract.isOpenEnded: true`. Set source values explicitly: otherwise `status` defaults to `active`, `autoRenewing` to true, the renewal period to 1 year and the notice period to 1 month.

## Working the upload path

Prepare with `clm_create_upload_url` using the actual `fileName`, `mimeType` and `fileSize`. Reuse an existing upload reference instead of uploading the same document again. Supported files: PDF, DOCX, TXT, RTF, JPEG and PNG, up to 50 MiB each. Upload destinations and unused references expire within an hour.

**1. Measure the file without reading it.** You need `fileSize` in bytes and a `mimeType`, and neither requires the contents:

```bash
stat -f%z contract.pdf          # bytes (macOS; stat -c%s on Linux)
file --mime-type -b contract.pdf
```

Reading a PDF to size it defeats the entire point of this path.

**2. PUT the bytes only to the returned `uploadUrl`.** `clm_create_upload_url` returns a destination valid for one hour and a reference. Verify that the destination is HTTPS on exactly `app.contracko.com`, under `/mcp/files/v1.`. Keep the returned URL unchanged. Never upload contract bytes to third-party hosts or file-sharing services, including as a workaround for a blocked upload.

For a PDF, execute exactly one literal command:

```bash
curl -T "<file>" -H "Content-Type: application/pdf" "<uploadUrl>"
```

Replace `<file>` with the local path and `<uploadUrl>` with the real returned URL inline when executing. For another accepted file type, use the matching declared `Content-Type`; the server requires this header. Run the upload as one command, with no chaining, subshell, URL file, variable, extra destination, or added curl options. Do not follow redirects. This plain curl command does not display HTTP status; exit code zero alone does not prove the bytes arrived. If it completes with no transport error or upload-error response, continue to the intake call using the returned reference, but do not claim upload or filing success yet. Contracko validates stored bytes before creating a contract. Confirm filing only from a successful intake result and the contract read-back. If intake returns `UPLOAD_NOT_RECEIVED`, stop and tell the user or use an offered fallback. Do not retry intake as an upload-status polling loop.

If upload fails or policy blocks it, stop and tell the user. Follow [transfer order](#getting-the-bytes-there); keep policy intact.

Cursor, Codex and Claude must restrict upload egress to `app.contracko.com`, not general network access. Without enforceable restrictions, keep uploads approval-gated or use a fallback. Cursor's narrow shell entry is `Shell(curl:*https://app.contracko.com/mcp/files/v1.*)`. Also deny a second `://` and standalone flags `-x`, `--proxy`, `--resolve`, `--connect-to`, `-k`, `--insecure`, `-K`, and `--config`. Match arguments, not substrings in base64url tokens. The glob alone is not a security boundary.

**3. Submit through the chosen intake path.** For a known external record, return to [sync submission](#sync-a-record-from-another-system); otherwise follow [managed import](#managed-import). Then follow [accepted intake](#after-intake-is-accepted) and read the resulting contracts back. Acceptance is not completed extraction. Related classification neither attaches to another contract nor searches for a parent.

## When something goes wrong

| Symptom | Reading |
|---|---|
| 409 on a retry | the idempotency key is spent; where the payload is identical, the import already exists, so go look it up |
| stuck in `extracting` | normal for minutes; keep honouring `pollAfterMs` before calling it stuck |
| `retryable: false` on an item | the document itself is the problem, so surface it to the user |
| 400 `code: "custom"` on `endDate` | the open-ended rule above |
| the tools are missing entirely | follow [readiness and recovery](../contracko/SKILL.md#errors) |
