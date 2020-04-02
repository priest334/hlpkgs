import sys
import os
from time import strftime, localtime
import logging


class Daemon(object):
    @staticmethod
    def warning(msg):
        logging.waring('[{}] {}'.format(strftime('%Y-%m-%d %H:%M:%S',localtime()), msg))

    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self._forkable = False
        if not hasattr(os, 'fork'):
            Daemon.warning('fork is unsupported on this platform')
            return
        self._forkable = True
        self._stdin = open(stdin, 'r')
        self._stdout = open(stdout, 'a+')
        self._stderr = open(stderr, 'a+')

    def start(self):
        if not self._forkable:
            return
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
        elif pid < 0:
            Daemon.warning('fork is failed with error {}'.format(os.errno))
        os.setsid()
        sys.stdin = self._stdin
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        Daemon.warning('daemon process is running with pid={}'.format(os.getpid()))

def runas_daemon():
    d = Daemon()
    d.start()



__all__ = ['runas_daemon']