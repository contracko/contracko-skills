#!/usr/bin/env python3
"""Checks for generated OpenClaw and Hermes release bundles."""

from __future__ import annotations

import json
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("contracko",)
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
                        manifest["keywords"],
                        json.loads((ROOT / "packaging/manifest.json").read_text())["keywords"],
                    )
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

    def test_single_skill_routes_every_workflow_reference(self) -> None:
        skill_root = ROOT / "skills" / "contracko"
        self.assertEqual({path.name for path in (ROOT / "skills").iterdir()}, {"contracko"})
        skill = (skill_root / "SKILL.md").read_text()
        references = {
            "onboarding.md", "importing-contracts.md", "notifications.md",
            "reviewing-ai-analysis.md", "portfolio-review.md",
            "organising-the-workspace.md", "new-agreement.md", "tool-index.md",
        }
        self.assertEqual({path.name for path in (skill_root / "references").iterdir()}, references)
        for name in references:
            self.assertIn(f"](references/{name})", skill)
        self.assertLess(len(skill.split()), 1000)
        description = skill.split("description: ", 1)[1].splitlines()[0].strip("'")
        self.assertLessEqual(len(description), 200)
        self.assertNotIn("/", description)
        self.assertNotIn(";", description)
        for trigger in ("import", "upload", "renewal", "notice", "reminders", "AI analysis",
                        "reports", "folders", "types", "draft new agreements", "Parser jobs"):
            self.assertIn(trigger, description)
        routing = skill.split("# Contracko\n\n", 1)[1].split("\n\n", 1)[0]
        for trigger in ("connecting", "onboarding", "importing", "uploading", "syncing",
                        "other systems", "notifications", "reminders", "notice and end dates",
                        "AI analysis", "portfolio reports", "comparing contracts", "folders",
                        "types", "parties", "creating", "drafting", "templates",
                        "signature handoffs", "filing signed agreements"):
            self.assertIn(trigger, routing)

    def test_preserves_privacy_and_workflow_safety_rules(self) -> None:
        skill_root = ROOT / "skills" / "contracko"
        core = (skill_root / "SKILL.md").read_text()
        self.assertIn(
            "> Contract data will be sent to the AI provider running this session. "
            "Contracko cannot control what that provider does with it. Turn off model training "
            "in the provider's settings before working with real contracts.",
            core,
        )
        for rule in ("completed Task", "nested `result`", "current audience-safe message",
                     "never retry the refused work",
                     "Use the returned trial date rather than assuming a duration"):
            self.assertIn(rule, core)
        expected = {
            "onboarding.md": ("Consent belongs to the user", "Connecting imports nothing"),
            "importing-contracts.md": (
                "Never invent `externalSystem` or `externalId`",
                "Never upload contract bytes to third-party hosts",
                "Confirm the grouping with the user",
                "Before a bulk import",
            ),
            "notifications.md": (
                "say who will be emailed and when", "`expectedUpdatedAt`",
                "Changing notifications on a custom event advances that event's version",
            ),
            "reviewing-ai-analysis.md": (
                "Explain that write and get approval before calling it",
                "a person approves each finding in Contracko",
                "Use `exact` when external query transfer is not authorised",
            ),
            "organising-the-workspace.md": (
                "wait for confirmation before creating or changing it",
                "Confirm the destination and every bulk change before writing",
                "never put a personal identifier in them",
            ),
            "new-agreement.md": (
                "human with legal competence", "Notice period: ask explicitly, never default it",
                "`clm_update_contract` supports metadata, custom-field and lifecycle-status changes",
                "`active`, `expired`, `terminated`, `notice-given`",
                "preference for extracted values over manual supplementation",
            ),
        }
        for reference, phrases in expected.items():
            text = (skill_root / "references" / reference).read_text()
            for phrase in phrases:
                with self.subTest(reference=reference, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_claude_connect_copy_is_directory_first(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn(CLAUDE_DIRECTORY_URL, readme)
        self.assertNotIn("contracko-skills@contracko", readme)
        plugin_install = readme.index("/plugin install contracko@contracko")
        mcp_add = readme.index("claude mcp add")
        self.assertGreater(mcp_add, plugin_install)
        self.assertIn("without the plugin", readme[plugin_install:mcp_add])
        self.assertIn("claude mcp list", readme[mcp_add - 400:mcp_add + 400])
        skill = (ROOT / "skills/contracko/SKILL.md").read_text()
        self.assertIn("https://github.com/contracko/contracko-skills#install", skill)
        self.assertNotIn("claude mcp add", skill)

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
        self.assertEqual(len(names), 60)
        panel_tools = {"clm_show_upload_widget", "clm_prepare_widget_upload"}
        self.assertEqual(len(names - panel_tools), 58)
        index = (ROOT / "skills/contracko/references/tool-index.md").read_text()
        self.assertIn("60 definitions: 58 normal tools plus two Claude-chat upload-panel tools", index)
        self.assertEqual({name for name in names if f"`{name}`" not in index}, set())

        skill = (ROOT / "skills/contracko/SKILL.md").read_text()
        when_to_use = skill[skill.index("## Find the right tool") :]
        when_to_use = when_to_use[: when_to_use.index("\n## ", 1)]
        for trigger in ("unsure which tool", "multi-step job", "first contract"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, when_to_use)

        rows = [line for line in index.splitlines() if line.startswith("| `")]
        self.assertEqual(len(rows), len(names))
        self.assertEqual({line.split("`")[1] for line in rows}, names)
        import_skill = (ROOT / "skills/contracko/references/importing-contracts.md").read_text()
        upload = import_skill.split("## Working the upload path\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("#managed-import", upload)
        self.assertIn("#sync-a-record-from-another-system", upload)
        self.assertNotIn("`clm_ingest_contract`", upload)
        sync = import_skill.split("## Sync a record from another system\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("Sync contract from another system", sync)
        self.assertIn("#choose-import-or-sync", sync)
        attachments = import_skill.split("### Add contract documents\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`clm_add_contract_documents`", attachments)
        for argument in ("`externalSystem`", "`externalId`", "`uploadReference`"):
            self.assertIn(argument, sync)
        onboarding = (ROOT / "skills/contracko/references/onboarding.md").read_text()
        self.assertIn("importing-contracts.md", onboarding)

    def test_connect_copy_matches_released_consent(self) -> None:
        text = (ROOT / "README.md").read_text()
        for phrase in (
            "choose your workspace", "View contracts", "Add and edit contracts",
            "start selected", "Untick", "workspace role allows it",
            "info button", "copyable prompt",
        ):
            self.assertIn(phrase, text)
        paths = (
            "GEMINI.md", "skills/contracko/SKILL.md",
            "packaging/openclaw/README.md", "packaging/hermes/README.md",
        )
        for relative in paths:
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text()
                self.assertIn("#install", text)
                for duplicated in ("View contracts", "Add and edit contracts", "copyable prompt"):
                    self.assertNotIn(duplicated, text)

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

    def test_public_listings_share_ordered_canonical_keywords(self) -> None:
        expected = json.loads((ROOT / "packaging/manifest.json").read_text())["keywords"]
        normalized = [" ".join(keyword.lower().replace("-", " ").split()) for keyword in expected]
        self.assertEqual(len(expected), len(set(normalized)))
        self.assertTrue(all(keyword and keyword == keyword.lower() for keyword in expected))
        self.assertTrue({
            "contracko", "clm", "contract lifecycle management",
            "contract management software", "contract management", "contracts", "ai contract management",
            "contract repository", "contract reminder software", "contract renewal reminders",
            "contract expiration tracking", "ai contract review", "ai contract analysis",
            "contract data extraction", "contract review", "contract analysis",
            "obligation tracking", "renewal tracking", "notice deadlines", "legal", "compliance", "procurement",
        } == set(expected))
        for relative in (
            ".cursor-plugin/plugin.json", ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json", "packages/agent-plugin/plugin.json",
            "packages/mcp/package.json",
        ):
            with self.subTest(path=relative):
                manifest = json.loads((ROOT / relative).read_text())
                self.assertEqual(manifest["keywords"], expected)
        for relative in (".claude-plugin/marketplace.json", ".github/plugin/marketplace.json"):
            plugins = json.loads((ROOT / relative).read_text())["plugins"]
            self.assertTrue(plugins)
            for plugin in plugins:
                with self.subTest(path=relative, plugin=plugin["name"]):
                    self.assertEqual(plugin["keywords"], expected)

    def test_chatgpt_manifest_keywords(self) -> None:
        manifest = json.loads((ROOT / "packaging/chatgpt/plugin.json").read_text())
        self.assertEqual(manifest["keywords"], [
            "CLM",
            "contract lifecycle management",
            "contract management software",
            "contract repository",
            "contract reminder software",
            "contract renewal reminders",
            "contract expiration tracking",
            "AI contract review",
            "AI contract analysis",
            "contract data extraction",
        ])

    def test_client_manifests_mirror_claude_plugin_description_except_cursor(self) -> None:
        expected = (
            "AI contract management (CLM): AI contract review and analysis of risks, liabilities and obligations, "
            "contract data extraction and parsing, automated reminders and renewal and notice deadline tracking."
        )
        descriptions = {
            ".claude-plugin/plugin.json": json.loads((ROOT / ".claude-plugin/plugin.json").read_text())["description"],
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
            "AI contract management: contract review and analysis, data extraction, automated reminders, "
            "and renewal and notice deadline tracking.",
        )
        self.assertLessEqual(len(cursor), 133)
        self.assertLess(len(cursor), len(expected))

        registry = json.loads((ROOT / "server.json").read_text())["description"]
        self.assertEqual(
            registry,
            "AI contract management (CLM): contract review, data extraction, reminders and renewal deadlines.",
        )
        self.assertLessEqual(len(registry), 100)
        for relative in ("packaging/manifest.json", "packages/agent-plugin/plugin.json"):
            with self.subTest(path=relative):
                manifest = json.loads((ROOT / relative).read_text())
                self.assertEqual(
                    manifest["description"],
                    "Contracko contract-management skills with guided native MCP setup.",
                )

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

    def test_agent_plugin_archives_preserve_directory_content_and_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            self.build(first)
            self.build(second)
            first_zip = first / "contracko-agent-plugin.zip"
            self.assertEqual(first_zip.read_bytes(), (second / first_zip.name).read_bytes())
            chatgpt_zip = first / "contracko-agent-plugin-chatgpt.zip"
            self.assertEqual(chatgpt_zip.read_bytes(), (second / chatgpt_zip.name).read_bytes())
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
                self.assertEqual(metadata["artifact"], "contracko-agent-plugin")
                self.assertEqual(metadata["platform"], "agent-plugin")
                with zipfile.ZipFile(chatgpt_zip) as chatgpt:
                    skill_files = {name: content for name, content in expected.items() if name.startswith("skills/")}
                    self.assertEqual(
                        set(chatgpt.namelist()),
                        {".codex-plugin/plugin.json", ".mcp.json", "assets/icon.png"} | set(skill_files),
                    )
                    self.assertEqual(
                        [name for name in chatgpt.namelist() if name.startswith("skills/")],
                        [name for name in archive.namelist() if name.startswith("skills/")],
                    )
                    self.assertNotIn("mcp.json", chatgpt.namelist())
                    self.assertNotIn("plugin.json", chatgpt.namelist())
                    listing = json.loads((ROOT / "packaging/directory-listings.json").read_text())["chatgpt"]
                    self.assertEqual(listing["listingId"], "plugin_asdk_app_6ac8e9b10f548191ab1ed190c3b0ccab")
                    chatgpt_manifest = json.loads(chatgpt.read(".codex-plugin/plugin.json"))
                    self.assertEqual(chatgpt_manifest["name"], listing["pluginName"])
                    self.assertEqual(chatgpt_manifest["version"], VERSION)
                    self.assertEqual(chatgpt_manifest["skills"], "./skills")
                    self.assertEqual(
                        set(chatgpt_manifest),
                        {"author", "description", "keywords", "interface", "name", "skills", "version", "mcpServers", "extensions"},
                    )
                    template = json.loads((ROOT / "packaging/chatgpt/plugin.json").read_text())
                    self.assertNotIn("name", template)
                    self.assertNotIn("version", template)
                    self.assertEqual(
                        chatgpt_manifest,
                        {**template, "name": listing["pluginName"], "version": VERSION},
                    )
                    identity = json.loads((ROOT / "tests/fixtures/chatgpt-1.1.0-identity.json").read_text())
                    interface_fields = {"capabilities", "developerName", "longDescription", "shortDescription"}
                    for field, value in identity.items():
                        if field == "interface":
                            for key, expected_value in value.items():
                                self.assertEqual(chatgpt_manifest["interface"][key], expected_value, key)
                            self.assertEqual(set(chatgpt_manifest["interface"]), set(value) | interface_fields)
                        elif field != "mcp":
                            self.assertEqual(chatgpt_manifest[field], value, field)
                    self.assertEqual(chatgpt_manifest["author"], {"name": "Contracko"})
                    self.assertEqual(chatgpt_manifest["interface"]["developerName"], "Contracko")
                    self.assertLessEqual(len(chatgpt_manifest["interface"]["shortDescription"]), 30)
                    self.assertEqual(chatgpt_manifest["description"], chatgpt_manifest["interface"]["longDescription"])
                    self.assertIn("contract lifecycle management", chatgpt_manifest["keywords"])
                    self.assertEqual(json.loads(chatgpt.read(".mcp.json")), identity["mcp"])
                    self.assertEqual(
                        hashlib.sha256(chatgpt.read("assets/icon.png")).hexdigest(),
                        "bcaa9ddc28dca07718fa5b79c9a4db898f010e257a3e62279243818ee1c5d25a",
                    )
                    for name, content in skill_files.items():
                        variant = ROOT / "packaging/chatgpt" / name
                        expected_content = variant.read_bytes() if variant.is_file() else content
                        self.assertEqual(chatgpt.read(name), expected_content)
                    for entry in chatgpt.infolist():
                        with self.subTest(entry=entry.filename):
                            self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))
                            self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
                            self.assertEqual(entry.create_system, 3)
                            self.assertEqual(entry.external_attr, 0o100644 << 16)
            third = Path(temporary) / "third"
            self.build(third, source_commit="abcdef0123456789abcdef0123456789abcdef01")
            self.assertNotEqual(first_zip.read_bytes(), (third / first_zip.name).read_bytes())
            self.assertEqual(chatgpt_zip.read_bytes(), (third / chatgpt_zip.name).read_bytes())

    def test_chatgpt_archive_has_no_commerce_or_parser_content(self) -> None:
        pattern = re.compile(r"\bfree\b|credit|trial|subscrib|subscription|upgrad|pricing|checkout|billing|parser", re.I)
        allowlist = {
            "skills/contracko/references/organising-the-workspace.md": {
                "SaaS subscriptions, leases, permits, certificates, insurance policies, warranties, and domains use the same pattern: a type, countable fields, native renewal dates, and a notification. Follow the linked portfolio pagination rules.",
            },
            "skills/contracko/references/new-agreement.md": {
                "2. What is bought or sold, for what value, currency and billing rhythm?",
                "For an approved secure destination, record the parties and owned entity, dates/open-ended status, renewal term, notice period and deadline, value/currency/billing rhythm, liability cap, governing law/jurisdiction, filing type, and rejected terms with reasons. In a later conversation, read that handoff before repeating questions.",
            },
        }
        seen = {}
        def scan_manifest(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertIsNone(pattern.search(key), str((*path, key)))
                    scan_manifest(child, (*path, key))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    scan_manifest(child, (*path, index))
            elif isinstance(value, str):
                self.assertIsNone(pattern.search(value), str(path))

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "dist"
            self.build(output)
            with zipfile.ZipFile(output / "contracko-agent-plugin-chatgpt.zip") as archive:
                for name in archive.namelist():
                    self.assertIsNone(pattern.search(name), name)
                    if name == ".codex-plugin/plugin.json":
                        scan_manifest(json.loads(archive.read(name)))
                        continue
                    allowed = allowlist.get(name, set())
                    for line in archive.read(name).decode("utf-8", errors="replace").splitlines():
                        if pattern.search(line):
                            self.assertIn(line, allowed, f"{name}: {line}")
                            seen.setdefault(name, set()).add(line)
                self.assertEqual(seen, allowlist)
                core = archive.read("skills/contracko/SKILL.md").decode()
                self.assertEqual(core.count("If an action is not available on the workspace's current plan, say so plainly and do not retry."), 1)

    def test_chatgpt_manifest_contains_only_public_metadata(self) -> None:
        manifest = json.loads((ROOT / "packaging/chatgpt/plugin.json").read_text())
        settings = manifest["extensions"]["com.openai"]
        self.assertEqual(set(settings), {"publication"})
        self.assertEqual(set(settings["publication"]), {"countries", "release_notes"})

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
                self.assertIn("https://github.com/contracko/contracko-skills#install", readme)
                self.assertNotIn("Add and edit contracts", readme)
                self.assertNotIn("mcp.contracko.com", readme)
                # Built at runtime so this negative check is not itself flagged as a credential.
                self.assertNotIn("Authorization: " + "Bearer", readme)

            self.assertIn("openclaw mcp login contracko", openclaw_readme)
            self.assertIn("hermes mcp login contracko", hermes_readme)

    def test_create_handoff_requires_destination_and_consent(self) -> None:
        text = (ROOT / "skills/contracko/references/new-agreement.md").read_text()
        lowered = text.lower()
        self.assertIn("choose a destination", lowered)
        self.assertIn("explicit consent", lowered)
        self.assertIn("do not write", lowered)
        self.assertIn("if the user does not choose", lowered)
        self.assertNotIn("the handoff, and it is not optional", lowered)


if __name__ == "__main__":
    unittest.main()
