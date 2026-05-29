#!/usr/bin/env bash
# Usage: wait-for-pv.sh POLL_CMD WAIT_PV POLL_TIMEOUT WAIT_TIMEOUT [LOG_FILE]
# Polls WAIT_PV using POLL_CMD until ready or POLL_TIMEOUT seconds elapse.
# When WAIT_PV is empty, sleeps WAIT_TIMEOUT seconds instead.
# On timeout, dumps LOG_FILE if given, otherwise docker logs $SOFTIOC_CONTAINER.
set -euo pipefail
POLL_CMD="$1"
WAIT_PV="$2"
POLL_TIMEOUT="${3:-30}"
WAIT_TIMEOUT="${4:-10}"
LOG_FILE="${5:-}"

if [ -n "$WAIT_PV" ]; then
  echo "Polling PV: $WAIT_PV"
  for i in $(seq 1 "$POLL_TIMEOUT"); do
    if "$POLL_CMD" -w 1 "$WAIT_PV" > /dev/null 2>&1; then
      echo "IOC ready after ${i}s"
      exit 0
    fi
    sleep 1
  done
  echo "::error::IOC did not become ready within ${POLL_TIMEOUT}s"
  if [ -n "$LOG_FILE" ]; then
    cat "$LOG_FILE"
  else
    docker logs "$SOFTIOC_CONTAINER" || true
  fi
  exit 1
else
  echo "No wait-pv specified, sleeping ${WAIT_TIMEOUT}s"
  sleep "$WAIT_TIMEOUT"
fi
