# Validate the skills

Run from the repository root (Python 3.10+ and `zip`; no Python dependencies):

```bash
python3 -m unittest discover -s tests -v
```

The checks verify tool names across skill Markdown, annotated MCP examples, selected obsolete
claims, and links inside the merged chat ZIP. Example arguments are checked against the pinned input
schemas, including types, enums, bounds, string patterns, nullable branches, and date windows. This
is a targeted documentation check, not a general JSON Schema validator or a live MCP integration test.

Mark executable examples with `json mcp:<tool-name>` on the opening code fence. Values must be
syntactically valid examples, not placeholders. Explain nearby that real IDs come from discovery and
dates come from the user's requested window.

## Refresh the release baseline

`fixtures/mcp-contract.json` contains released tool names, capability versions, and the input schemas
needed to validate the documented examples. Its revision pins the reviewed app release. It contains no user data.
When an app release changes MCP, export `docs/mcp-tool-catalog.json` from that exact release commit
in an authorized app checkout, then run:

```bash
python3 scripts/check_contracts.py --refresh /path/to/released-catalog.json --revision FULL_40_CHARACTER_COMMIT_SHA
python3 -m unittest discover -s tests -v
```

Review the fixture diff and update skills before publishing. CI intentionally uses the committed
baseline, without private-repository credentials or runtime network access. It cannot discover a
new app release automatically. Use live `tools/list` for each actual credential; the pinned maximum
surface is not an entitlement.

Review [workflow-cases.md](workflow-cases.md) for behavioral acceptance cases. Record the model,
bundle revision, and observed tool calls if running them with an agent. Automated checks do not
substitute for those model evaluations.
