from conippets import json

class Config(dict):
    def __init__(self, **kwargs):
        cfg_kwargs = {}
        for k, v in kwargs.items():
            if isinstance(v, dict):
                cfg_kwargs[k] = Config(**v)
            elif isinstance(v, (list, tuple)):
                cfg_kwargs[k] = [Config(**vi) if isinstance(vi, dict) else vi for vi in v]
            else:
                cfg_kwargs[k] = v

        super().__init__(**cfg_kwargs)

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
