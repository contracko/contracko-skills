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
# The router becomes SKILL.md; the siblings become reference files beside it,
# so every handoff resolves inside one upload.
work=$(mktemp -d)/contracko
mkdir -p "$work/references"
cp skills/contracko/SKILL.md "$work/SKILL.md"
cp skills/contracko/references/tool-index.md "$work/references/"
for s in import review create; do
  # strip frontmatter: a reference file is prose, not a skill
  awk 'BEGIN{n=0} /^---$/{n++; next} n>=2' "skills/contracko-$s/SKILL.md" > "$work/references/$s.md"
done

# rewrite cross-skill paths to the merged layout. The router sits one level
# above its references, so the two get different rules.
sed -i '' -e 's|\.\./contracko-\([a-z]*\)/SKILL\.md|references/\1.md|g' "$work/SKILL.md"
for f in "$work"/references/*.md; do
  sed -i '' \
    -e 's|\.\./contracko/SKILL\.md|../SKILL.md|g' \
    -e 's|\.\./contracko-\([a-z]*\)/SKILL\.md|\1.md|g' \
    -e 's|\.\./\.\./contracko-\([a-z]*\)/SKILL\.md|\1.md|g' \
    -e 's|(\.\./\([a-z-]*\)\.md)|(\1.md)|g' \
    -e 's|(\.\./SKILL\.md)|(../SKILL.md)|g' "$f"
done

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
