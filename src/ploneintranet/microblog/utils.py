# coding=utf-8
from BTrees import LLBTree

import time


def longkeysortreverse(btreeish, minv=None, maxv=None, limit=None):
    """Performance optimized keyspace accessor.
    Returns an iterable of btreeish keys, reverse sorted by key.
    Expects a btreeish with long(microsec) keys.
    """
    try:
        accessor = btreeish.keys
    except AttributeError:
        accessor = LLBTree.TreeSet(btreeish).keys

    i = 0

    minv_or_maxv = minv or maxv

    if minv_or_maxv:
        tmin = minv
        tmax = maxv
    else:
        tmax = long(time.time() * 1e6)
        tmin = long(tmax - 3600 * 1e6)

    keys = sorted(accessor(min=tmin, max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return

    if minv_or_maxv:
        return

    # second run: last day until last hour
    tmax = tmin
    tmin = long(tmax - 23 * 3600 * 1e6)
    keys = sorted(accessor(min=tmin, max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return

    # final run: everything else
    tmax = tmin
    keys = sorted(accessor(max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return
