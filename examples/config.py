from conippets.config import Config

data = dict(
    a=3, b=4, c=5, d=6,
    e={'f': 7, 'g': 8},
)
cfg = Config(**data)

assert cfg.a == 3 and cfg.e.f == 7

has_exception = False
try:
    cfg.e.c
except Exception as e:
    has_exception = True
assert has_exception == True

cfg.f = {'q': 8, 'z': 1, 'm': {'x': 3, 'y': 9}}

assert cfg.f.q == 8 and cfg.f.m.x == 3
assert cfg.f.m.__key_trace__ == ['f', 'm']
