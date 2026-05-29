import platform
import sys

_MAPPING = {
    ("Linux",  "x86_64"):  "linux-x86_64",
    ("Linux",  "aarch64"): "linux-aarch64",
    ("Darwin", "x86_64"):  "darwin-x86_64",
    ("Darwin", "arm64"):   "darwin-aarch64",
}


def get_arch(system: str, machine: str) -> str:
    arch = _MAPPING.get((system, machine))
    if arch is None:
        raise SystemExit(
            f"Unsupported platform: {system}-{machine}. "
            "Add it to scripts/detect_arch.py."
        )
    return arch


if __name__ == "__main__":
    print(get_arch(platform.system(), platform.machine()))
