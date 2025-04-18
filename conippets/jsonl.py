from conippets import json

def read(file, encoding='utf-8', eager=True):
    with open(file, mode='r', encoding=encoding) as f:
        generator = (json.loads(line) for line in f)
        if eager: return list(generator)
        else: yield from generator

def __writelines__(file, data, *, mode, encoding):
    with open(file, mode=mode, encoding=encoding) as f:
        for item in data:
            line = json.dumps(item, ensure_ascii=False, indent=None)
            f.write(line + '\n')

def write(file, data, encoding='utf-8'):
    __writelines__(file, data, mode='w', encoding=encoding)

def append(file, data, encoding='utf-8'):
    __writelines__(file, data, mode='a', encoding=encoding)