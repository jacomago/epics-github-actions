#!/usr/bin/env bash
# Usage: make-docker-wrappers.sh WRAPPERS_DIR NETWORK IMAGE CMD [CMD...]
# Creates exec-docker wrapper scripts for each CMD in WRAPPERS_DIR.
set -euo pipefail
WRAPPERS="$1"; NETWORK="$2"; IMAGE="$3"; shift 3
ENVFWD='-e EPICS_CA_AUTO_ADDR_LIST -e EPICS_CA_ADDR_LIST -e EPICS_PVA_AUTO_ADDR_LIST -e EPICS_PVA_ADDR_LIST'
mkdir -p "$WRAPPERS"
for CMD in "$@"; do
  printf '#!/usr/bin/env bash\nexec docker run --rm --network "%s" %s "%s" "%s" "$@"\n' \
    "$NETWORK" "$ENVFWD" "$IMAGE" "$CMD" > "$WRAPPERS/$CMD"
  chmod +x "$WRAPPERS/$CMD"
done
