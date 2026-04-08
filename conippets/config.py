from conippets import json

class Config(dict):
    def __init__(self, *, __key_trace__=[], **kwargs):
        super().__init__(**kwargs)

        self.__key_trace__ = __key_trace__
        for k, v in self.items():
            if isinstance(v, dict):
                self[k] = Config(**v, __key_trace__=self.__key_trace__+[k])

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            key_trace = self.__key_trace__ + [name]
            raise AttributeError(f"'Config' object has no attribute '{'.'.join(key_trace)}'.")

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = Config(**value, __key_trace__=self.__key_trace__+[name])
        self[name] = value

    @classmethod
    def from_json(cls, file):
        cfg = json.read(file)
        if not isinstance(cfg, dict):
            raise TypeError(f"JSON root must be a dict, got {type(cfg).__name__}.")
        return cls(**cfg)

    def save(self, file):
        json.write(file, self)
