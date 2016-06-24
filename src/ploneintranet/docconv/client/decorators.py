# coding=utf-8
from ploneintranet.docconv.client import handlers


def force_synchronous_previews(func):
    ''' Decorator that will force the previews to be generated synchrously
    '''
    def wrapper(*args, **kwargs):
        backup = handlers.ASYNC_ENABLED
        handlers.ASYNC_ENABLED = False
        try:
            return func(*args, **kwargs)
        finally:
            handlers.ASYNC_ENABLED = backup
    return wrapper
