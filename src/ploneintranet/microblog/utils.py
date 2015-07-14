import time
from BTrees import LLBTree


def longkeysortreverse(
        btreeish, minv=None, maxv=None, limit=None, reverse=True):
    """Performance optimized keyspace accessor.
    Returns an iterable of btreeish keys, reverse sorted by key.
    Expects a btreeish with long(microsec) keys.
    """
    try:
        accessor = btreeish.keys
    except AttributeError:
        accessor = LLBTree.TreeSet(btreeish).keys

    i = 0

    if minv or maxv:
        # no optimization
        keys = [x for x in accessor(min=minv, max=maxv)]
        keys.sort()
        if reverse:
            keys.reverse()
        for key in keys:
            yield key
            i += 1
            if i == limit:
                return

    else:

        # first run: last hour
        tmax = long(time.time() * 1e6)
        tmin = long(tmax - 3600 * 1e6)
        keys = [x for x in accessor(min=tmin, max=tmax)]
        keys.sort()
        if reverse:
            keys.reverse()
        for key in keys:
            yield key
            i += 1
            if i == limit:
                return

        # second run: last day until last hour
        tmax = tmin
        tmin = long(tmax - 23 * 3600 * 1e6)
        keys = [x for x in accessor(min=tmin, max=tmax)]
        keys.sort()
        if reverse:
            keys.reverse()
        for key in keys:
            yield key
            i += 1
            if i == limit:
                return

        # final run: everything else
        tmax = tmin
        keys = [x for x in accessor(max=tmax)]
        keys.sort()
        if reverse:
            keys.reverse()
        for key in keys:
            yield key
            i += 1
            if i == limit:
                return
