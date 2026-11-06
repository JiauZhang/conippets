import json

import pytest

from conippets.config import Config


def test_nested_dicts_become_configs():
    config = Config(vision=dict(hidden_size=32, inner=dict(depth=2)))
    assert isinstance(config.vision, Config)
    assert isinstance(config.vision.inner, Config)
    assert config.vision.inner.depth == 2


def test_non_string_keys_stay_plain_dict():
    config = Config(labels={0: "a", 1: "b"})
    assert config.labels == {0: "a", 1: "b"}
    assert not isinstance(config.labels, Config)


def test_list_items_are_converted():
    config = Config(modules=[dict(name="a"), {0: "b"}])
    assert isinstance(config.modules[0], Config)
    assert config.modules[1] == {0: "b"}


def test_from_dict():
    config = Config.from_dict({"hidden_size": 32, "labels": {0: "a"}})
    assert config.hidden_size == 32
    assert config.labels == {0: "a"}


def test_from_dict_requires_mapping():
    with pytest.raises(TypeError):
        Config.from_dict([("hidden_size", 32)])


def test_from_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"hidden_size": 32, "vision": {"depth": 2}}))
    config = Config.from_json(path)
    assert config.hidden_size == 32
    assert isinstance(config.vision, Config)
    assert config.vision.depth == 2
