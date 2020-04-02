import sys
import traceback
import functools
import inspect
import logging
import asyncio

def PrintException():
    logger.warning(' EXCEPTION '.center(100,'=')+'\n'+''.join(traceback.format_exception(*sys.exc_info())))

class CatchException:
    def __init__(self, default=None):
        self.default = default

    def __call__(self, api, *args, **kwargs):
        wrapper = api
        if inspect.iscoroutinefunction(api):
            @functools.wraps(api)
            async def async_decorator(*args, **kwargs):
                try:
                    return await api(*args, **kwargs)
                except:
                    PrintException()
                    return self.default
            wrapper = async_decorator
        else:
            @functools.wraps(api)
            def sync_decorator(*args, **kwargs):
                try:
                    return api(*args, **kwargs)
                except:
                    PrintException()
                    return self.default
            wrapper = sync_decorator
        return wrapper


__all__ = ['PrintException', 'CatchException']
