---
name: contracko-import
description: Imports contracts into Contracko from disk, Google Drive, SharePoint, Box or a URL. Use to onboard, migrate, bulk-upload, or file a signed PDF.
---

# Importing contracts into Contracko

Onboarding is this skill plus types in [contracko](../contracko/SKILL.md). Find and file here. Shape types after extraction, not before.

## Find the files first

Contracko MCP does not browse disks or cloud drives. Use the file, Google Drive, SharePoint, Box or OneDrive tools *you already have*. If you have none, ask the user to share the folder, attach files, or paste a signed download link.

1. Ask where the contracts live. Typical: a laptop folder, Google Drive, SharePoint, Box, email exports.
2. List candidates. Keep PDFs and DOCX (and the other ingest types). Skip obvious noise (photos of whiteboards, duplicate `final-final-v3`).
3. Group related files before filing: an MSA with its SOWs, a signed copy next to an unsigned draft. Say the grouping out loud. Nothing in Contracko detects it for you.
4. Confirm workspace, count and names before a bulk send. A single file they just handed you needs no ceremony.

Do not publish a confidential file to a public URL so `remote` import works. A signed or authenticated link from their own store is the remote path.

## Getting the bytes there

MCP has no file transfer, so where you run decides how a document reaches Contracko. Decide this first, before anything else.

| You are | Use | Why |
|---|---|---|
| in a shell with network access | `clm_create_upload_url` → PUT → `clm_import_contracts` with `kind: "upload"` (Contracko extracts), or → `clm_ingest_contract` (you supply the fields) | the bytes go machine-to-machine and never touch your context |
| in ChatGPT with the file attached | `clm_import_files` with the attached files | Contracko downloads them from ChatGPT's file service. Ask for an attachment if there is none. |
| in Claude chat (web or desktop) with the file attached | the sandbox upload first (`clm_create_upload_url`, one `curl -T` from the sandbox, then `clm_import_contracts` with `kind: "upload"`). If network access is blocked, base64 the same file in the sandbox and send `kind: "inline"`. Only if neither transfer works, `clm_create_upload_session` | ask permission before reading or uploading the attached file (usually under `/mnt/user-data/uploads/`). Inline is up to 35 MiB per file and within the client's tool-argument limit. |
| without network, and the file is tiny | `clm_import_contracts` with `kind: "inline"` | base64 travels through your context: roughly 1.4x the file size, so a 50 KB PDF costs around 17k tokens. The cap is 35 MiB per file, but clients manage only tens of KB in practice. |
| unable to send the bytes at all | `clm_create_upload_session`, then give the user its `uploadPageUrl` | the user adds the files in their browser, signed in to Contracko, within the hour |
| pointing at a URL Contracko can fetch | `clm_import_contracts` with `kind: "remote"` | Contracko downloads it directly. |

How the tested clients behave:

- **Claude Code** uploads from the user's own shell. In sandbox mode, `app.contracko.com` must be allowed.
- **Claude web and desktop chat** run the PUT from the code-execution sandbox, which works only when `app.contracko.com` is an allowed egress domain.
- **Codex CLI** needs `sandbox_workspace_write.network_access = true` for the PUT, with egress limited to `app.contracko.com` where the environment can enforce it. Non-interactive runs need approval for `clm_import_contracts`.
- **Cursor CLI** works only with one plain `curl -T "<file>" -H "Content-Type: <mimeType>" "<uploadUrl>"`, the URL written inline: no chaining, variables, or URL files. **Cursor web** limits attachments to 4 MB, so use the upload link.
- **ChatGPT**'s sandbox has no internet. Use `clm_import_files`; some developer-mode connectors do not pass attached files through, so fall back to the upload link.

If the PUT cannot reach Contracko, follow `ifUploadUrlUnreachable` in the upload result rather than preparing the file again. **Upload only to the returned `uploadUrl`. Never send a contract to a third-party host or file-sharing service**, including to work around a block. If the upload is blocked, stop and tell the user.

**Never publish a contract to a public URL to make `remote` work.** A signed or authenticated link from the user's own document store is what that option is for.

Requires `contract:write`. Where the tools are absent from your list, the credential is the problem: see the [contracko](../contracko/SKILL.md) skill.

If the document is already associated with a contract the user can see, import and ingest return a duplicate conflict instead of a second copy. Tell them which contract holds it. Only retry with `allowDuplicate: true` if they insist on another copy.

To add a file to an *existing* contract (draft, related, or replace the primary), use `clm_add_contract_documents` with a new idempotency key. That is not an import.

## Confirm before writing

Nothing here can be undone. Contracko deliberately keeps delete and archive out of an agent's hands, so a batch sent to the wrong workspace is cleaned up by hand in the web app, one record at a time.

Before a bulk import, put three things in front of the user and wait: the workspace `auth_validate` reports, how many documents you are about to send, and what they are. A single file the user just handed you needs no ceremony. Fifty files out of a shared drive does.

