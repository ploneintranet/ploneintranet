from zope.component import queryUtility
from .interfaces import IExecutor


def maybe_async(func):
    def _wrapper(*args, **kwargs):
        executor = queryUtility(IExecutor)
        executor.run(func, *args, **kwargs)
    return _wrapper
