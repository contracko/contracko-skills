#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from build_release_artifacts import VERSION_PATTERN


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packaging/manifest.json"
REQUIRED = (
    SOURCE,
    "packages/agent-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
    "gemini-extension.json",
    "server.json",
    "packages/mcp/package.json",
    "packages/mcp/package-lock.json",
)
PUBLIC_DIRECTORIES = (
    "packaging", "packages/agent-plugin", ".claude-plugin", ".codex-plugin",
    ".cursor-plugin", ".agents/plugins", ".github/plugin",
)


def version_locations(relative, document):
    if relative in REQUIRED or "version" in document:
        yield ("version",)
    if relative == "packages/mcp/package-lock.json":
        yield ("packages", "", "version")
    if relative == "server.json":
        for index, package in enumerate(document.get("packages", [])):
            yield ("packages", index, "version")
    if relative == ".claude-plugin/marketplace.json":
        yield ("metadata", "version")
    if relative in (
        ".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json",
        ".github/plugin/marketplace.json",
    ):
        for index, plugin in enumerate(document.get("plugins", [])):
            if relative == ".github/plugin/marketplace.json" or "version" in plugin:
                yield ("plugins", index, "version")


def check(root: Path, tag: str | None = None) -> str:
    version = json.loads((root / SOURCE).read_text()).get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
        raise ValueError(f"{SOURCE}: version must be a concrete semantic version")
    paths = set(root.glob("*.json"))
    paths.update(root / relative for relative in REQUIRED)
    paths.update(root / relative for relative in (
        ".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json",
        ".github/plugin/marketplace.json",
    ))
    for directory in PUBLIC_DIRECTORIES:
        paths.update((root / directory).rglob("*.json"))
    failures = []
    for path in sorted(paths):
        relative = path.relative_to(root).as_posix()
        document = json.loads(path.read_text())
        for location in version_locations(relative, document):
            field = ".".join(map(str, location))
            actual = document
            try:
                for key in location:
                    actual = actual[key]
            except (KeyError, IndexError, TypeError):
                failures.append(f"{relative}: missing {field}")
                continue
            if actual != version:
                failures.append(f"{relative}:{field} is {actual!r}, expected {version}")
    if tag is not None and tag != f"v{version}":
        failures.append(f"release tag {tag!r} does not match v{version}")
    if failures:
        raise ValueError("\n".join(failures))
    return version


def main() -> int:
    parser = argparse.ArgumentParser(description="Check every public version against packaging/manifest.json.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tag", help="Release tag, including its v prefix")
    args = parser.parse_args()
    try:
        version = check(args.root, args.tag)
    except (OSError, ValueError, TypeError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Public versions agree: {version}" + (f" ({args.tag})" if args.tag else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
