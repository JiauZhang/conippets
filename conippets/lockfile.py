import os.path as osp
from glob import glob
from conippets import json
from conippets.path import rm


class LockFile:
    def __init__(self, root, *, name='file-lock.json', saved=30):
        self.root, self.name, self.saved = root, name, saved
        self.lock_file = f'{root}/{name}'
        self.files = self._load()

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        return self.files[index]

    def __iter__(self):
        return iter(self.files)

    def __contains__(self, file):
        return file in self.files

    @property
    def current(self):
        return self.files[-1] if self.files else None

    def _datasets(self):
        pats = (f'{self.root}/**/*.json', f'{self.root}/**/*.md')
        return sorted(
            osp.basename(f) for f in glob(pats[0], recursive=True) + glob(pats[1], recursive=True)
            if osp.basename(f) != self.name
        )

    def _load(self):
        datasets = self._datasets()
        if not osp.exists(self.lock_file):
            for f in datasets:
                rm(f'{self.root}/{f}', missing_ok=True)
            return []
        files = [f for f in dict.fromkeys(json.read(self.lock_file)) if osp.exists(f'{self.root}/{f}')]
        recorded = set(files)
        return files + [f for f in datasets if f not in recorded]

    def add(self, file):
        if self.files[-1:] != [file]:
            self.files.append(file)

    def trim(self):
        diff = len(self.files) - self.saved
        if diff > 0:
            for i in range(diff):
                rm(f'{self.root}/{self.files[i]}', missing_ok=True)
            self.files = self.files[diff:]

    def save(self):
        json.write(self.lock_file, self.files)
