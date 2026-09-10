#!/usr/bin/env python3
"""Build deterministic skill archives and Agent Plugins directory/release packages."""

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
DIRECTORY_PACKAGE = ROOT / "packages" / "agent-plugin"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
VERSION_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
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


def load_manifest(version: str | None = None) -> dict[str, object]:
    manifest = json.loads((ROOT / "packaging" / "manifest.json").read_text())
    if version is not None:
        manifest["version"] = version
    manifest_version = manifest.get("version")
    if not isinstance(manifest_version, str) or "{{" in manifest_version:
        raise ValueError("packaging manifest must contain a concrete version")
    validate_manifest(manifest, manifest_version)
    return manifest


def build_platform_bundle(output: Path, platform: str, version: str, source_commit: str) -> None:
    package = output / platform
    if package.exists():
        shutil.rmtree(package)
    package.mkdir(parents=True)

    manifest = load_manifest(version)
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


def populate_directory_package(destination: Path, manifest: dict[str, object]) -> None:
    source = ROOT / "packaging" / "directory"
    reject_symlink_entries(source, label="directory packaging source")
    for filename in ("mcp.json", ".mcp.json"):
        if (source / filename).exists():
            raise ValueError(f"directory package must not include {filename}")
    destination.mkdir(parents=True, exist_ok=True)
    write_bytes(destination / "plugin.json", (json.dumps(manifest, indent=2) + "\n").encode())
    copy_tree(source, destination)
    write_bytes(destination / "LICENSE", (ROOT / "LICENSE").read_bytes())
    write_bytes(destination / "NOTICE.md", (ROOT / "packaging" / "NOTICE.md").read_bytes())
    for skill in SKILLS:
        skill_source = ROOT / "skills" / skill
        reject_symlink_entries(skill_source, label=f"canonical skill source {skill}")
        copy_tree(skill_source, destination / "skills" / skill)


def reject_symlink_entries(path: Path, *, label: str) -> None:
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symlink: {path}")
    for child in path.rglob("*"):
        if child.is_symlink():
            relative = child.relative_to(path).as_posix()
            raise ValueError(f"{label} contains symlink: {relative}")


def directory_files(path: Path) -> list[str]:
    reject_symlink_entries(path, label="directory package")
    return sorted(
        child.relative_to(path).as_posix()
        for child in path.rglob("*")
        if child.is_file() and child.name != ".DS_Store"
    )


def check_directory_package(expected_version: str | None = None) -> None:
    manifest = load_manifest()
    if expected_version is not None and manifest["version"] != expected_version:
        raise ValueError(
            "directory package version "
            f"{manifest['version']} does not match requested release version {expected_version}"
        )
    with tempfile.TemporaryDirectory() as temporary:
        expected = Path(temporary) / "agent-plugin"
        populate_directory_package(expected, manifest)
        if not DIRECTORY_PACKAGE.is_dir() or DIRECTORY_PACKAGE.is_symlink():
            raise ValueError("packages/agent-plugin is missing or is not a real directory")
        expected_files = directory_files(expected)
        actual_files = directory_files(DIRECTORY_PACKAGE)
        if expected_files != actual_files:
            missing = sorted(set(expected_files) - set(actual_files))
            extra = sorted(set(actual_files) - set(expected_files))
            raise ValueError(
                "directory package drift: "
                f"missing={missing or 'none'} extra={extra or 'none'}"
            )
        for relative in expected_files:
            expected_bytes = (expected / relative).read_bytes()
            actual_bytes = (DIRECTORY_PACKAGE / relative).read_bytes()
            if expected_bytes != actual_bytes:
                raise ValueError(f"directory package drift: {relative} differs")


def write_directory_package() -> None:
    manifest = load_manifest()
    with tempfile.TemporaryDirectory() as temporary:
        expected = Path(temporary) / "agent-plugin"
        populate_directory_package(expected, manifest)
        if DIRECTORY_PACKAGE.exists() and DIRECTORY_PACKAGE.is_symlink():
            raise ValueError("packages/agent-plugin must not be a symlink")
        if DIRECTORY_PACKAGE.exists() and not DIRECTORY_PACKAGE.is_dir():
            raise ValueError("packages/agent-plugin must be a directory")
        DIRECTORY_PACKAGE.parent.mkdir(parents=True, exist_ok=True)
        if DIRECTORY_PACKAGE.exists():
            shutil.rmtree(DIRECTORY_PACKAGE)
        shutil.copytree(expected, DIRECTORY_PACKAGE)


def default_source_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "working-tree"


def validate_output_path(output: Path) -> Path:
    """Return a safe output path without allowing source-tree deletion."""
    resolved = output.resolve()
    root = ROOT.resolve()
    dist = root / "dist"

    # The default release output lives under dist. Every other path inside the
    # checkout is either source, tests, metadata, or git state and must remain
    # protected from the clean-before-build step. Keep dist lexical: resolving
    # it would let a symlink redefine the only repository subtree we may clean.
    try:
        resolved.relative_to(root)
    except ValueError:
        pass
    else:
        try:
            resolved.relative_to(dist)
        except ValueError:
            raise ValueError("--output must be outside the repository or inside repository dist/")

    # An ancestor of the repository would delete the checkout when cleaned.
    try:
        root.relative_to(resolved)
    except ValueError:
        pass
    else:
        raise ValueError("--output cannot contain the repository")

    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument(
        "--version",
        default=None,
        help="Release version; directory checks reject versions differing from the committed package",
    )
    parser.add_argument("--source-commit", default=default_source_commit())
    parser.add_argument(
        "--allow-unpinned",
        action="store_true",
        help="Allow a non-SHA source marker for local, non-release builds",
    )
    directory = parser.add_mutually_exclusive_group()
    directory.add_argument(
        "--check-directory",
        action="store_true",
        help="Check the committed Agent Plugins directory package for generated drift",
    )
    directory.add_argument(
        "--write-directory",
        action="store_true",
        help="Regenerate the committed Agent Plugins directory package",
    )
    args = parser.parse_args()
    version = args.version or "0.0.0-dev"
    if not VERSION_PATTERN.fullmatch(version):
        parser.error("--version must be a semantic version")

    if args.check_directory or args.write_directory:
        try:
            if args.write_directory:
                write_directory_package()
            else:
                check_directory_package(args.version)
        except ValueError as error:
            parser.error(str(error))
        return 0

    if not args.source_commit:
        parser.error("--source-commit must not be empty")
    if not COMMIT_PATTERN.fullmatch(args.source_commit) and not args.allow_unpinned:
        parser.error("--source-commit must be a full 40-character commit SHA")

    try:
        output = validate_output_path(args.output)
    except ValueError as error:
        parser.error(str(error))
    output.mkdir(parents=True, exist_ok=True)
    for child in output.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    build_skill_archives(output)
    build_chat_archive(output)
    for platform in PLATFORMS:
        build_platform_bundle(output, platform, version, args.source_commit)
    print("\n".join(path.name for path in sorted(output.glob("*.zip"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
