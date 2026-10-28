# ChatGPT package

Build from the repository root with `bash build-zips.sh`. The output is `dist/contracko-agent-plugin-chatgpt.zip`. Versions come from `packaging/manifest.json`.

The archive contains `.codex-plugin/plugin.json`, `.mcp.json`, `assets/icon.png` and `skills/`. The builder copies the canonical skill tree and overlays the complete file variants in `packaging/chatgpt/skills/`. Update both versions when changing a shared workflow in an overridden file. Other archives retain canonical skill files.

`plugin.json` supplies public package metadata. The builder adds the package name from `packaging/directory-listings.json` and the shared version. The MCP declaration, legal URLs, icon and package paths are checked for compatibility.

The ChatGPT variants cover contract workflows without product purchasing or standalone Parser instructions. Validation scans all archive contents. It allows only the exact contract-related uses of `billing rhythm` and `SaaS subscriptions` in the relevant workflow references. Extraction headings and links use “What extraction gives you automatically”.

Use the [ChatGPT installation instructions](../../README.md#install) to connect a workspace. See [package maintenance](../../DISTRIBUTION.md) for versioning and release downloads.
