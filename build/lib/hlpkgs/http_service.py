import sys
import asyncio
import inspect
import logging
from .config import conf
from aiohttp import http
http.SERVER_SOFTWARE = conf.get('service.name', 'simple/1.0')
from aiohttp import web


class SimpleHttpService:
    def __init__(self, initializer = None):
        self._app = web.Application()
        self._initializer = initializer

    def start(self, healing = True):
        loop = asyncio.get_event_loop()
        if hasattr(self._initializer, '__call__'):
            if inspect.isawaitable(self._initializer):
                loop.run_until_complete(self._initializer(self._app))
            else:
                self._initializer(self._app)  
        while healing:
            try:      
                web.run_app(self._app, host=conf.get('service.host', '127.0.0.1'), port=conf.number('service.port', 8181))    
            except:
                logging.fatal(sys.exc_info())
                if loop.is_closed():
                    break
                loop.run_until_complete(asyncio.sleep(5))


__all__ = ['SimpleHttpService']
