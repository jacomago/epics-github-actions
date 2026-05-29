import pytest
from scripts.detect_arch import get_arch


@pytest.mark.parametrize(
    "system,machine,expected",
    [
        ("Linux",  "x86_64",  "linux-x86_64"),
        ("Linux",  "aarch64", "linux-aarch64"),
        ("Darwin", "x86_64",  "darwin-x86_64"),
        ("Darwin", "arm64",   "darwin-aarch64"),
    ],
)
def test_known_platforms(system, machine, expected):
    assert get_arch(system, machine) == expected


def test_unknown_platform_raises():
    with pytest.raises(SystemExit, match="Unsupported platform"):
        get_arch("Windows", "x86_64")
