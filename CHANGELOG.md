# Changelog

User-facing changes to the Contracko skills and plugin packages. Client manifests (Claude, Codex, Cursor, Copilot, Gemini, MCP Registry) share one version; the Agent Plugins package and release bundles follow the `v*` release tag line.

## 0.7.10 (Agent Plugins 0.8.5), 2026-10-07

- Claude chat surfaces (claude.ai, Claude Desktop chat, Cowork, mobile) block outbound hosts in the code-execution sandbox by default. The README and import skill now give the exact step: add `app.contracko.com` under Settings > Capabilities > Code execution and file creation > Additional allowed domains. Claude then uploads attached contracts itself.
- On Team and Enterprise, an organization Owner can allow `app.contracko.com` once for all members.
- Local agents (Claude Code, Cursor, Codex CLI) upload from your own shell and only need the command approved. If a strict sandbox blocks network access, allow `app.contracko.com` in its sandbox or network settings. ChatGPT needs no setting.

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
