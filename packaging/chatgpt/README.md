# ChatGPT package 1.2.1

Release notes: ChatGPT package: skills cover contract management only and give no plan or purchase guidance. Negative review cases now include a plan change request.

Version 1.2.1 is a distinct upload after the 1.2.0 draft failed the portal case-count requirement. All public versions remain aligned with `packaging/manifest.json`.

`skills/` holds complete ChatGPT variants of canonical files that contain product commerce or standalone processing instructions. The builder copies the canonical skill tree, then overlays only these files for `contracko-agent-plugin-chatgpt.zip`. Edit both versions when changing a shared workflow in an overridden file. Other archives continue to use canonical skill bytes.

ChatGPT calls the extraction section “What extraction gives you automatically” and uses matching anchors. The archive scan also rejects `free` as a whole word.

`plugin.json` embeds exactly five positive and three negative submission cases, as the portal requires. The negative cases cover deleting all contracts, contacting an external vendor to cancel an agreement, and changing the Contracko plan, in that order. The last case expects no plans, prices or purchase links. Cross-tenant isolation stays covered by our own MCP server tests rather than an imported portal review case. The default example-contract expectation no longer mentions a trial. Automated checks prove content and package behavior, not model execution of these cases.

The archive-wide case-insensitive scan permits these exact contract-vocabulary occurrences:

| File or JSON path | Kept occurrence | Meaning |
|---|---|---|
| `skills/contracko/references/new-agreement.md`, intake question | `billing rhythm` | Payment schedule of the user's agreement |
| Same file, handoff fields | `value/currency/billing rhythm` | Recorded terms of the user's agreement |
| `skills/contracko/references/organising-the-workspace.md`, register examples | `SaaS subscriptions` | Contract type managed by the user |
| `extensions.com.openai.review.test_cases.positive[1].expected_behavior` | `Forgeboard cloud subscription` | Seeded user's contract |
| `extensions.com.openai.review.test_cases.positive[4].description` | `Forgeboard subscription` | Seeded user's contract |
| `extensions.com.openai.review.test_cases.positive[4].prompt` | `Forgeboard cloud subscription` | Seeded user's contract |
| `extensions.com.openai.review.test_cases.positive[4].expected_behavior` | `Forgeboard subscription contract` | Seeded user's contract |
| `extensions.com.openai.review.test_cases.negative[1].description` | `vendor subscription` | External vendor agreement |
| `extensions.com.openai.review.test_cases.negative[1].prompt` | `Helion cloud subscription` | External vendor agreement |

The only additional exception is the exact value `Upgrade my plan` at `extensions.com.openai.review.test_cases.negative[2].prompt`. The scan compares whole values at these JSON paths and exact skill lines, not arbitrary substrings. Every other manifest field, skill, reference, asset and MCP declaration stays under the strict scan.

The accepted 1.1.0 ZIP is the compatibility baseline. Its identity is captured in `tests/fixtures/chatgpt-1.1.0-identity.json`; its icon is checked by SHA-256. The live listing is `plugin_asdk_app_6ac8e9b10f548191ab1ed190c3b0ccab`, with manifest name `contracko`. The retired listing's `app-...` naming rule does not apply.

| Identity field | Accepted 1.1.0 versus new package |
|---|---|
| `name`, `author`, `description`, `skills` | Identical |
| Complete `interface`, including legal URLs, logo and composer icon | Identical |
| `mcpServers` | Identical: `./.mcp.json` |
| `.mcp.json` | Identical bytes: key `contracko`, URL `https://app.contracko.com/mcp`, no explicit transport |
| `assets/icon.png` | Identical bytes |
| `version` | `1.1.0` to `1.2.1` |

The review cases and publication release notes change as described above. Other review metadata and country settings are preserved. This updates the same plugin and keeps its existing MCP connection.

Build with `bash build-zips.sh`. The PR's `ChatGPT package` CI job runs that command, uploads the ZIP as `contracko-chatgpt-plugin-<head SHA>`, and records its SHA-256 in the job summary. Download the ZIP from that exact candidate run. Upload only `contracko-agent-plugin-chatgpt.zip` to the live listing with version `1.2.1`, after approval to submit. Official release assets still come from the tagged release workflow.
