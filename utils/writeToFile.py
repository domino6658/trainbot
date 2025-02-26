import json

def write(filename, data):
    with open(filename, 'w') as f:
        f.seek(0)
        f.truncate(0)
        f.write(data)
