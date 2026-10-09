#!/usr/bin/env python3
"""Checks for generated OpenClaw and Hermes release bundles."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("contracko", "contracko-create", "contracko-import", "contracko-review")
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
CLAUDE_DIRECTORY_URL = "https://claude.ai/directory/connectors/contracko"
VERSION = json.loads((ROOT / "packaging/manifest.json").read_text())["version"]


class ReleaseArtifactTests(unittest.TestCase):
    def build(
        self, output: Path, version: str = VERSION,
        source_commit: str = "0123456789abcdef0123456789abcdef01234567",
    ) -> None:
        subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/build_release_artifacts.py"),
                "--output",
                str(output),
                "--version",
                version,
                "--source-commit",
                source_commit,
            ],
            check=True,
            cwd=ROOT,
        )

    def test_platform_bundles_are_generated_from_canonical_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist"
            self.build(output)

            expected_skill_files = {
                f"skills/{skill}/{path.relative_to(ROOT / 'skills' / skill).as_posix()}"
                for skill in SKILLS
                for path in (ROOT / "skills" / skill).rglob("*")
                if path.is_file()
            }

            for platform in ("openclaw", "hermes"):
                archive_path = output / f"contracko-{platform}.zip"
                self.assertTrue(archive_path.is_file())
                with zipfile.ZipFile(archive_path) as archive:
                    names = set(archive.namelist())
                    self.assertTrue(expected_skill_files <= names)
                    self.assertIn("plugin.json", names)
                    self.assertIn("README.md", names)
                    self.assertIn("LICENSE", names)
                    self.assertIn("NOTICE.md", names)
                    self.assertIn("RELEASE-METADATA.json", names)
                    self.assertNotIn("mcp.json", names)
                    self.assertNotIn(".mcp.json", names)

                    manifest = json.loads(archive.read("plugin.json"))
                    self.assertEqual(manifest["$schema"], PLUGIN_SCHEMA)
                    self.assertEqual(manifest["name"], "contracko")
                    self.assertEqual(manifest["version"], VERSION)
                    self.assertEqual(
                        set(manifest),
                        {
                            "$schema",
                            "name",
                            "version",
                            "description",
                            "author",
                            "homepage",
                            "repository",
                            "license",
                            "keywords",
                        },
                    )

                    metadata = json.loads(archive.read("RELEASE-METADATA.json"))
                    self.assertEqual(metadata["platform"], platform)
                    self.assertEqual(
                        metadata["source_commit"],
                        "0123456789abcdef0123456789abcdef01234567",
                    )
                    self.assertEqual(metadata["version"], VERSION)
                    self.assertEqual(metadata["skills"], list(SKILLS))

                    for skill in SKILLS:
                        for path in (ROOT / "skills" / skill).rglob("*"):
                            if path.is_file():
                                archive_name = f"skills/{skill}/{path.relative_to(ROOT / 'skills' / skill).as_posix()}"
                                self.assertEqual(archive.read(archive_name), path.read_bytes())

    def test_canonical_skills_use_approved_product_vocabulary(self) -> None:
        expected_lines = {
            "skills/contracko/SKILL.md": (
                "| `parser:compute` | separate Contracko Parser bulk processing using Parser credits, not contract intake |",
                "| `contract:write` | contract and folder changes, import and ingest, documents, comments, events, notifications, types, and parties |",
                "| notice dates, notifications, comparisons, risk, priorities, or gaps | [contracko-review](../contracko-review/SKILL.md) |",
                "| standalone bulk extraction without a managed contract | Contracko Parser, using Parser credits, in [references/tool-index.md](references/tool-index.md) |",
                "### Notifications and registers",
                "A notification hangs from a contract event. [contracko-review](../contracko-review/SKILL.md) owns date queries and notification writes. Renewal notifications use the existing `end` system event.",
                "SaaS subscriptions, leases, permits, certificates, insurance policies, warranties, and domains use the same pattern: a type, countable fields, native renewal dates, and a notification. Use supported filters first, then complete the required pages before local filtering.",
            ),
            "skills/contracko-create/SKILL.md": (
                "6. **Set the notification** that will matter in a year — [contracko-review](../contracko-review/SKILL.md).",
                "## Step 6: the notification",
                "A filed contract with no notification is a renewal nobody sees coming. After import, list events, then add a notification on the `end` system event (renewal) or `notice` if they care about the notice window. [contracko-review](../contracko-review/SKILL.md) has the calls. Prefer notice over end when both exist and they asked not to miss the window to get out.",
            ),
            "skills/contracko-review/SKILL.md": (
                "description: Reviews Contracko contracts. Use for notice dates, end dates, annual review, notifications (reminders), risk audits, comparing proposals or redlines, or portfolio priorities and gaps.",
                "Requires `contract:read`. Compare, audit and report can use read-only tools. Reprocess and reconciliation `get` helpers change saved state despite that scope; explain the change and get approval, or use the list-only view. Setting notifications needs `contract:write`. Where the tools are missing from your tool list, the credential is narrower than the user thinks: see [contracko](../contracko/SKILL.md), which also covers connecting and reading Contracko's errors.",
                "## Events and notifications",
                "A notification hangs off an event. List first: `clm_list_contract_events`.",
                "**System events** (`notice`, `end`, `open_ended_review`) already exist. You do not create them. Renewal alerts target `end`. Attach a notification with `clm_create_event_reminders`, `anchorType: \"system\"`, and that `systemType`.",
                "**Custom events** (a review meeting, an option window, an insurance expiry) are created with `clm_create_contract_events`: `title`, `date` as `YYYY-MM-DD`, optional recurrence (`recurrenceInterval` and `recurrenceUnit` together), optional nested `reminders` (max 25 per event). Batches are max 100 events or notifications, each item independent.",
                "A notification needs `offsetValue`, `offsetUnit` (`days` | `weeks` | `months` | `quarters` | `years`), `offsetDirection` (`before` | `on` | `after`), and `recipient` (`{ \"type\": \"contract_owner\" }` or `{ \"type\": \"user\", \"userId\" }`). `on` requires `offsetValue: 0`. Optional `message`.",
                "Mutations need `idempotencyKey` (8–128 characters). Update and delete need `expectedUpdatedAt` as a UTC timestamp ending in `Z`. Changing notifications on a custom event advances that event's version: relist before you replace its notification set. Deleting an event deletes its notifications; deleting a notification leaves the event.",
                "**Two files not in Contracko.** Import them with CLM without Parser credits, then compare. If the user explicitly wants standalone bulk processing instead of filing, Contracko Parser uses Parser credits. A vendor A/B belongs as two contracts, not one.",
            ),
            "skills/contracko/references/tool-index.md": (
                "## CLM events and notifications",
                "Events and notifications need `contract:read` to list and `contract:write` to change. List before a change, use the latest `expectedUpdatedAt` for updates or deletes, and confirm a bulk write. Renewal notifications attach to the existing `end` system event.",
                "| `clm_list_contract_events` | `contract:read` | List custom and supported system events with notifications. |",
                "| `clm_create_event_reminders`, `clm_update_event_reminders`, `clm_delete_event_reminders` | `contract:write` | Manage notifications on events. |",
                "Preflight before starting a Parser job, confirm the estimated Parser credit cost, and retrieve exports before their retention window ends. Parser credit refusals affect this product, not CLM contract intake.",
            ),
            "skills/contracko/references/workflows.md": (
                "Get today's date from the environment. Use inclusive end-date or notice-date filters for dated candidates and complete every returned page. `autoRenewing` identifies a renewal; a date window alone does not. For contracts ending OR needing notice, run separate complete queries and deduplicate by contract ID. Use existing system events for renewal or notice notifications. [contracko-review](../../contracko-review/SKILL.md) owns the calendar.",
                "**Done when:** the user has the urgent bucket, its dates, and any requested notification confirmed as created.",
                "**They say:** notice dates, end dates, renewals, annual review, reminders, notifications.",
            ),
            "README.md": (
                "| I do not want silent renewals. What needs notice, ends, or auto-renews in the next quarter? Set reminders for all of it. | Lists the dates that matter today, then creates notifications on those contracts so you are notified in time. |",
                "| [contracko-review](skills/contracko-review/SKILL.md) | Notice dates, notifications, comparisons, risk language, and what to look at next |",
            ),
            ".claude-plugin/plugin.json": (
                '"description": "CLM: add, import, review and manage contracts without Parser credits. Separate Contracko Parser: bulk document processing using Parser credits, not needed to add contracts.",',
            ),
            ".codex-plugin/plugin.json": (
                '"description": "CLM: add, import, review and manage contracts without Parser credits. Separate Contracko Parser: bulk document processing using Parser credits, not needed to add contracts.",',
            ),
        }

        for relative, lines in expected_lines.items():
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text()
                for line in lines:
                    self.assertIn(line, text)

        claude_plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        claude_marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(claude_plugin["version"], VERSION)
        self.assertEqual(claude_marketplace["metadata"]["version"], claude_plugin["version"])

    def test_claude_connect_copy_is_directory_first(self) -> None:
        sources = {
            "README.md": (ROOT / "README.md").read_text(),
            "skills/contracko/SKILL.md": (ROOT / "skills/contracko/SKILL.md").read_text(),
        }
        for relative, text in sources.items():
            with self.subTest(path=relative):
                self.assertIn(CLAUDE_DIRECTORY_URL, text)
                self.assertIn("contracko@contracko", text)
                self.assertNotIn("contracko-skills@contracko", text)
                plugin_install = text.index("/plugin install contracko@contracko")
                mcp_add = text.index("claude mcp add")
                self.assertGreater(mcp_add, plugin_install)
                between = text[plugin_install:mcp_add]
                self.assertIn("without the plugin", between)
                self.assertIn("claude mcp list", text[mcp_add - 400 : mcp_add + 400])

        readme = sources["README.md"]
        claude_section = readme[readme.index("<summary><strong>Claude</strong>") :]
        claude_section = claude_section[: claude_section.index("</details>")]
        first_step = claude_section[claude_section.index("1. ") :].splitlines()[0]
        self.assertIn(CLAUDE_DIRECTORY_URL, first_step)
        self.assertIn("custom connector", claude_section)
        self.assertNotIn("Add custom connector", claude_section)
        self.assertIn("https://app.contracko.com/mcp", readme[readme.index("<summary><strong>Codex</strong>") :])

    def test_skills_cover_tool_search_and_full_catalog(self) -> None:
        catalog = json.loads((ROOT / "tests/fixtures/mcp-contract.json").read_text())
        names = {tool["name"] for tool in catalog["tools"]}
        self.assertEqual(len(names), 52)
        index = (ROOT / "skills/contracko/references/tool-index.md").read_text()
        self.assertIn("all 52 tools", index)
        self.assertEqual({name for name in names if f"`{name}`" not in index}, set())

        skill = (ROOT / "skills/contracko/SKILL.md").read_text()
        when_to_use = skill[skill.index("## Find the right tool") :]
        when_to_use = when_to_use[: when_to_use.index("\n## ", 1)]
        for trigger in ("unsure which tool", "multi-step job", "first contract"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, when_to_use)

        workflows = (ROOT / "skills/contracko/references/workflows.md").read_text()
        first = workflows[workflows.index("## Add your first contract") :]
        first = first[: first.index("\n## ", 1)]
        steps = [first.index(tool) for tool in ("clm_create_upload_url", "PUT", "clm_ingest_contract", "clm_get_contract`")]
        self.assertEqual(steps, sorted(steps))

    def test_connect_copy_has_no_workspace_choice(self) -> None:
        paths = [ROOT / "README.md", ROOT / "GEMINI.md", ROOT / "llms-install.md", ROOT / "agent-setup/prompt.md"]
        paths += sorted((ROOT / "skills").rglob("*.md")) + sorted((ROOT / "packaging").rglob("*.md"))
        for path in paths:
            text = path.read_text().lower()
            for phrase in ("choose a workspace", "select the workspace", "workspace selection", "workspace picker"):
                with self.subTest(path=path.relative_to(ROOT).as_posix(), phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_client_manifests_mirror_claude_plugin_version(self) -> None:
        expected = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["version"]
        versions = {
            ".codex-plugin/plugin.json": json.loads((ROOT / ".codex-plugin/plugin.json").read_text())["version"],
            ".cursor-plugin/plugin.json": json.loads((ROOT / ".cursor-plugin/plugin.json").read_text())["version"],
            "gemini-extension.json": json.loads((ROOT / "gemini-extension.json").read_text())["version"],
            "server.json": json.loads((ROOT / "server.json").read_text())["version"],
        }
        github_marketplace = json.loads((ROOT / ".github/plugin/marketplace.json").read_text())
        for plugin in github_marketplace["plugins"]:
            versions[f".github/plugin/marketplace.json:{plugin['name']}"] = plugin["version"]
        for relative, version in versions.items():
            with self.subTest(path=relative):
                self.assertEqual(version, expected)

    def test_client_manifests_mirror_claude_plugin_description_except_cursor(self) -> None:
        # Cursor's marketplace truncates long descriptions, so Cursor carries its own shorter one.
        # server.json keeps its own MCP Registry description and is not checked here.
        expected = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["description"]
        descriptions = {
            ".codex-plugin/plugin.json": json.loads((ROOT / ".codex-plugin/plugin.json").read_text())["description"],
            "gemini-extension.json": json.loads((ROOT / "gemini-extension.json").read_text())["description"],
        }
        for relative in (".claude-plugin/marketplace.json", ".github/plugin/marketplace.json"):
            marketplace = json.loads((ROOT / relative).read_text())
            for plugin in marketplace["plugins"]:
                descriptions[f"{relative}:{plugin['name']}"] = plugin["description"]
        for relative, description in descriptions.items():
            with self.subTest(path=relative):
                self.assertEqual(description, expected)

        cursor = json.loads((ROOT / ".cursor-plugin/plugin.json").read_text())["description"]
        self.assertEqual(
            cursor,
            "CLM manages contracts without Parser credits. Separate Parser bulk processing uses credits, "
            "not needed to add contracts.",
        )
        self.assertLess(len(cursor), len(expected))

    def test_committed_directory_package_exposes_canonical_skills(self) -> None:
        package = ROOT / "packages" / "agent-plugin"
        self.assertTrue((package / "plugin.json").is_file())
        self.assertTrue((package / "README.md").is_file())
        self.assertTrue((package / "LICENSE").is_file())
        self.assertTrue((package / "NOTICE.md").is_file())
        descriptor = json.loads((package / "mcp.json").read_text())
        self.assertEqual(descriptor["$schema"], MCP_SCHEMA)
        self.assertEqual(descriptor["mcpServers"]["contracko"]["type"], "streamable-http")
        self.assertEqual(descriptor["mcpServers"]["contracko"]["url"], "https://app.contracko.com/mcp")
        self.assertNotIn(".mcp.json", {path.name for path in package.rglob("*")})

        manifest = json.loads((package / "plugin.json").read_text())
        self.assertEqual(manifest["$schema"], PLUGIN_SCHEMA)
        self.assertEqual(manifest["name"], "contracko")
        self.assertNotIn("{{VERSION}}", manifest["version"])
        self.assertEqual(
            set(manifest),
            {
                "$schema",
                "name",
                "version",
                "description",
                "author",
                "homepage",
                "repository",
                "license",
                "keywords",
            },
        )

        for skill in SKILLS:
            source = ROOT / "skills" / skill
            generated = package / "skills" / skill
            self.assertTrue((generated / "SKILL.md").is_file())
            for path in source.rglob("*"):
                if path.is_file():
                    relative = path.relative_to(source)
                    self.assertEqual((generated / relative).read_bytes(), path.read_bytes())

    def test_committed_directory_package_passes_generator_drift_check(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/build_release_artifacts.py"),
                "--check-directory",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_directory_check_rejects_skill_tree_drift_without_writing(self) -> None:
        cases = (
            ("skills/new-skill/SKILL.md", b"New canonical skill\n"),
            ("skills/shared.txt", b"Canonical asset\n"),
            ("skills/contracko/SKILL.md", b"Changed canonical skill\n"),
            ("packages/agent-plugin/skills/contracko/SKILL.md", b"Changed package\n"),
            ("packages/agent-plugin/skills/contracko/SKILL.md", None),
            ("packages/agent-plugin/skills/extra/asset.bin", b"\x00\xff"),
            ("packages/agent-plugin/mcp.json", (ROOT / "mcp.json").read_bytes()),
            ("mcp.json", b'{"mcpServers":{"contracko":{"type":"http","url":"https://example.com/mcp"}}}'),
        )
        for relative, content in cases:
            with self.subTest(path=relative, content=content):
                with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
                    fixture = Path(temporary)
                    for directory in ("scripts", "skills", "packaging", "packages/agent-plugin"):
                        shutil.copytree(ROOT / directory, fixture / directory)
                    shutil.copyfile(ROOT / "LICENSE", fixture / "LICENSE")
                    shutil.copyfile(ROOT / "mcp.json", fixture / "mcp.json")
                    target = fixture / relative
                    if content is None:
                        target.unlink()
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(content)
                    before = {
                        path.relative_to(fixture): path.read_bytes()
                        for path in fixture.rglob("*") if path.is_file()
                    }
                    result = subprocess.run(
                        ["python3", str(fixture / "scripts/build_release_artifacts.py"), "--check-directory"],
                        cwd=fixture, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("drift", result.stderr)
                    after = {
                        path.relative_to(fixture): path.read_bytes()
                        for path in fixture.rglob("*") if path.is_file()
                    }
                    self.assertEqual(after, before)

    def test_directory_check_rejects_release_version_mismatch(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/build_release_artifacts.py"),
                "--check-directory",
                "--version",
                "9.9.9",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match requested release version", result.stderr)

    def test_release_wrapper_rejects_version_mismatch(self) -> None:
        environment = os.environ.copy()
        environment.update(
            {
                "VERSION": "9.9.9",
                "SOURCE_COMMIT": "0123456789abcdef0123456789abcdef01234567",
            }
        )
        result = subprocess.run(
            ["bash", str(ROOT / "build-zips.sh")],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match requested release version", result.stderr)

    def test_directory_check_rejects_symlinked_entries(self) -> None:
        package_file = ROOT / "packages/agent-plugin/skills/contracko/SKILL.md"
        original = package_file.read_bytes()
        result = None
        try:
            package_file.unlink()
            package_file.symlink_to(ROOT / "skills/contracko/SKILL.md")
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/build_release_artifacts.py"),
                    "--check-directory",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        finally:
            if package_file.is_symlink():
                package_file.unlink()
            package_file.write_bytes(original)

        self.assertIsNotNone(result)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contains symlink", result.stderr)

    def test_platform_archives_are_reproducible_for_same_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            self.build(first)
            self.build(second)
            for platform in ("openclaw", "hermes"):
                self.assertEqual(
                    (first / f"contracko-{platform}.zip").read_bytes(),
                    (second / f"contracko-{platform}.zip").read_bytes(),
                )

    def test_release_build_rejects_unpinned_source_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/build_release_artifacts.py"),
                    "--output",
                    str(Path(temporary) / "dist"),
                    "--source-commit",
                    "working-tree",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("full 40-character commit SHA", result.stderr)

    def test_release_build_rejects_different_prerelease_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist"
            result = subprocess.run(
                ["python3", str(ROOT / "scripts/build_release_artifacts.py"),
                 "--output", str(output), "--version", "1.2.3-rc.1+build.5"],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not match requested release version", result.stderr)
            self.assertFalse(output.exists())

    def test_chatgpt_submission_archive_matches_directory_package_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            self.build(first)
            self.build(second)
            first_zip = first / "contracko-agent-plugin.zip"
            self.assertEqual(first_zip.read_bytes(), (second / first_zip.name).read_bytes())
            package = ROOT / "packages/agent-plugin"
            expected = {
                path.relative_to(package).as_posix(): path.read_bytes()
                for path in package.rglob("*") if path.is_file()
            }
            with zipfile.ZipFile(first_zip) as archive:
                self.assertEqual(set(archive.namelist()), set(expected) | {"RELEASE-METADATA.json"})
                for name, content in expected.items():
                    self.assertEqual(archive.read(name), content)
                self.assertEqual(json.loads(archive.read("plugin.json"))["version"], VERSION)
                self.assertIn("mcp.json", archive.namelist())
                descriptor = json.loads(archive.read("mcp.json"))
                self.assertEqual(descriptor["$schema"], MCP_SCHEMA)
                self.assertEqual(descriptor["mcpServers"]["contracko"]["type"], "streamable-http")
                self.assertEqual(descriptor["mcpServers"]["contracko"]["url"], "https://app.contracko.com/mcp")
                metadata = json.loads(archive.read("RELEASE-METADATA.json"))
                self.assertEqual(metadata["version"], VERSION)
                self.assertEqual(metadata["source_commit"], "0123456789abcdef0123456789abcdef01234567")
            third = Path(temporary) / "third"
            self.build(third, source_commit="abcdef0123456789abcdef0123456789abcdef01")
            self.assertNotEqual(first_zip.read_bytes(), (third / first_zip.name).read_bytes())

    def test_release_build_rejects_repository_output_paths(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/build_release_artifacts.py"),
                "--output",
                str(ROOT),
                "--source-commit",
                "0123456789abcdef0123456789abcdef01234567",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--output", result.stderr)
        self.assertIn("repository", result.stderr)

    def test_release_build_rejects_symlinked_source_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist-link"
            output.symlink_to(ROOT / "scripts", target_is_directory=True)
            result = subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts/build_release_artifacts.py"),
                    "--output",
                    str(output),
                    "--source-commit",
                    "0123456789abcdef0123456789abcdef01234567",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("inside repository dist/", result.stderr)

    def test_setup_guidance_keeps_registration_and_consent_host_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist"
            self.build(output)
            openclaw = zipfile.ZipFile(output / "contracko-openclaw.zip")
            hermes = zipfile.ZipFile(output / "contracko-hermes.zip")
            try:
                openclaw_readme = openclaw.read("README.md").decode()
                hermes_readme = hermes.read("README.md").decode()
            finally:
                openclaw.close()
                hermes.close()

            for readme in (openclaw_readme, hermes_readme):
                self.assertIn("https://app.contracko.com/mcp", readme)
                self.assertIn("explicit", readme.lower())
                self.assertIn("browser", readme.lower())
                self.assertIn("Read", readme)
                self.assertIn("Write", readme)
                self.assertNotIn("mcp.contracko.com", readme)
                # Built at runtime so this negative check is not itself flagged as a credential.
                self.assertNotIn("Authorization: " + "Bearer", readme)

            self.assertIn("openclaw mcp login contracko", openclaw_readme)
            self.assertIn("hermes mcp login contracko", hermes_readme)

    def test_create_handoff_requires_destination_and_consent(self) -> None:
        text = (ROOT / "skills/contracko-create/SKILL.md").read_text()
        lowered = text.lower()
        self.assertIn("choose a destination", lowered)
        self.assertIn("explicit consent", lowered)
        self.assertIn("do not write", lowered)
        self.assertIn("if the user does not choose", lowered)
        self.assertNotIn("the handoff, and it is not optional", lowered)


if __name__ == "__main__":
    unittest.main()