## Managed import

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
| `UPLOAD_NOT_RECEIVED` | The file never reached the prepared destination. | Run the upload command from `clm_create_upload_url` again and retry the intake, or send a tiny file inline. Do not poll intake as an upload check. If the upload keeps failing, give the user the upload link. |
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

## Prepare and file

Three steps, per contract, then a read-back. This is also the "add your first contract" sequence that `clm_search_tools` returns for an empty workspace.

1. `clm_create_upload_url` with `fileName`, `mimeType` and `fileSize`. Returns a signed destination valid for one hour, and an opaque `uploadReference`.
2. `PUT` the bytes only to that URL with the matching `Content-Type`. A plain HTTP request, not a tool call. Intake checks whether the bytes arrived; the curl exit code alone is not confirmation.
3. `clm_ingest_contract` with `externalSystem`, `externalId`, the `contract` object, and the upload references, `isPrimary` on the main document.
4. `clm_get_contract` on the returned contract to confirm it landed.

Accepted: PDF, DOCX, TXT, RTF, JPEG, PNG. 50 MiB per file, 100 files per contract. To let Contracko extract instead, replace step 3 with `clm_import_contracts` and a `kind: "upload"` file carrying the same reference. Contracko cleans up uploads that are never imported or ingested, so use the reference within the hour.

### The rule that costs a call

`contract.endDate` is absent from the schema's required list and required anyway. Omit it and the call fails with a 400 whose only detail is `code: "custom"` on `endDate`, which tells you nothing.

The rule: **send `endDate`, or send `isOpenEnded: true`.** A contract with no end date by design is legitimate, and that flag is how you say so.

Four defaults apply silently, so set them from the document rather than letting them land: `status` becomes `active`, `autoRenewing` true, the renewal period 1 year, the notice period 1 month. You have read the contract; use what it says.

`externalSystem` and `externalId` are the source system's identity for this contract, and they are how a re-run recognises what it already filed. Where there is no source system, choose something stable and honest about its origin.

## Working the upload path

The three steps, with the parts that actually trip agents up.

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

If the upload fails or policy blocks it, stop and tell the user. Offer `clm_import_contracts` with `kind: "inline"` only for files <=35 MiB that also fit the live tool's file and encoded-payload limits (the pinned release limits are listed above), or give the user the `clm_create_upload_session` upload link. Do not weaken policy or try a different host.

Cursor, Codex, and Claude execution environments must allowlist only `app.contracko.com` for this upload, not general network egress. Cursor's narrow shell allow entry is `Shell(curl:*https://app.contracko.com/mcp/files/v1.*)`. This glob alone is not a security boundary: also deny a second `://` in the command and the standalone flag arguments `-x`, `--proxy`, `--resolve`, `--connect-to`, `-k`, `--insecure`, `-K`, and `--config`. Match flag arguments, not substrings inside the signed URL: base64url tokens can contain `-K`-like substrings. See the [README upload policy](https://github.com/contracko/contracko-skills#local-upload-policy) for operator setup.

**3. Read the document for its content, not its bytes.** To fill the contract and its analysis you need the text, and text is cheap where base64 is not. Extract it locally:

```bash
pdftotext -layout contract.pdf -      # PDF
textutil -convert txt -stdout f.docx  # DOCX on macOS
```

A 50 KB PDF is perhaps 4k tokens as text against 17k as base64, and the text is the part you can actually reason over.

Then call `clm_ingest_contract` with the reference, the metadata you read off the document, and a filled `summary.analysis`.

### For a folder

Do the loop, one contract per document, and keep the whole file out of your context every time: size it, upload it, extract its text, ingest it, move on. Confirm the batch with the user before starting, as above.

Where several files clearly belong to one agreement, a master and its order forms, or a signed and unsigned copy of the same contract, say so before filing them as unrelated records. Nothing detects that for you, and a migration out of a shared drive is full of it.

## When you ingest, do the extraction properly

A contract filed through ingest does not go through Contracko's extraction pipeline. What lands is what you send, so sending a title and two dates produces a thin record that looks identical to a rich one until someone opens it.

`contract.summary.analysis` is built for exactly this, and it takes far more than most callers give it: `risks[]`, `obligations[]`, `warranties[]`, `riskAllocation[]`, `gaps[]` and `deviations[]`, each with a severity, a headline and an `evidenceQuote`, plus `fieldEvidence` pointing at where each extracted value came from. There is also `proposedCategoryFields` for the custom fields this contract implies.

You have read the document. Fill them. Quote verbatim in every `evidenceQuote`, because those are what the app highlights in the document viewer, and a paraphrase highlights nothing.

An ingest that skips the analysis is the one case where the manual path really is worse than the managed one. Done properly it is equal, and it costs no context.

## When something goes wrong

| Symptom | Reading |
|---|---|
| 409 on a retry | the idempotency key is spent; where the payload is identical, the import already exists, so go look it up |
| stuck in `extracting` | normal for minutes; keep honouring `pollAfterMs` before calling it stuck |
| `retryable: false` on an item | the document itself is the problem, so surface it to the user |
| 400 `code: "custom"` on `endDate` | the open-ended rule above |
| the tools are missing entirely | `contract:write` was not granted |
