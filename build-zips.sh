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
directory_check_args=(--check-directory)
if [ -n "$release_version" ]; then
  release_version="${release_version#v}"
  directory_check_args+=(--version "$release_version")
fi
python3 scripts/build_release_artifacts.py "${directory_check_args[@]}"

python3 scripts/build_release_artifacts.py \
  --output dist \
  --version "${release_version:-0.0.0-dev}" \
  --source-commit "$source_commit" \
  $allow_unpinned
