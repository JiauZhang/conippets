from conippets import json

def read(file, mode='r', encoding='utf-8'):
    with open(file, mode=mode, encoding=encoding) as f:
        for line in f:
            data = json.loads(line)
            yield data

def __writelines__(file, data, *, mode, encoding):
    with open(file, mode=mode, encoding=encoding) as f:
        for item in data:
            line = json.dumps(item, ensure_ascii=False, indent=None)
            f.write(line + '\n')

def write(file, data, encoding='utf-8'):
    __writelines__(file, data, mode='w', encoding=encoding)

def append(file, data, encoding='utf-8'):
    __writelines__(file, data, mode='a', encoding=encoding)