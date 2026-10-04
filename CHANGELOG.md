# Changelog

User-facing changes to the Contracko skills and plugin packages. Client manifests (Claude, Codex, Cursor, Copilot, Gemini, MCP Registry) share one version; the Agent Plugins package and release bundles follow the `v*` release tag line.

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
