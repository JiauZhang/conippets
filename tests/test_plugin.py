from conippets.plugin import collect


class _EP:
    def __init__(self, mod):
        self._mod = mod

    def load(self):
        return self._mod


def _noop_entry_points(group=""):
    return []


def test_collect_empty_when_no_plugins(monkeypatch):
    monkeypatch.setattr("conippets.plugin.entry_points", _noop_entry_points)
    assert collect("x.tools", "tools") == []


def test_collect_dedupes_and_skips_missing_attr(monkeypatch):
    mods = [
        type("M1", (), {"tools": ["a", "b"]}),
        type("M2", (), {"tools": ["b", "c"]}),
        type("M3", (), {}),
    ]
    monkeypatch.setattr(
        "conippets.plugin.entry_points",
        lambda group="": [_EP(m) for m in mods],
    )
    assert collect("g", "tools") == ["a", "b", "c"]


def test_collect_with_key(monkeypatch):
    mods = [type("M1", (), {"tools": [{"name": "a"}, {"name": "a"}]})]
    monkeypatch.setattr(
        "conippets.plugin.entry_points",
        lambda group="": [_EP(m) for m in mods],
    )
    assert [t["name"] for t in collect("g", "tools", key=lambda t: t["name"])] == ["a"]


def test_collect_tolerates_broken_plugin(monkeypatch):
    class _BadEP:
        def load(self):
            raise RuntimeError("boom")

    mods = [_BadEP(), _EP(type("M", (), {"tools": ["ok"]}))]
    monkeypatch.setattr(
        "conippets.plugin.entry_points",
        lambda group="": mods,
    )
    assert collect("g", "tools") == ["ok"]
