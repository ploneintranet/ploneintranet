from zope.interface import implementer
from .interfaces import IExecutor


@implementer(IExecutor)
class SyncExecutor(object):
    """The syncronous executor.

    Calls the function straight away.
    """

    def run(self, func, *args, **kwargs):
        func(*args, **kwargs)
