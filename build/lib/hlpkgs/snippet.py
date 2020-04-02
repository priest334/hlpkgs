from functools import partial

def TextToValue(valuetype, text, default=None):
    if valuetype is None:
        return None
    if default and not isinstance(default, valuetype):
        raise TypeError('default value must be type: {}'.format(valuetype))
    try:
        return valuetype(text)
    except:
        if default is None:
            return text
        else:
            return default

T2I = partial(TextToValue, int)
T2F = partial(TextToValue, float)

def Round(x, a, b):
   return a if x < a else b if x > b else x

def PartialCopy(src: dict, *args):
    ret = {}
    for key in args:
        ret.update({key: src.get(key, None)})
    return ret

def CopyDict(src: dict, include_keys = [], exclude_keys = []):
    if include_keys:
        keys = set(include_keys)
        return PartialCopy(src, *tuple(keys))
    if exclude_keys:
        keys = set(src.keys())-set(exclude_keys)
        return PartialCopy(src, *tuple(keys))
    return src.copy()


__all__ = ['TextToValue', 'T2I', 'T2F', 'Round', 'PartialCopy', 'CopyDict']
