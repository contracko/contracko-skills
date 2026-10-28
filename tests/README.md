# Validate the skills

Run from the repository root (Python 3.10+ and `zip`; no Python dependencies):

```bash
python3 -m unittest discover -s tests -v
```

The checks verify unified public versions and release tags, tool names across skill Markdown, annotated MCP examples, selected obsolete
claims, and links inside the single-skill ZIP and its chat compatibility alias. Example arguments are checked against the pinned input
schemas, including types, enums, bounds, string patterns, nullable branches, and date windows. This
is a targeted documentation check, not a general JSON Schema validator or a live MCP integration test.
The release tests also build the OpenClaw and Hermes bundles from the canonical skill directories,
check the Agent Plugins v1 manifest boundary, compare skill bytes, and verify reproducibility. They
do not install or run OpenClaw or Hermes. Package layouts, regeneration and version checks: [DISTRIBUTION.md](../DISTRIBUTION.md). Tests compare package bytes, deterministic output and source metadata without installing clients.

Mark executable examples with `json mcp:<tool-name>` on the opening code fence. Values must be
syntactically valid examples, not placeholders. Explain nearby that real IDs come from discovery and
dates come from the user's requested window.

## Refresh the release baseline

`fixtures/mcp-contract.json` contains released tool names, capability versions, annotations, effects, and the input schemas
needed to validate the documented examples. Its revision is an opaque catalog version label. It contains no user data.

When the released tools change, update this fixture and the skills together. Validate the documented examples with:

```bash
python3 scripts/check_contracts.py
```

CI uses the committed baseline without network access. Use live `tools/list` for each actual credential; the pinned maximum
surface is not an entitlement.

Review [workflow-cases.md](workflow-cases.md) for behavioral acceptance cases. Record the model,
bundle revision, and observed tool calls if running them with an agent. Automated checks do not
substitute for those model evaluations.
