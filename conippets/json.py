import json as json_

load = json_.load
loads = json_.loads
dump = json_.dump
dumps = json_.dumps

del json_

def read(file, mode='r', encoding='utf-8'):
    with open(file, mode=mode, encoding=encoding) as f:
        data = load(f)
    return data

def write(file, data, mode='w', encoding='utf-8', indent=4):
    with open(file, mode=mode, encoding=encoding) as f:
        dump(data, f, ensure_ascii=False, indent=indent)