# Changelog

User-facing changes to the Contracko skills and plugin packages. Client manifests (Claude, Codex, Cursor, Copilot, Gemini, MCP Registry) share one version; the Agent Plugins package and release bundles follow the `v*` release tag line.

## 0.7.12 (Agent Plugins 0.8.7), 2026-10-08

- CLM and Contracko Parser are described as separate products. Adding, importing and managing contracts (`clm_*`), including bulk imports, never needs Parser credits. `parser_*` is separate bulk document processing that uses Parser credits.
- The 7-day CLM free trial is documented with its whole-trial caps: 3 AI extractions (imports and document re-reads count), 10 Clara messages and 1 signature request. At a cap, tell the user it is a plan notice, keep accepted work and do not retry. Subscribing lifts the caps and keeps the original free end date. Parser credits do not lift them.
- Parser's free allowance is 20 credits once per workspace without an eligible Parser subscription, not 20 extractions. An extraction costs 1 to 5 credits per document, and review doubles the cost.
- `npx -y @contracko/mcp --help` prints this guidance without connecting.

## 0.7.11 (Agent Plugins 0.8.6), 2026-10-07

- Claude chat (claude.ai, Claude Desktop chat, Cowork, mobile) blocks outbound hosts in the code-execution sandbox by default. The README and import skill now match what Contracko tells Claude users: if available, open Settings > Capabilities > Code execution and file creation, allow network egress, and add `app.contracko.com` under Additional allowed domains.
- On Team and Enterprise, an organization Owner allows it once for everyone under Organization settings > Capabilities > Package managers + specific domains, adding `app.contracko.com`.
- Local agents (Claude Code, Cursor, Codex CLI) upload from your own shell and only need the command approved. If a strict sandbox blocks network access, allow `app.contracko.com` in its sandbox or network settings. ChatGPT needs no setting.

## 0.7.10 (Agent Plugins 0.8.5), 2026-10-07

Matches the Contracko MCP behaviour live in production on 2026-10-07. Agents see no new tools.

- First contract: the skills describe the server's first-contract invitation (attach the file or give its path, ask permission before reading or uploading, use the person's own document).
- After an import or ingest is accepted, tell the user Contracko received their contract and is reading it now before any status check or wait. For several files, say how many were received.
- `clm_get_import_status` takes `processing.jobId` and returns a snapshot by default. `wait: true` waits at most 25 seconds. Still-reading results show elapsed time, with singular or plural wording and a count of contracts read for several files.
- Upload errors have recovery steps: `UPLOAD_NOT_RECEIVED` (run the upload again, or send a tiny file inline), `UPLOAD_EXPIRED` (prepare again) and `INVALID_FILE_CONTENT` (ask for the file again).
- Claude chat (web and desktop) order: upload from the sandbox with one `curl -T`, then inline base64 if the network is blocked, and the upload link only if neither works.
- Contracko serves MCP protocol 2026-07-28 alongside the earlier versions. No skill change is needed.
- The README now says to open a skills-bundle sync PR after each MCP release reaches production.

## 0.7.9 (Agent Plugins 0.8.4), 2026-10-04

- Local uploads now use one literal curl command with the required Content-Type header and only the returned Contracko upload URL. This is the single-command upload that is now live in production; the README and the Cursor, Codex, and Claude notes use the same command.
- Contract files go only to the returned upload URL on `app.contracko.com`, never to a third-party host or file-sharing service, even to work around a blocked upload. If the upload fails or is blocked, the assistant stops and tells you.
- A finished curl command does not prove the bytes arrived. Filing is confirmed from the intake result and the contract read-back, and an `UPLOAD_NOT_RECEIVED` result stops the import.
- Added a README upload policy for Cursor, Codex, and Claude: allow only `app.contracko.com`, with a narrow Cursor shell entry and denials for extra destinations and unsafe curl flags.

## Maintenance, 2026-10-04

- CI now checks the complete canonical skill tree against the generated Agent Plugins package, including newly added skills that the generator would otherwise omit.

## 0.7.8 (Agent Plugins 0.8.3), 2026-10-04

Matches the Contracko MCP surface live since 2026-10-04 (52 tools, about 24k tokens of tool descriptions).

- Two new tools: `clm_import_files` imports files attached in ChatGPT, and `clm_create_upload_session` returns an upload link where the person adds files in their browser.
- After a signed upload, `clm_import_contracts` now accepts `kind: "upload"`, so Contracko extracts the file without its bytes passing through the assistant. Inline files go up to 35 MiB each; upload and remote files go up to 50 MiB.
- The import skills now choose the upload path by client: a shell with network uses the signed upload, ChatGPT uses attached-file import, and a client without network sends only tiny files inline and otherwise gives the user an upload link. Contract files go only to the returned Contracko upload address, never to a third-party host.
- The README explains how to add a contract on Claude web and desktop, Claude Code, ChatGPT, Codex, and Cursor.
- Comments now say that Contracko emails the contract's followers.

## 0.7.7, 2026-10-04

- Cursor now has its own shorter plugin description, because the Cursor marketplace truncated the full one mid-sentence. Every other client keeps the full description.

## 0.7.6 (Agent Plugins 0.8.2), 2026-10-03

- Added `clm_search_tools` guidance: use it when unsure which tool fits, before multi-step jobs, and for the first contract in an empty workspace.
- Added an "Add your first contract" job: `clm_create_upload_url`, upload, `clm_ingest_contract`, then read back.
- The tool index now lists all 50 tools, including document re-reads and their read-only findings. `clm_get_folder_access` is gone; `clm_get_folder` shows who can see a folder.
- Connect steps are now sign in or start the trial, then consent. There is no workspace choice.
- Event and notification writes now say that Contracko emails each notification to its recipient.
- Party tax and registration numbers are documented as organisation-only.
