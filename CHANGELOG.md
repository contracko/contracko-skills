# Changelog

User-facing changes to the Contracko skills and plugin packages. Client manifests (Claude, Codex, Cursor, Copilot, Gemini, MCP Registry) share one version; the Agent Plugins package and release bundles follow the `v*` release tag line.

## 0.7.7 (Agent Plugins 0.8.3), 2026-10-04

- The Claude install notes now say how to give Contracko a file on web, desktop, Cowork, mobile, and Claude Code. On web and desktop, allowing `app.contracko.com` for code-execution network egress makes large files fast.
- The import skills now choose the upload path by surface: a signed upload from a shell, the upload from Claude's chat sandbox only when the domain is allowed (otherwise, or on a 403 or challenge page, the same file goes inline without preparing again), an upload page link without code execution, and attached-file import in ChatGPT.

## 0.7.6 (Agent Plugins 0.8.2), 2026-10-03

- Added `clm_search_tools` guidance: use it when unsure which tool fits, before multi-step jobs, and for the first contract in an empty workspace.
- Added an "Add your first contract" job: `clm_create_upload_url`, upload, `clm_ingest_contract`, then read back.
- The tool index now lists all 50 tools, including document re-reads and their read-only findings. `clm_get_folder_access` is gone; `clm_get_folder` shows who can see a folder.
- Connect steps are now sign in or start the trial, then consent. There is no workspace choice.
- Event and notification writes now say that Contracko emails each notification to its recipient.
- Party tax and registration numbers are documented as organisation-only.
