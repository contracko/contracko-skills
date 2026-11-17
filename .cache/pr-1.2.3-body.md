## Summary

Supersedes #49. Rebased onto `main` after #48's squash merge (`eb082c21f4b3be1a7c8030f9e9675258cba5c6ac`, released as v1.2.2), then bumped the unified public version to 1.2.3 and regenerated the directory package. A new branch preserves #49's original history without a force-push.

- **Developer name:** `author.name` and `interface.developerName` change from Budi Voogt to Contracko. The OpenAI org has business verification approved.
- **Listing copy:** the subtitle becomes "AI contract management (CLM)". This is the 28-character fallback from #49, replacing its 32-character subtitle to satisfy OpenAI's documented 30-character public-submission limit. The identical description and long description lead with AI contract lifecycle management (CLM), a searchable contract repository, AI contract review and analysis, and renewal and expiration reminders.
- **Search fields:** adds top-level `keywords` (CLM, contract lifecycle management, contract management software, contract repository, contract reminder software, renewal reminders, expiration tracking, AI contract review, AI contract analysis, contract data extraction) and four `interface.capabilities` entries.
- **Release preparation:** aligns every public manifest, the npm lockfile root and both MCP Registry version fields at 1.2.3; updates the ChatGPT package notes and records the 1.2.2 and 1.2.3 changelog sections without duplicating entries.

The search rationale from #49 is unchanged: the published listing does not appear in ChatGPT plugin search for "CLM". Tomorro is the only result for "contract lifecycle management". Contracko comes 7th of 7 for "contract management" and does not appear for "contract" or "contracts". The wording follows Contracko's Google Search Console queries over the last 90 days and 16 months, where contract management software, renewal and reminder, repository and CLM searches carry the most demand.

## How can this be tested?

- `tests/test_release_artifacts.py` still pins the connection identity against the accepted 1.1.0 baseline: name, skills path, MCP declaration, category, prompts, legal URLs, brand color, logo and icon. Listing copy fields (`author`, `description`, `developerName`, `longDescription`, `shortDescription`, `capabilities`) may differ. Assertions check the Contracko developer name, identical description and long description, a CLM keyword, and a subtitle of at most 30 characters. `keywords` joins the allowed top-level key set.
- The existing archive-wide commerce-safe scan continues to cover the listing copy and release notes without new exceptions. Skills and review cases are unchanged.
- Passed local static checks: `python3 -m py_compile tests/test_release_artifacts.py`, `python3 scripts/check_versions.py --tag v1.2.3`, `python3 scripts/build_release_artifacts.py --check-directory`, prose policy, `git diff --check`, and a redacted Gitleaks scan of the PR commits.
- Hosted `validate` CI runs `python3 -m unittest discover -s tests -v` and `bash build-zips.sh`, including archive identity, commerce scanning and reproducibility checks. These suites and builds were not run locally under the shared static-only validation policy.

## Additional context

This PR prepares the package only. It does not merge, tag, release, or upload to the developer portal. The existing CI candidate-ZIP artifact upload is unchanged.

### Notes and risks for the uploader

- Upload only after approval. Use "Create draft from ZIP" on `plugin_asdk_app_6ac8e9b10f548191ab1ed190c3b0ccab`, with version `1.2.3`, then check the draft's Developer field before submitting.
- OpenAI support says the developer name must match the verified organisation name exactly. If the reviewer rejects "Contracko" (legal entity: Velocity Ventures B.V., trading as Contracko), revert these two fields.
- OpenAI distinguishes draft-upload acceptance from public-submission metadata limits. The selected subtitle is already within the 30-character submission limit; a successful draft upload alone is not submission proof.
