#
""""""
from os import getpid
import logging.handlers
from .snippet import T2I

def mapped_level(name):
    levels = {'debug': logging.DEBUG, 'info': logging.INFO,  'warning': logging.WARNING, 'error': logging.ERROR, 'fatal': logging.FATAL}
    return levels[name] if name in levels else logging.WARNING;

def mapped_when(name):
    when = ['S', 'M', 'H', 'D']
    return name if name in when else when[-1]

def mapped_backup_count(name):
    return T2I(name, default=7)

def mapped_interval(name):
    return T2I(name, 1)

def init_logging_parameters(**kwargs):
    logger = logging.getLogger()
    filename = kwargs.get('log.file', 'default.{}.log'.format(getpid()))
    level = mapped_level(kwargs.get('log.level', 'warning'))
    backup = mapped_backup_count(kwargs.get('log.backup', 7))
    when = mapped_when(kwargs.get('log.when', 'D').upper())
    interval = mapped_interval(kwargs.get('log.interval', 1))
    handler = logging.handlers.TimedRotatingFileHandler(filename, backupCount = backup, when = when, interval = interval)
    formatter = logging.Formatter('[%(asctime)s]+%(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')     
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
