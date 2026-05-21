import os
import subprocess
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor


class Result:
    def __init__(self, stdout_stream, stderr_stream, marker, pool, timeout=None):
        self._exit_code = None
        self._exit_event = threading.Event()
        self._out_lines = []
        self._err_lines = []
        self._out_done = threading.Event()
        self._err_done = threading.Event()
        self._timeout = timeout

        pool.submit(self._reader, stdout_stream, self._out_lines, self._out_done, marker)
        pool.submit(self._reader, stderr_stream, self._err_lines, self._err_done, marker)

    def _reader(self, stream, lines, done, marker):
        for line in stream:
            line = line.rstrip("\n")
            if marker in line:
                self._set_exit_code(int(line.split(":")[1]))
                break
            lines.append(line)
        if not self._exit_event.is_set():
            self._set_exit_code(-1)
        done.set()

    def _set_exit_code(self, code):
        if self._exit_event.is_set():
            return
        self._exit_code = code
        self._exit_event.set()

    def _iter_lines(self, lines, done):
        idx = 0
        while True:
            if idx < len(lines):
                yield lines[idx]
                idx += 1
            elif self._exit_event.is_set() and done.is_set():
                break
            else:
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


class Shell:
    def __init__(self, cwd=None):
        self._cwd = cwd or os.getcwd()
        self._process = None
        self._pool = ThreadPoolExecutor(max_workers=2)
        self._last_result = None

    def open(self):
        self._process = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._cwd,
            text=True,
            bufsize=1,
        )
        return self

    def close(self):
        if self._process and self._process.poll() is None:
            self._process.stdin.write("exit\n")
            self._process.stdin.flush()
            self._process.wait(timeout=5)
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
        cmd = f"({command})\necho \"EXIT:$?:{marker}\"\necho \"EXIT:$?:{marker}\" >&2\n"
        self._process.stdin.write(cmd)
        self._process.stdin.flush()

        result = Result(self._process.stdout, self._process.stderr, marker, self._pool, timeout=timeout)
        self._last_result = result
        return result

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()