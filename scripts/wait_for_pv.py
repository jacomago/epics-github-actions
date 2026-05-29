import os
import subprocess
import sys
import time
from pathlib import Path


def wait_for_pv(
    poll_cmd: str,
    wait_pv: str,
    poll_timeout: int = 30,
    wait_timeout: int = 10,
    log_file: str = "",
) -> None:
    if not wait_pv:
        print(f"No wait-pv specified, sleeping {wait_timeout}s")
        time.sleep(wait_timeout)
        return

    print(f"Polling PV: {wait_pv}")
    for i in range(1, poll_timeout + 1):
        result = subprocess.run([poll_cmd, "-w", "1", wait_pv], capture_output=True)
        if result.returncode == 0:
            print(f"IOC ready after {i}s")
            return
        time.sleep(1)

    print(f"::error::IOC did not become ready within {poll_timeout}s", file=sys.stderr)
    if log_file and Path(log_file).exists():
        print(Path(log_file).read_text())
    else:
        container = os.environ.get("SOFTIOC_CONTAINER", "")
        if container:
            subprocess.run(["docker", "logs", container])
    sys.exit(1)


if __name__ == "__main__":
    # argv: poll_cmd wait_pv poll_timeout wait_timeout [log_file]
    args = sys.argv[1:]
    wait_for_pv(
        args[0],
        args[1],
        int(args[2]),
        int(args[3]),
        args[4] if len(args) > 4 else "",
    )
