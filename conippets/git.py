from .shell import Shell


class Git:
    def __init__(self, cwd=None):
        self._shell = Shell(cwd=cwd)
        self._shell.open()

    def _run(self, cmd):
        return self._shell.run(f"git {cmd}")

    def run(self, cmd):
        return self._run(cmd)

    def status(self):
        return self._run("status")

    def add(self, *paths):
        if not paths:
            return self._run("add .")
        return self._run(f"add {' '.join(paths)}")

    def commit(self, message):
        msg = message.replace("'", "'\\''")
        return self._run(f"commit -m '{msg}'")

    def log(self, n=10):
        return self._run(f"log --oneline -{n}")

    def diff(self, args=""):
        return self._run(f"diff {args}")

    def push(self, remote="origin", branch=None):
        cmd = f"push {remote}"
        if branch:
            cmd += f" {branch}"
        return self._run(cmd)

    def pull(self, remote="origin", branch=None):
        cmd = f"pull {remote}"
        if branch:
            cmd += f" {branch}"
        return self._run(cmd)

    def branch(self, args=""):
        return self._run(f"branch {args}")

    def checkout(self, target):
        return self._run(f"checkout {target}")

    def clone(self, repo, dest=None, branch=None, depth=None):
        cmd = f"clone {repo}"
        if branch:
            cmd += f" --branch {branch}"
        if depth:
            cmd += f" --depth {depth}"
        if dest:
            cmd += f" {dest}"
        return self._run(cmd)