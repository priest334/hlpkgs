from abc import ABC, abstractmethod

class Cache(ABC):
    def __init__(self):
        self._data = {}

    @abstractmethod
    def get(self, key, default=None):
        return self._data.get(key, default)

    @abstractmethod
    def set(self, key, value):
        self._data.update({key: value})


installed_cache_kclass = Cache

cache = None
named_cache = {}

def defaultCache():
    global cache
    if not cache:
        cache = installed_cache_kclass()
    return cache

def getCache(name):
    if not name:
        return defaultCache()
    instance = named_cache.get(name, None)
    if not instance:
        instance = installed_cache_kclass()
        named_cache[name] = instance
    return instance

def setCacheClass(kclass):
    global installed_cache_kclass
    installed_cache_kclass = kclass


def get(key, default=None):
    return getCache().get(key, default)

def set(key, value):
    return getCache().set(key, value)


__all__ = ['get', 'set', 'setCacheClass', 'getCache']

