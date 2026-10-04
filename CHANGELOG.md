# Changelog

User-facing changes to the Contracko skills and plugin packages. Client manifests (Claude, Codex, Cursor, Copilot, Gemini, MCP Registry) share one version; the Agent Plugins package and release bundles follow the `v*` release tag line.

## 0.7.7, 2026-10-04

- Cursor now has its own shorter plugin description, because the Cursor marketplace truncated the full one mid-sentence. Every other client keeps the full description.

## 0.7.6 (Agent Plugins 0.8.2), 2026-10-03

- Added `clm_search_tools` guidance: use it when unsure which tool fits, before multi-step jobs, and for the first contract in an empty workspace.
- Added an "Add your first contract" job: `clm_create_upload_url`, upload, `clm_ingest_contract`, then read back.
- The tool index now lists all 50 tools, including document re-reads and their read-only findings. `clm_get_folder_access` is gone; `clm_get_folder` shows who can see a folder.
- Connect steps are now sign in or start the trial, then consent. There is no workspace choice.
- Event and notification writes now say that Contracko emails each notification to its recipient.
- Party tax and registration numbers are documented as organisation-only.
