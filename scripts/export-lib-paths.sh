#!/usr/bin/env bash
# Usage: export-lib-paths.sh PATH [PATH...]
# Prepends paths to LD_LIBRARY_PATH (Linux) or DYLD_LIBRARY_PATH (macOS) via GITHUB_ENV.
set -euo pipefail
JOINED=$(IFS=:; echo "$*")
if [ "$(uname)" = "Linux" ]; then
  echo "LD_LIBRARY_PATH=${JOINED}:${LD_LIBRARY_PATH:-}" >> "$GITHUB_ENV"
else
  echo "DYLD_LIBRARY_PATH=${JOINED}:${DYLD_LIBRARY_PATH:-}" >> "$GITHUB_ENV"
fi
