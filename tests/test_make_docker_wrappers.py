from scripts.make_docker_wrappers import make_wrappers


def test_creates_executable_wrappers(tmp_path):
    make_wrappers(str(tmp_path), "my-net", "my/image:tag", ["caget", "caput"])
    for cmd in ("caget", "caput"):
        p = tmp_path / cmd
        assert p.exists()
        assert p.stat().st_mode & 0o111, "wrapper should be executable"
        text = p.read_text()
        assert "my-net" in text
        assert "my/image:tag" in text
        assert f'"{cmd}"' in text
        assert "EPICS_CA_AUTO_ADDR_LIST" in text
        assert "EPICS_PVA_ADDR_LIST" in text


def test_creates_parent_directories(tmp_path):
    dest = str(tmp_path / "nested" / "wrappers")
    make_wrappers(dest, "net", "img", ["caget"])
    assert (tmp_path / "nested" / "wrappers" / "caget").exists()


def test_wrapper_is_bash_script(tmp_path):
    make_wrappers(str(tmp_path), "net", "img", ["caget"])
    text = (tmp_path / "caget").read_text()
    assert text.startswith("#!/usr/bin/env bash")


def test_empty_command_list(tmp_path):
    make_wrappers(str(tmp_path), "net", "img", [])
    assert list(tmp_path.iterdir()) == []
