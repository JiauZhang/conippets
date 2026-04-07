from conippets.config import Config

data = dict(
    a=3, b=4, c=5, d=6,
    e={'f': 7, 'g': 8},
)
cfg = Config(**data)

assert cfg.a == 3 and cfg.e.f == 7
try:
    cfg.e.c
except Exception as e:
    print(e)
