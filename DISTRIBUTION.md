# Package maintenance

## Versioning

`packaging/manifest.json` holds the version shared by the plugin, extension, MCP Registry and npm packages. Copy version changes to the client manifests and the npm lockfile's root package fields, then regenerate the directory package:

```bash
python3 scripts/build_release_artifacts.py --write-directory
python3 scripts/check_versions.py --tag vX.Y.Z
python3 scripts/build_release_artifacts.py --check-directory
```

Dependency and protocol versions are separate. Add user-visible changes to [CHANGELOG.md](CHANGELOG.md).

## Build and release

`skills/` is canonical. The builder generates `packages/agent-plugin/` and release ZIPs from that tree and `packaging/manifest.json`. Do not edit generated files directly. The ChatGPT archive uses its [manifest and skill variants](packaging/chatgpt/README.md); other archives retain the canonical skill files.

Build release archives with `bash build-zips.sh`. Archive paths and timestamps are fixed. The generic Agent Plugins archive records the source commit; the ChatGPT archive does not. Identical source files and configuration produce identical archives.

[Release CI](.github/workflows/release.yml) checks the version against the `vX.Y.Z` tag, builds from the tagged commit and attaches `dist/*.zip` to the GitHub release. It stages `@contracko/mcp` on npm using trusted publishing; a maintainer completes publication with `npm stage approve` and two-factor authentication.

## Public installation links

- [Claude connector](https://claude.ai/directory/connectors/contracko)
- [Claude Code installation](README.md#install)
- [ChatGPT](https://chatgpt.com/plugins/plugin_asdk_app_6ac8e9b10f548191ab1ed190c3b0ccab)
- [Cursor Marketplace](https://cursor.com/marketplace/contracko)
- [Codex, Copilot, Gemini CLI, Cline and other clients](README.md#install)
- [OpenClaw setup](packaging/openclaw/README.md) and [Hermes setup](packaging/hermes/README.md)
- [npm launcher for stdio clients](https://www.npmjs.com/package/@contracko/mcp)
- [Copyable setup prompt](https://contracko.com/mcp/install/prompt.md)
- [Release downloads](https://github.com/contracko/contracko-skills/releases/latest)

For Claude chat, download `contracko.zip` from the release, not GitHub's source ZIP. `contracko-chat.zip` is a byte-identical compatibility alias. Client connection, consent, update and safety instructions remain in [README.md](README.md#install).
