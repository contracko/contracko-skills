#!/usr/bin/env python3
"""Public artifact checks for skill packaging."""

from __future__ import annotations

import re
import posixpath
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("contracko", "contracko-create", "contracko-import", "contracko-review")
MARKDOWN_LINK = re.compile(r"!?\[[^]]*]\(([^)\s]+)(?:\s+[^)]*)?\)")


class PackagingTests(unittest.TestCase):
    def test_builds_portable_archives_with_resolved_merged_links(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            copied_repo = Path(temp_dir) / "repo"
            shutil.copytree(REPO_ROOT, copied_repo, ignore=shutil.ignore_patterns(".git", "dist"))
            bin_dir = Path(temp_dir) / "bin"
            bin_dir.mkdir()
            for command in (
                "bash",
                "basename",
                "dirname",
                "ls",
                "mkdir",
                "mktemp",
                "python3",
                "rm",
                "zip",
            ):
                executable = shutil.which(command)
                assert executable, f"missing test prerequisite: {command}"
                (bin_dir / command).symlink_to(executable)

            subprocess.run(
                [str(copied_repo / "build-zips.sh")],
                cwd=copied_repo,
                env={"PATH": str(bin_dir)},
                check=True,
            )

            for skill in SKILLS:
                with zipfile.ZipFile(copied_repo / "dist" / f"{skill}.zip") as archive:
                    self.assertIn(f"{skill}/SKILL.md", archive.namelist())

            with zipfile.ZipFile(copied_repo / "dist" / "contracko-chat.zip") as archive:
                markdown = {
                    name: archive.read(name).decode("utf-8")
                    for name in archive.namelist()
                    if name.endswith(".md")
                }

            for source, content in markdown.items():
                for destination in MARKDOWN_LINK.findall(content):
                    parsed = urlsplit(destination)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    target = posixpath.normpath(
                        posixpath.join(posixpath.dirname(source), parsed.path)
                    )
                    self.assertIn(target, markdown, f"{source} links to missing {destination}")


if __name__ == "__main__":
    unittest.main()
