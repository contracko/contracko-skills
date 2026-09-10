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

python3 scripts/build_release_artifacts.py \
  --output dist \
  --version "${VERSION:-0.0.0-dev}" \
  --source-commit "$source_commit" \
  $allow_unpinned
