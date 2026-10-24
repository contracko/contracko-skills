# ChatGPT package 1.2.0

Release notes: Removes all pricing, trial, credit and subscription content for ChatGPT; adds a negative test for upgrade requests.

The public 1.2.0 candidate is newer than the rejected 1.1.0 submission. All public versions remain aligned with `packaging/manifest.json`.

`skills/` holds complete ChatGPT variants of canonical files that contain product commerce or standalone processing instructions. The builder copies the canonical skill tree, then overlays only these files for `contracko-agent-plugin-chatgpt.zip`. Edit both versions when changing a shared workflow in an overridden file. Other archives continue to use canonical skill bytes.

The archive-wide regression check permits only two exact lines, both in `skills/contracko/references/new-agreement.md`: the intake question about the user's contract's billing rhythm and the handoff fields that include that rhythm. These describe the user's agreement, not Contracko's offering.

`test-cases.json` keeps the five positive and three existing negative submission cases and adds the fourth negative case for an upgrade request. The default example-contract expectation no longer mentions a trial. The Forgeboard subscription wording describes the seeded user's contract. Review cases and these release notes are portal submission material, outside the ZIP, so a purchase-request test prompt does not become an agent instruction.

Build with `bash build-zips.sh`. Upload only `dist/contracko-agent-plugin-chatgpt.zip`, and use the unified version and the release notes above. Copy the review cases into the portal. Automated checks prove content and package behavior, not model execution of these cases.

Keep the existing listing mapping and MCP connection. The repository currently maps the ChatGPT package to `plugin_asdk_app_6a9e97994d248191b2dcb1714454bb2f`; the rejection brief names `plugin_asdk_app_6ac8e9b10f548191ab1ed190c3b0ccab`. Confirm the intended portal listing before uploading. This change does not rename the plugin or change its MCP declaration.
