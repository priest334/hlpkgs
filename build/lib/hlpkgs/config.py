# mit license
"""
use conf readonly
"""

import sys, os, logging
from .default_init_handlers import init_logging_parameters
from .snippet import TextToValue


class Conf(dict):
    def __init__(self):
        self.load('hlpkgs.conf')

    def _parse_line(self, line):
        s = line.strip()
        if s.startswith('#'):
            return None, None
        pos = s.find('=')
        if pos == -1:
            return s, ''
        key, value = s[0:pos], s[pos+1:]
        key = key.rstrip()
        value = value.lstrip()
        return key, value

    def load(self, filename):
        if filename and os.path.exists(filename):
            with open(filename, 'rt') as file:
                for line in file:
                    key, value = self._parse_line(line)
                    if not key:
                        continue
                    self[key] = value
        init_logging_parameters(**self)
        return True

    def number(self, key, default=None, valuetype=int):
        value = self.get(key, None)
        if value is None:
            return default
        return TextToValue(valuetype, value, default)

    def has(self, key):
        return key in self;

conf = Conf()

__all__ = ['conf']
