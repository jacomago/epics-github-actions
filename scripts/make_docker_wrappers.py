import sys
from pathlib import Path

_ENVFWD = (
    "-e EPICS_CA_AUTO_ADDR_LIST"
    " -e EPICS_CA_ADDR_LIST"
    " -e EPICS_PVA_AUTO_ADDR_LIST"
    " -e EPICS_PVA_ADDR_LIST"
)
_TEMPLATE = (
    '#!/usr/bin/env bash\n'
    'exec docker run --rm --network "{network}" {envfwd} "{image}" "{cmd}" "$@"\n'
)


def make_wrappers(
    wrappers_dir: str, network: str, image: str, commands: list[str]
) -> None:
    dest = Path(wrappers_dir)
    dest.mkdir(parents=True, exist_ok=True)
    for cmd in commands:
        path = dest / cmd
        path.write_text(
            _TEMPLATE.format(network=network, envfwd=_ENVFWD, image=image, cmd=cmd)
        )
        path.chmod(0o755)


if __name__ == "__main__":
    # argv: wrappers_dir network image cmd [cmd ...]
    make_wrappers(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
