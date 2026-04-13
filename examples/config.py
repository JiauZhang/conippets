from conippets.config import Config

cfg = Config()
cfg.x = 6
assert cfg.x == 6

cfg = Config(
    a=3, b=4, c=5, d=6,
    e={'f': 7, 'g': 8},
)

assert cfg.a == 3 and cfg.e.f == 7

has_exception = False
try:
    cfg.e.c
except Exception as e:
    has_exception = True
assert has_exception == True

cfg.f = {'q': 8, 'z': 1, 'm': {'x': 3, 'y': 9}}

assert cfg.f.q == 8 and cfg.f.m.x == 3
