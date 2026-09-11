#!/usr/bin/env python3
"""Checks for generated OpenClaw and Hermes release bundles."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("contracko", "contracko-create", "contracko-import", "contracko-review")
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


class ReleaseArtifactTests(unittest.TestCase):
    def build(self, output: Path, version: str = "1.2.3") -> None:
        subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/build_release_artifacts.py"),
                "--output",
                str(output),
                "--version",
                version,
                "--source-commit",
                "0123456789abcdef0123456789abcdef01234567",
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
                    self.assertEqual(manifest["version"], "1.2.3")
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
                    self.assertEqual(metadata["version"], "1.2.3")
                    self.assertEqual(metadata["skills"], list(SKILLS))

                    for skill in SKILLS:
                        for path in (ROOT / "skills" / skill).rglob("*"):
                            if path.is_file():
                                archive_name = f"skills/{skill}/{path.relative_to(ROOT / 'skills' / skill).as_posix()}"
                                self.assertEqual(archive.read(archive_name), path.read_bytes())

    def test_canonical_skills_use_approved_product_vocabulary(self) -> None:
        expected_lines = {
            "skills/contracko/SKILL.md": (
                "| `parser:compute` | document-processing tools |",
                "| `contract:write` | contract and folder changes, import and ingest, documents, comments, events, notifications, types, and parties |",
                "| notice dates, notifications, comparisons, risk, priorities, or gaps | [contracko-review](../contracko-review/SKILL.md) |",
                "| extraction without a managed contract | document-processing tools in [references/tool-index.md](references/tool-index.md) |",
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
                "Requires `contract:read`. Compare, audit and report stay read-only. Setting notifications needs `contract:write`. Where the tools are missing from your tool list, the credential is narrower than the user thinks: see [contracko](../contracko/SKILL.md), which also covers connecting and reading Contracko's errors.",
                "## Events and notifications",
                "A notification hangs off an event. List first: `clm_list_contract_events`.",
                "**System events** (`notice`, `end`, `open_ended_review`) already exist. You do not create them. Renewal alerts target `end`. Attach a notification with `clm_create_event_reminders`, `anchorType: \"system\"`, and that `systemType`.",
                "**Custom events** (a review meeting, an option window, an insurance expiry) are created with `clm_create_contract_events`: `title`, `date` as `YYYY-MM-DD`, optional recurrence (`recurrenceInterval` and `recurrenceUnit` together), optional nested `reminders` (max 25 per event). Batches are max 100 events or notifications, each item independent.",
                "A notification needs `offsetValue`, `offsetUnit` (`days` | `weeks` | `months` | `quarters` | `years`), `offsetDirection` (`before` | `on` | `after`), and `recipient` (`{ \"type\": \"contract_owner\" }` or `{ \"type\": \"user\", \"userId\" }`). `on` requires `offsetValue: 0`. Optional `message`.",
                "Mutations need `idempotencyKey` (8–128 characters). Update and delete need `expectedUpdatedAt` as a UTC timestamp ending in `Z`. Changing notifications on a custom event advances that event's version: relist before you replace its notification set. Deleting an event deletes its notifications; deleting a notification leaves the event.",
                "**Two files not in Contracko.** Import them (or use document processing if the user does not want them filed), then compare. A vendor A/B belongs as two contracts, not one.",
            ),
            "skills/contracko/references/tool-index.md": (
                "## Events, notifications, and document processing",
                "Events and notifications need `contract:read` to list and `contract:write` to change. List before a change, use the latest `expectedUpdatedAt` for updates or deletes, and confirm a bulk write. Renewal notifications attach to the existing `end` system event.",
                "| `clm_list_contract_events` | `contract:read` | List custom and supported system events with notifications. |",
                "| `clm_create_event_reminders`, `clm_update_event_reminders`, `clm_delete_event_reminders` | `contract:write` | Manage notifications on events. |",
                "Document-processing jobs spend credits. Preflight before creating one, and retrieve exports before their retention window ends.",
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
                '"version": "0.7.2",',
                '"description": "Agent skills for Contracko contract management over MCP: connect and verify the server, organise the workspace, import contracts, set notifications, create and file new agreements, and answer renewal, risk and vendor questions.",',
            ),
            ".codex-plugin/plugin.json": (
                '"version": "0.7.1",',
                '"description": "Agent skills for Contracko contract management over MCP: connect and verify the server, organise the workspace, import contracts, set notifications, create and file new agreements, and answer renewal, risk and vendor questions.",',
            ),
        }

        for relative, lines in expected_lines.items():
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text()
                for line in lines:
                    self.assertIn(line, text)

        claude_plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        claude_marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(claude_plugin["version"], "0.7.2")
        self.assertEqual(claude_marketplace["metadata"]["version"], claude_plugin["version"])

    def test_committed_directory_package_exposes_canonical_skills(self) -> None:
        package = ROOT / "packages" / "agent-plugin"
        self.assertTrue((package / "plugin.json").is_file())
        self.assertTrue((package / "README.md").is_file())
        self.assertTrue((package / "LICENSE").is_file())
        self.assertTrue((package / "NOTICE.md").is_file())
        self.assertNotIn("mcp.json", {path.name for path in package.rglob("*")})
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

    def test_release_build_accepts_prerelease_and_build_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist"
            self.build(output, version="1.2.3-rc.1+build.5")
            with zipfile.ZipFile(output / "contracko-openclaw.zip") as archive:
                manifest = json.loads(archive.read("plugin.json"))
            self.assertEqual(manifest["version"], "1.2.3-rc.1+build.5")

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
                self.assertNotIn("Authorization: Bearer", readme)

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
