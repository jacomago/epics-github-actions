import time
import subprocess
import pytest
from unittest.mock import MagicMock, patch
from scripts.wait_for_pv import wait_for_pv


def _result(returncode: int) -> MagicMock:
    r = MagicMock(spec=subprocess.CompletedProcess)
    r.returncode = returncode
    return r


def test_sleep_fallback_when_no_pv(monkeypatch):
    slept = []
    monkeypatch.setattr(time, "sleep", slept.append)
    wait_for_pv("caget", "", wait_timeout=7)
    assert slept == [7]


def test_ready_on_first_poll(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)
    with patch("subprocess.run", return_value=_result(0)) as mock_run:
        wait_for_pv("caget", "MY:PV", poll_timeout=5)
    mock_run.assert_called_once_with(["caget", "-w", "1", "MY:PV"], capture_output=True)


def test_ready_after_retries(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)
    responses = [_result(1), _result(1), _result(0)]
    with patch("subprocess.run", side_effect=responses):
        wait_for_pv("pvxget", "MY:PV", poll_timeout=10)


def test_timeout_exits_nonzero(monkeypatch, tmp_path):
    monkeypatch.setattr(time, "sleep", lambda _: None)
    with patch("subprocess.run", return_value=_result(1)):
        with pytest.raises(SystemExit):
            wait_for_pv("caget", "MY:PV", poll_timeout=2)


def test_timeout_dumps_log_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(time, "sleep", lambda _: None)
    log = tmp_path / "ioc.log"
    log.write_text("IOC startup output")
    with patch("subprocess.run", return_value=_result(1)):
        with pytest.raises(SystemExit):
            wait_for_pv("caget", "MY:PV", poll_timeout=1, log_file=str(log))
    assert "IOC startup output" in capsys.readouterr().out


def test_timeout_calls_docker_logs_when_no_log_file(monkeypatch):
    monkeypatch.setattr(time, "sleep", lambda _: None)
    monkeypatch.setenv("SOFTIOC_CONTAINER", "my-ioc")
    responses = [_result(1), _result(1)]
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return _result(1)

    with patch("subprocess.run", side_effect=fake_run):
        with pytest.raises(SystemExit):
            wait_for_pv("caget", "MY:PV", poll_timeout=2)

    assert any("docker" in str(c) for c in calls)
