from conippets import json

class Config(dict):
    def __init__(self, **kwargs):
        kwargs = {
            k: Config(**v) if isinstance(v, dict) else v
            for k, v in kwargs.items()
        }
        super().__init__(**kwargs)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if isinstance(value, dict):
            value = Config(**value)
        self[name] = value

    @classmethod
    def from_json(cls, file):
        cfg = json.read(file)
        if not isinstance(cfg, dict):
            raise TypeError(f"JSON root must be a dict, got {type(cfg).__name__}.")
        return cls(**cfg)

    def save(self, file):
        json.write(file, self)
