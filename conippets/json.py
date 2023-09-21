import json as json_

load = json_.load
loads = json_.loads
dump = json_.dump
dumps = json_.dumps

del json_

def read(file, mode, encoding='utf-8', **kwargs):
    with open(file, mode=mode, encoding=encoding, **kwargs) as f:
        data = load(f)
    return data

def write(data, file, mode, encoding='utf-8', indent=4, **kwargs):
    with open(file, mode=mode, encoding=encoding) as f:
        dump(data, f, ensure_ascii=False, indent=indent, **kwargs)