#!/usr/bin/env python3
"""Public contracts for the @contracko/mcp npx launcher."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "packages" / "mcp"
MCP_URL = "https://app.contracko.com/mcp"


class McpShimTests(unittest.TestCase):
    def test_package_is_a_public_npx_launcher_not_a_second_server(self) -> None:
        package = json.loads((PACKAGE_DIR / "package.json").read_text())
        self.assertEqual(package["name"], "@contracko/mcp")
        self.assertEqual(package["bin"]["contracko-mcp"], "bin/contracko-mcp.js")
        self.assertEqual(package["publishConfig"]["access"], "public")
        self.assertEqual(package["publishConfig"]["registry"], "https://registry.npmjs.org")
        self.assertIn("mcp-remote", package["dependencies"])
        self.assertNotIn("private", package)
        self.assertEqual(package["engines"]["node"], ">=20.18.1")
        self.assertEqual(package["mcpName"], "com.contracko/contracko")

        launcher = (PACKAGE_DIR / "bin" / "contracko-mcp.js").read_text()
        self.assertIn(MCP_URL, launcher)
        self.assertIn("mcp-remote", launcher)
        self.assertIn("'proxy.js'", launcher)
        self.assertIn("stdio", launcher)
        self.assertNotIn("path.resolve(process.argv[1])", launcher)

    def test_server_json_advertises_the_npm_package_beside_the_http_remote(self) -> None:
        server = json.loads((REPO_ROOT / "server.json").read_text())
        remotes = server.get("remotes") or []
        self.assertTrue(
            any(remote.get("url") == MCP_URL for remote in remotes),
            "HTTP remote must keep the hosted endpoint",
        )
        packages = server.get("packages") or []
        npm = next(
            (
                item
                for item in packages
                if item.get("registryType") == "npm" and item.get("identifier") == "@contracko/mcp"
            ),
            None,
        )
        self.assertIsNotNone(npm)
        assert npm is not None
        self.assertEqual(npm["transport"]["type"], "stdio")
        self.assertEqual(npm["version"], json.loads((PACKAGE_DIR / "package.json").read_text())["version"])

    def test_distribution_docs_name_the_npx_command(self) -> None:
        docs = (REPO_ROOT / "DISTRIBUTION.md").read_text()
        self.assertIn("npx -y @contracko/mcp", docs)
        self.assertIn(MCP_URL, docs)

    def test_lockfile_pins_patched_proxy_addr_and_qs(self) -> None:
        package = json.loads((PACKAGE_DIR / "package.json").read_text())
        self.assertEqual(package["overrides"]["proxy-addr"], "2.0.8")
        self.assertEqual(package["overrides"]["qs"], "6.16.0")

        lock = json.loads((PACKAGE_DIR / "package-lock.json").read_text())
        packages = lock["packages"]
        proxy = packages["node_modules/proxy-addr"]["version"]
        self.assertGreaterEqual(tuple(int(part) for part in proxy.split(".")), (2, 0, 8))

        qs_versions = [
            entry["version"]
            for name, entry in packages.items()
            if name == "node_modules/qs" or name.endswith("/node_modules/qs")
        ]
        self.assertTrue(qs_versions)
        for version in qs_versions:
            self.assertGreaterEqual(tuple(int(part) for part in version.split(".")), (6, 16, 0))


if __name__ == "__main__":
    unittest.main()
