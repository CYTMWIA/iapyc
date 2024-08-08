import os


def ls(path: str):
    return [os.path.join(path, p) for p in os.listdir(path)]
