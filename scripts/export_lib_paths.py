import os
import platform
import sys
from pathlib import Path


def export_lib_paths(paths: list[str], github_env: str | None = None) -> None:
    var = "LD_LIBRARY_PATH" if platform.system() == "Linux" else "DYLD_LIBRARY_PATH"
    existing = os.environ.get(var, "")
    joined = ":".join(paths)
    value = f"{joined}:{existing}" if existing else joined
    env_file = Path(github_env or os.environ["GITHUB_ENV"])
    with env_file.open("a") as f:
        f.write(f"{var}={value}\n")


if __name__ == "__main__":
    export_lib_paths(sys.argv[1:])
