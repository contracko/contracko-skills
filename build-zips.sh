#!/usr/bin/env bash
# Package the skills for upload.
#
#   dist/<skill>.zip     one zip per skill, for Claude Code and for anyone
#                        who wants a single skill on its own
#   dist/contracko-chat.zip
#                        ALL FOUR merged into one skill, for Claude Desktop
#                        and claude.ai chat, where each upload is isolated and
#                        cross-skill links would otherwise point at nothing
#
# Settings > Capabilities > Skills > upload. Skill folder at the archive root.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p dist && rm -rf dist/* 

for s in skills/*/; do
  name=$(basename "$s")
  (cd skills && zip -qr "../dist/$name.zip" "$name" -x "*.DS_Store")
done

# --- merged chat build -------------------------------------------------------
# The router becomes SKILL.md; its references and sibling skills become local
# files so every handoff resolves inside one upload.
work=$(mktemp -d)/contracko
python3 - "$(pwd)" "$work" <<'PY'
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

source = Path(sys.argv[1])
work = Path(sys.argv[2])
router = source / "skills" / "contracko"
merged = {router / "SKILL.md": work / "SKILL.md"}

# Preserve the full router reference tree, including references added later.
for path in (router / "references").rglob("*"):
    if path.is_file():
        merged[path] = work / "references" / path.relative_to(router / "references")

for name in ("import", "review", "create"):
    merged[source / "skills" / f"contracko-{name}" / "SKILL.md"] = work / "references" / f"{name}.md"

for original, destination in merged.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = original.read_text()
    if original.parent.name.startswith("contracko-"):
        # A sibling is prose in the merged skill, not a nested skill.
        parts = text.split("---", 2)
        text = parts[2].lstrip("\n") if len(parts) == 3 and text.startswith("---") else text
    destination.write_text(text)

link = re.compile(r"(]\()([^)\s]+)([^)]*\))")

def rewrite(match, original, destination):
    target, suffix = match.group(2), match.group(3)
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return match.group(0)
    resolved = Path(os.path.normpath(original.parent / parsed.path))
    merged_target = merged.get(resolved)
    if merged_target is None:
        return match.group(0)
    relative = os.path.relpath(merged_target, destination.parent).replace(os.sep, "/")
    return match.group(1) + urlunsplit(("", "", relative, parsed.query, parsed.fragment)) + suffix

for original, destination in merged.items():
    destination.write_text(link.sub(lambda match: rewrite(match, original, destination), destination.read_text()))
PY

# one description has to carry every job, and claude.ai caps it at 200 chars
python3 - "$work/SKILL.md" <<'PY'
import re,sys,pathlib
d="Contracko contract management over MCP: connect a workspace, import contracts, answer renewal, risk and vendor questions, organise types and fields, and draft and file new agreements."
assert len(d)<=200, len(d)
p=pathlib.Path(sys.argv[1]); t=p.read_text()
t=re.sub(r'^description: .*$','description: '+d,t,count=1,flags=re.M)
p.write_text(t)
PY

(cd "$(dirname "$work")" && zip -qr - contracko -x "*.DS_Store") > dist/contracko-chat.zip
rm -rf "$(dirname "$work")"

ls -1 dist/
