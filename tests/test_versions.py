import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VERSION_FIELDS = (
    ("packages/agent-plugin/plugin.json", ("version",)),
    (".claude-plugin/plugin.json", ("version",)),
    (".claude-plugin/marketplace.json", ("metadata", "version")),
    (".claude-plugin/marketplace.json", ("plugins", 0, "version")),
    (".agents/plugins/marketplace.json", ("plugins", 0, "version")),
    (".codex-plugin/plugin.json", ("version",)),
    (".cursor-plugin/plugin.json", ("version",)),
    (".github/plugin/marketplace.json", ("plugins", 0, "version")),
    ("gemini-extension.json", ("version",)),
    ("server.json", ("version",)),
    ("server.json", ("packages", 0, "version")),
    ("packages/mcp/package.json", ("version",)),
    ("packages/mcp/package-lock.json", ("version",)),
    ("packages/mcp/package-lock.json", ("packages", "", "version")),
)


class PublicVersionTests(unittest.TestCase):
    def check(self, root=ROOT, tag=None):
        command = ["python3", str(ROOT / "scripts/check_versions.py"), "--root", str(root)]
        if tag is not None:
            command += ["--tag", tag]
        return subprocess.run(command, capture_output=True, text=True)

    def fixture(self, root):
        for directory in ("packaging", "packages", ".claude-plugin", ".codex-plugin", ".cursor-plugin", ".agents", ".github/plugin"):
            shutil.copytree(ROOT / directory, root / directory)
        for path in ROOT.glob("*.json"):
            shutil.copyfile(path, root / path.name)

    def test_committed_public_versions_and_release_tag_agree(self):
        version = json.loads((ROOT / "packaging/manifest.json").read_text())["version"]
        for tag in (None, f"v{version}"):
            with self.subTest(tag=tag):
                result = self.check(tag=tag)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_public_surface_rejects_drift(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            root = Path(temporary)
            self.fixture(root)
            for relative, location in PUBLIC_VERSION_FIELDS:
                with self.subTest(path=relative, field=location):
                    path = root / relative
                    original = path.read_bytes()
                    document = json.loads(original)
                    target = document
                    for key in location[:-1]:
                        target = target[key]
                    target[location[-1]] = "9.9.9"
                    path.write_text(json.dumps(document))
                    result = self.check(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(relative, result.stderr)
                    path.write_bytes(original)

    def test_rejects_wrong_and_malformed_release_tags(self):
        for tag in ("v9.9.9", "1.1.0", "v1.1", "v1.1.0-rc.1"):
            with self.subTest(tag=tag):
                result = self.check(tag=tag)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("release tag", result.stderr)

    def test_ignores_unrelated_nested_versions_on_public_surfaces(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            root = Path(temporary)
            self.fixture(root)
            for relative in sorted({relative for relative, location in PUBLIC_VERSION_FIELDS}):
                path = root / relative
                document = json.loads(path.read_text())
                document["dependencies"] = {"example": {"version": "9.9.9"}}
                document["protocol"] = {"schema": {"version": "2.0.0"}}
                if "plugins" in document:
                    document["plugins"][0]["config"] = {"version": "3.0.0"}
                path.write_text(json.dumps(document))
            result = self.check(root)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_checks_new_top_level_public_fields_but_not_lockfile_dependencies(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            root = Path(temporary)
            self.fixture(root)
            lock = root / "packages/mcp/package-lock.json"
            document = json.loads(lock.read_text())
            document["packages"]["node_modules/example"] = {"version": "9.9.9"}
            lock.write_text(json.dumps(document))
            self.assertEqual(self.check(root).returncode, 0)
            manifest = root / ".agents/plugins/marketplace.json"
            document = json.loads(manifest.read_text())
            document["plugins"][0]["version"] = "9.9.9"
            manifest.write_text(json.dumps(document))
            result = self.check(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(".agents/plugins/marketplace.json", result.stderr)
            manifest.write_bytes((ROOT / ".agents/plugins/marketplace.json").read_bytes())
            (root / "packaging/new-client.json").write_text('{"version": "9.9.9"}')
            result = self.check(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("packaging/new-client.json", result.stderr)

    def test_rejects_missing_public_versions_and_invalid_source(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            root = Path(temporary)
            self.fixture(root)
            fields = (("packaging/manifest.json", ("version",)),) + PUBLIC_VERSION_FIELDS
            for relative, location in fields:
                with self.subTest(path=relative, field=location):
                    path = root / relative
                    original = path.read_bytes()
                    document = json.loads(original)
                    target = document
                    for key in location[:-1]:
                        target = target[key]
                    if location[-1] not in target:
                        continue
                    del target[location[-1]]
                    path.write_text(json.dumps(document))
                    result = self.check(root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(relative, result.stderr)
                    path.write_bytes(original)
            source = root / "packaging/manifest.json"
            document = json.loads(source.read_text())
            document["version"] = "{{VERSION}}"
            source.write_text(json.dumps(document))
            self.assertNotEqual(self.check(root).returncode, 0)


if __name__ == "__main__":
    unittest.main()
