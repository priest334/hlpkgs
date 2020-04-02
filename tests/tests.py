#!/usr/bin/env python3


import sys
import logging
import hlpkgs

def main(argv):
    if hlpkgs.conf.has('daemon'):
        hlpkgs.runas_daemon()
    service = hlpkgs.SimpleHttpService()
    service.start()


if __name__ == '__main__':
    main(sys.argv[1:])

