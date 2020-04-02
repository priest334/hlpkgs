import hashlib


def md5(src):
    m = hashlib.md5()
    m.update(src.encode())
    return m.hexdigest()

def sha512(src):
    m = hashlib.sha512()
    m.update(src.encode())
    return m.hexdigest()


__all__ = ['md5', 'sha512']


