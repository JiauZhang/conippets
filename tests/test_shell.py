from conippets.shell import Shell
import pytest
import time


def test_basic_stdout(timeout):
    with Shell() as sh:
        r = sh.run("echo hello", timeout=timeout)
        lines = list(r.stdout)
        assert lines == ["hello"]
        assert list(r.stderr) == []
        assert r.exit_code() == 0


def test_stdout_and_stderr(timeout):
    with Shell() as sh:
        r = sh.run("echo out; echo err >&2", timeout=timeout)
        out = list(r.stdout)
        err = list(r.stderr)
        assert out == ["out"]
        assert err == ["err"]
        assert r.exit_code() == 0


def test_multiple_lines(timeout):
    with Shell() as sh:
        r = sh.run("echo a; echo b; echo c", timeout=timeout)
        assert list(r.stdout) == ["a", "b", "c"]
        assert r.exit_code() == 0


def test_exit_code_nonzero(timeout):
    with Shell() as sh:
        r = sh.run("false", timeout=timeout)
        assert r.exit_code() == 1
        r = sh.run("exit 42", timeout=timeout)
        assert r.exit_code() == 42


def test_multi_run_no_cross_contamination(timeout):
    with Shell() as sh:
        r1 = sh.run("echo alpha", timeout=timeout)
        r2 = sh.run("echo beta", timeout=timeout)
        r3 = sh.run("echo gamma; exit 3", timeout=timeout)
        assert list(r3.stdout) == ["gamma"]
        assert r3.exit_code() == 3
        assert list(r2.stdout) == ["beta"]
        assert r2.exit_code() == 0
        assert list(r1.stdout) == ["alpha"]
        assert r1.exit_code() == 0


def test_shell_closed_raises():
    sh = Shell()
    sh.open()
    sh.close()
    with pytest.raises(RuntimeError, match="not open"):
        sh.run("echo never")


def test_context_manager():
    with Shell() as sh:
        assert not sh.closed
        r = sh.run("echo ok")
        assert list(r.stdout) == ["ok"]
    assert sh.closed


def test_cwd(timeout):
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmp:
        with Shell(cwd=tmp) as sh:
            r = sh.run("pwd", timeout=timeout)
            out = list(r.stdout)
            assert out == [os.path.realpath(tmp)]


def test_empty_command(timeout):
    with Shell() as sh:
        r = sh.run("", timeout=timeout)
        assert list(r.stdout) == []
        assert r.exit_code() == 0


def test_large_output(timeout):
    with Shell() as sh:
        r = sh.run("for i in $(seq 1 100); do echo line$i; done", timeout=timeout)
        lines = list(r.stdout)
        assert len(lines) == 100
        assert lines[0] == "line1"
        assert lines[99] == "line100"
        assert r.exit_code() == 0


def test_exit_code_after_stdout(timeout):
    with Shell() as sh:
        r = sh.run("echo data; exit 3", timeout=timeout)
        assert r.exit_code() == 3
        assert list(r.stdout) == ["data"]


def test_multiple_stdout_iterations_same(timeout):
    with Shell() as sh:
        r = sh.run("echo hello", timeout=timeout)
        it1 = list(r.stdout)
        it2 = list(r.stdout)
        assert it1 == ["hello"]
        assert it2 == ["hello"]


def test_timeout_exit_code():
    sh = Shell()
    sh.open()
    try:
        r = sh.run("sleep 10", timeout=1)
        with pytest.raises(TimeoutError):
            r.exit_code()
    finally:
        sh._process.kill()
        sh._process.wait()
        sh.close()


def test_exit_code_override_timeout(timeout):
    with Shell() as sh:
        r = sh.run("echo hi", timeout=timeout)
        assert r.exit_code(timeout=10) == 0


def test_export_env_persists_across_runs(timeout):
    with Shell() as sh:
        r1 = sh.run("export MY_VAR=hello", timeout=timeout)
        assert r1.exit_code() == 0
        r2 = sh.run("echo $MY_VAR", timeout=timeout)
        assert list(r2.stdout) == ["hello"]
        assert r2.exit_code() == 0


def test_export_env_no_leak_between_shells(timeout):
    with Shell() as sh1:
        r = sh1.run("export SECRET=42", timeout=timeout)
        assert r.exit_code() == 0
    with Shell() as sh2:
        r = sh2.run("echo ${SECRET:-empty}", timeout=timeout)
        assert list(r.stdout) == ["empty"]


def test_cancel_foreground_command(timeout):
    with Shell() as sh:
        r = sh.run("sleep 10", timeout=timeout)
        time.sleep(0.3)
        sh.cancel()
        code = r.exit_code()
        assert code is not None
        r2 = sh.run("echo after_cancel", timeout=timeout)
        assert list(r2.stdout) == ["after_cancel"]
        assert r2.exit_code() == 0