# coding=utf-8
from BTrees import LLBTree

import time


def longkeysortreverse(btreeish, minv=None, maxv=None, limit=None):
    """Performance optimized keyspace accessor.
    Returns an iterable of btreeish keys, reverse sorted by key.
    Expects a btreeish with long(microsec) keys.

    In case neither minv nor maxv is given, performs an optimization
    by not sorting the whole keyspace, but instead heuristically chunk
    the keyspace and sort only chunks, until the limit is reached.
    """
    try:
        accessor = btreeish.keys
    except AttributeError:
        accessor = LLBTree.TreeSet(btreeish).keys

    i = 0

    minv_or_maxv = minv or maxv

    if minv_or_maxv:
        # no optimization - chunking defined by parameters
        tmin = minv
        tmax = maxv
    else:
        # first auto-chunk: last hour
        tmax = long(time.time() * 1e6)
        tmin = long(tmax - 3600 * 1e6)

    keys = sorted(accessor(min=tmin, max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return  # no need to sort 2nd and 3rd chunks

    # unoptimized stops here even if under limit
    if minv_or_maxv:
        return

    # second auto-chunk: last day until last hour
    tmax = tmin
    tmin = long(tmax - 23 * 3600 * 1e6)
    keys = sorted(accessor(min=tmin, max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return  # no need to sort 3rd chunk

    # final auto-chunk: everything else
    tmax = tmin
    keys = sorted(accessor(max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return
