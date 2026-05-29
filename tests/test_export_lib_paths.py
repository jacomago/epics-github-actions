import platform
import pytest
from scripts.export_lib_paths import export_lib_paths


def test_linux_writes_ld_library_path(tmp_path, monkeypatch):
    env_file = tmp_path / "GITHUB_ENV"
    monkeypatch.delenv("LD_LIBRARY_PATH", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    export_lib_paths(["/a", "/b"], github_env=str(env_file))
    assert env_file.read_text() == "LD_LIBRARY_PATH=/a:/b\n"


def test_macos_writes_dyld_library_path(tmp_path, monkeypatch):
    env_file = tmp_path / "GITHUB_ENV"
    monkeypatch.delenv("DYLD_LIBRARY_PATH", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    export_lib_paths(["/x"], github_env=str(env_file))
    assert env_file.read_text() == "DYLD_LIBRARY_PATH=/x\n"


def test_prepends_to_existing_path(tmp_path, monkeypatch):
    env_file = tmp_path / "GITHUB_ENV"
    monkeypatch.setenv("LD_LIBRARY_PATH", "/existing")
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    export_lib_paths(["/new"], github_env=str(env_file))
    assert env_file.read_text() == "LD_LIBRARY_PATH=/new:/existing\n"


def test_appends_to_existing_file(tmp_path, monkeypatch):
    env_file = tmp_path / "GITHUB_ENV"
    env_file.write_text("OTHER=value\n")
    monkeypatch.delenv("LD_LIBRARY_PATH", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    export_lib_paths(["/p"], github_env=str(env_file))
    lines = env_file.read_text().splitlines()
    assert lines[0] == "OTHER=value"
    assert lines[1] == "LD_LIBRARY_PATH=/p"


def test_creates_file_if_missing(tmp_path, monkeypatch):
    env_file = tmp_path / "GITHUB_ENV"
    monkeypatch.delenv("LD_LIBRARY_PATH", raising=False)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    assert not env_file.exists()
    export_lib_paths(["/p"], github_env=str(env_file))
    assert env_file.exists()
