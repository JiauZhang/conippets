from conippets import json

def read(file, mode='r', encoding='utf-8'):
    with open(file, mode=mode, encoding=encoding) as f:
        for line in f:
            data = json.loads(line)
            yield data

def __writelines__(f, data):
    for item in data:
        line = json.dumps(item, ensure_ascii=False, indent=None)
        f.write(line + '\n')

def write(file, data, mode='w', encoding='utf-8'):
    with open(file, mode=mode, encoding=encoding) as f:
        __writelines__(f, data)

def append(file, data, mode='a', encoding='utf-8'):
    with open(file, mode=mode, encoding=encoding) as f:
        __writelines__(f, data)