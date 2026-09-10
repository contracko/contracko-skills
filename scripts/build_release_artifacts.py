#!/usr/bin/env python3
"""Build deterministic skill, chat, OpenClaw, and Hermes release archives."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("contracko", "contracko-create", "contracko-import", "contracko-review")
PLATFORMS = ("openclaw", "hermes")
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
COMMIT_PATTERN = re.compile(r"^[a-f0-9]{40}$")


def render(text: str, *, version: str, source_commit: str) -> str:
    return text.replace("{{VERSION}}", version).replace("{{SOURCE_COMMIT}}", source_commit)


def write_bytes(destination: Path, content: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)


def copy_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.name != ".DS_Store":
            write_bytes(destination / path.relative_to(source), path.read_bytes())


def zip_tree(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            relative = path.relative_to(source).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def build_skill_archives(output: Path) -> None:
    for skill in SKILLS:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / skill
            copy_tree(ROOT / "skills" / skill, package)
            zip_tree(Path(temporary), output / f"{skill}.zip")


def merged_chat_tree(destination: Path) -> None:
    source = ROOT
    router = source / "skills" / "contracko"
    merged: dict[Path, Path] = {router / "SKILL.md": destination / "SKILL.md"}

    for path in (router / "references").rglob("*"):
        if path.is_file():
            merged[path] = destination / "references" / path.relative_to(router / "references")

    for name in ("import", "review", "create"):
        merged[source / "skills" / f"contracko-{name}" / "SKILL.md"] = (
            destination / "references" / f"{name}.md"
        )

    for original, target in merged.items():
        content = original.read_text()
        if original.parent.name.startswith("contracko-"):
            parts = content.split("---", 2)
            content = parts[2].lstrip("\n") if len(parts) == 3 and content.startswith("---") else content
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    link = re.compile(r"(]\()([^()\s]+)([^)]*\))")

    def rewrite(match: re.Match[str], original: Path, target: Path) -> str:
        destination_text, suffix = match.group(2), match.group(3)
        parsed = urlsplit(destination_text)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return match.group(0)
        resolved = Path(os.path.normpath(original.parent / parsed.path))
        merged_target = merged.get(resolved)
        if merged_target is None:
            return match.group(0)
        relative = os.path.relpath(merged_target, target.parent).replace(os.sep, "/")
        return match.group(1) + urlunsplit(("", "", relative, parsed.query, parsed.fragment)) + suffix

    for original, target in merged.items():
        target.write_text(link.sub(lambda match: rewrite(match, original, target), target.read_text()))


def build_chat_archive(output: Path) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        package = Path(temporary) / "contracko"
        merged_chat_tree(package)
        router = package / "SKILL.md"
        description = (
            "Contracko contract management over MCP: connect a workspace, import contracts, "
            "answer renewal, risk and vendor questions, organise types and fields, and draft "
            "and file new agreements."
        )
        text = router.read_text()
        text = re.sub(r"^description: .*$", f"description: {description}", text, count=1, flags=re.MULTILINE)
        router.write_text(text)
        zip_tree(Path(temporary), output / "contracko-chat.zip")


def validate_manifest(manifest: dict[str, object], version: str) -> None:
    allowed = {
        "$schema",
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "extensions",
    }
    if set(manifest) - allowed:
        raise ValueError("manifest contains fields outside Agent Plugins v1")
    if not isinstance(manifest.get("$schema"), str):
        raise ValueError("manifest schema must be a string")
    if manifest.get("$schema") != PLUGIN_SCHEMA:
        raise ValueError("manifest does not target Agent Plugins v1")
    name = manifest.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,62}[a-z0-9])?", name):
        raise ValueError("manifest name is outside Agent Plugins v1 constraints")
    if "--" in name or ".." in name:
        raise ValueError("manifest name contains repeated separators")
    if name != "contracko":
        raise ValueError("manifest name must remain contracko")
    if not isinstance(manifest.get("version"), str) or manifest.get("version") != version:
        raise ValueError("manifest version does not match release version")
    if not isinstance(manifest.get("description"), str):
        raise ValueError("manifest description must be a string")
    author = manifest.get("author")
    if not isinstance(author, dict) or set(author) - {"name", "email", "url"}:
        raise ValueError("manifest author is outside Agent Plugins v1 constraints")
    if any(not isinstance(value, str) for value in author.values()):
        raise ValueError("manifest author values must be strings")
    keywords = manifest.get("keywords")
    if not isinstance(keywords, list) or any(not isinstance(value, str) for value in keywords):
        raise ValueError("manifest keywords must be a list of strings")


def build_platform_bundle(output: Path, platform: str, version: str, source_commit: str) -> None:
    package = output / platform
    if package.exists():
        shutil.rmtree(package)
    package.mkdir(parents=True)

    manifest = json.loads((ROOT / "packaging" / "manifest.json").read_text().replace("{{VERSION}}", version))
    validate_manifest(manifest, version)
    for filename in ("mcp.json", ".mcp.json"):
        if (ROOT / "packaging" / platform / filename).exists():
            raise ValueError(f"{platform} bundle must not include {filename}")
    write_bytes(package / "plugin.json", (json.dumps(manifest, indent=2) + "\n").encode())
    copy_tree(ROOT / "packaging" / platform, package)
    readme = package / "README.md"
    readme.write_text(render(readme.read_text(), version=version, source_commit=source_commit))
    write_bytes(package / "LICENSE", (ROOT / "LICENSE").read_bytes())
    write_bytes(package / "NOTICE.md", (ROOT / "packaging" / "NOTICE.md").read_bytes())
    metadata = {
        "artifact": "contracko-agent-plugin",
        "platform": platform,
        "format": "agent-plugins-1.0.0",
        "version": version,
        "source_commit": source_commit,
        "skills": list(SKILLS),
        "generator": "scripts/build_release_artifacts.py",
    }
    write_bytes(package / "RELEASE-METADATA.json", (json.dumps(metadata, indent=2) + "\n").encode())
    for skill in SKILLS:
        copy_tree(ROOT / "skills" / skill, package / "skills" / skill)
    zip_tree(package, output / f"contracko-{platform}.zip")


def default_source_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "working-tree"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--version", default="0.0.0-dev")
    parser.add_argument("--source-commit", default=default_source_commit())
    parser.add_argument(
        "--allow-unpinned",
        action="store_true",
        help="Allow a non-SHA source marker for local, non-release builds",
    )
    args = parser.parse_args()
    if not VERSION_PATTERN.fullmatch(args.version):
        parser.error("--version must be a semantic version")
    if not args.source_commit:
        parser.error("--source-commit must not be empty")
    if not COMMIT_PATTERN.fullmatch(args.source_commit) and not args.allow_unpinned:
        parser.error("--source-commit must be a full 40-character commit SHA")

    args.output.mkdir(parents=True, exist_ok=True)
    for child in args.output.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    build_skill_archives(args.output)
    build_chat_archive(args.output)
    for platform in PLATFORMS:
        build_platform_bundle(args.output, platform, args.version, args.source_commit)
    print("\n".join(path.name for path in sorted(args.output.glob("*.zip"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
