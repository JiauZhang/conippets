import logging
from importlib.metadata import entry_points

logger = logging.getLogger(__name__)


def load(group):
    for ep in entry_points(group=group):
        try:
            yield ep.load()
        except Exception as exc:
            logger.warning('failed to load plugin %s: %s', ep, exc)


def collect(group, attr, key=None):
    items = []
    seen = set()
    for mod in load(group):
        for item in getattr(mod, attr, []) or []:
            k = key(item) if key else item
            if k in seen:
                continue
            seen.add(k)
            items.append(item)
    return items