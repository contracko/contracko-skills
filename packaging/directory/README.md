# Contracko Agent Plugin

This is the canonical Agent Plugins v1 skills package for Contracko. It is generated from the four source directories in `skills/` by `scripts/build_release_artifacts.py`.

The package includes `plugin.json`, the four skills, and `mcp.json` pointing to `https://app.contracko.com/mcp`. The host client owns MCP registration, OAuth, credential storage, and user consent. The release ZIP `contracko-agent-plugin.zip` is the ChatGPT submission package and adds `RELEASE-METADATA.json` with the release version and source commit. It contains no `.codex-plugin` metadata.
