#!/usr/bin/env bash
# Build deterministic skill and platform release archives.
set -euo pipefail
cd "$(dirname "$0")"

source_commit="${SOURCE_COMMIT:-}"
allow_unpinned=""
if [ -z "$source_commit" ]; then
  if source_commit=$(git rev-parse HEAD 2>/dev/null); then
    :
  else
    source_commit="working-tree"
    allow_unpinned="--allow-unpinned"
  fi
fi

if [ -n "${CI:-}" ] && ! [[ "$source_commit" =~ ^[0-9a-f]{40}$ ]]; then
  echo "SOURCE_COMMIT must be a full 40-character commit SHA in CI" >&2
  exit 2
fi

release_version="${VERSION:-}"
if [ -z "$release_version" ]; then
  release_version=$(python3 -c 'import json; from pathlib import Path; print(json.loads(Path("packaging/manifest.json").read_text())["version"])')
fi
release_version="${release_version#v}"
python3 scripts/build_release_artifacts.py --check-directory --version "$release_version"
python3 scripts/check_versions.py --tag "v$release_version"

python3 scripts/build_release_artifacts.py \
  --output dist \
  --version "$release_version" \
  --source-commit "$source_commit" \
  $allow_unpinned
