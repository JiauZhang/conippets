import os
import pty
import select
import subprocess
import termios
import threading
import uuid


def _split_pty(text):
    for line in text.replace("\r\n", "\n").rstrip("\n").split("\n"):
        line = line.rstrip("\r")
        if line:
            yield line


def _split_pipe(text):
    for line in text.rstrip("\n").split("\n"):
        line = line.rstrip("\r")
        if line:
            yield line


def _read_fd_until_marker(fd, marker, split_func, lines, done_event, cancel_event=None):
    buf = b""
    marker_seen = False
    try:
        while True:
            if cancel_event and cancel_event.is_set():
                break
            try:
                r, _, _ = select.select([fd], [], [], 0.1)
            except OSError:
                break
            if not r:
                continue
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
            buf += data
            decoded = buf.decode("utf-8", errors="replace")
            if marker not in decoded:
                continue
            marker_seen = True
            idx = decoded.find(marker)
            lines.extend(split_func(decoded[:idx]))
            return decoded[idx:]
    finally:
        if buf and not marker_seen:
            lines.extend(split_func(buf.decode("utf-8", errors="replace")))
        done_event.set()
    return None


class Result:
    def __init__(self, master_fd, stderr_r, marker, process, timeout=None):
        self._exit_code = None
        self._exit_event = threading.Event()
        self._out_lines = []
        self._err_lines = []
        self._out_done = threading.Event()
        self._err_done = threading.Event()
        self._timeout = timeout
        self._process = process
        self._cancel_requested = threading.Event()

        self._exit_marker = f"EXIT:{marker}:"
        self._err_marker = f"STDERR_MARKER:{marker}"

        threading.Thread(target=self._read_stdout, args=(master_fd,), daemon=True).start()
        threading.Thread(target=self._read_stderr, args=(stderr_r,), daemon=True).start()

    def cancel(self):
        self._cancel_requested.set()

    def _read_stdout(self, master_fd):
        rest = _read_fd_until_marker(
            master_fd, self._exit_marker, _split_pty,
            self._out_lines, self._out_done,
            cancel_event=self._cancel_requested,
        )
        if rest is not None:
            exit_line = rest.split("\n")[0].rstrip("\r")
            try:
                code = int(exit_line[len(self._exit_marker):])
                self._set_exit_code(code)
            except (ValueError, IndexError):
                self._set_exit_code(-1)
        elif not self._exit_event.is_set():
            if self._cancel_requested.is_set():
                self._set_exit_code(-2)
            else:
                rc = self._process.poll()
                self._set_exit_code(rc if rc is not None else -1)

    def _read_stderr(self, stderr_r):
        _read_fd_until_marker(
            stderr_r, self._err_marker, _split_pipe,
            self._err_lines, self._err_done,
            cancel_event=self._cancel_requested,
        )

    def _set_exit_code(self, code):
        if self._exit_event.is_set():
            return
        self._exit_code = code
        self._exit_event.set()

    def _iter_lines(self, lines, done):
        idx = 0
        while True:
            while idx < len(lines):
                yield lines[idx]
                idx += 1
            if self._exit_event.is_set() and done.is_set():
                break
            self._exit_event.wait(timeout=0.01)

    @property
    def stdout(self):
        return self._iter_lines(self._out_lines, self._out_done)

    @property
    def stderr(self):
        return self._iter_lines(self._err_lines, self._err_done)

    def exit_code(self, timeout=None):
        if timeout is None:
            timeout = self._timeout
        self._exit_event.wait(timeout=timeout)
        if not self._exit_event.is_set():
            raise TimeoutError("Command did not finish")
        return self._exit_code

    def drain(self):
        self._out_done.wait()
        self._err_done.wait()


def _safe_close(fd):
    if fd is not None:
        try:
            os.close(fd)
        except OSError:
            pass


class Shell:
    def __init__(self, cwd=None):
        self._cwd = cwd or os.getcwd()
        self._master_fd = None
        self._stderr_r = None
        self._process = None
        self._last_result = None

    def open(self):
        master_fd, slave_fd = pty.openpty()
        stderr_r, stderr_w = os.pipe()

        attrs = termios.tcgetattr(slave_fd)
        attrs[3] = attrs[3] & ~termios.ECHO
        termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)

        self._process = subprocess.Popen(
            ["/bin/bash"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=stderr_w,
            cwd=self._cwd,
            start_new_session=True,
        )

        os.close(slave_fd)
        os.close(stderr_w)

        self._master_fd = master_fd
        self._stderr_r = stderr_r

        os.write(self._master_fd, b"trap ':' INT\n")

        return self

    def close(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
        if self._last_result is not None:
            self._last_result.drain()
        _safe_close(self._master_fd)
        self._master_fd = None
        _safe_close(self._stderr_r)
        self._stderr_r = None
        self._process = None

    @property
    def closed(self):
        return self._process is None or self._process.poll() is not None

    def run(self, command, timeout=None):
        if self.closed:
            raise RuntimeError("Shell is not open")

        if self._last_result is not None:
            self._last_result.drain()

        if not command.strip():
            command = ":"

        marker = uuid.uuid4().hex
        cmd = f"{command}\necho \"EXIT:{marker}:$?\"\necho \"STDERR_MARKER:{marker}\" >&2\n"
        os.write(self._master_fd, cmd.encode())

        result = Result(
            self._master_fd, self._stderr_r, marker,
            self._process, timeout=timeout,
        )
        self._last_result = result

        return result

    def cancel(self):
        if self._master_fd is not None:
            os.write(self._master_fd, b"\x03")
            if self._last_result is not None:
                self._last_result.cancel()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()