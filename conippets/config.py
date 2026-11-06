from collections.abc import Mapping

from conippets import json


def _convert(value):
    if isinstance(value, Mapping) and all(isinstance(key, str) for key in value):
        return Config(**value)
    if isinstance(value, (list, tuple)):
        return [_convert(item) for item in value]
    return value


class Config(dict):
    def __init__(self, **kwargs):
        super().__init__(**{key: _convert(value) for key, value in kwargs.items()})

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        self[name] = _convert(value)

    @classmethod
    def from_dict(cls, mapping):
        if not isinstance(mapping, Mapping):
            raise TypeError(f"Config root must be a mapping, got {type(mapping).__name__}.")
        config = cls()
        config.update({key: _convert(value) for key, value in mapping.items()})
        return config

    @classmethod
    def from_json(cls, file):
        return cls.from_dict(json.read(file))

    def save(self, file):
        json.write(file, self)
