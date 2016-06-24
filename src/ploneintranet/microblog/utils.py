# coding=utf-8
from BTrees import LLBTree

import time


def longkeysortreverse(btreeish, minv=None, maxv=None, limit=None):
    """Performance optimized keyspace accessor.
    Returns an iterable of btreeish keys, reverse sorted by key.
    Expects a btreeish with long(microsec) keys.

    In case a limit, but neither minv nor maxv is given, optimizates
    by not sorting the whole keyspace, but instead heuristically chunk
    the keyspace and sort only chunks, until the limit is reached.

    The reason for this is that we want the most recent slice, which
    is last in the accessor, so we cannot just start iterating the slice.
    Basically we want to iterate backwards.
    """
    try:
        accessor = btreeish.keys
    except AttributeError:
        accessor = LLBTree.TreeSet(btreeish).keys

    if minv or limit is None:
        return _longkeysortreverse_direct(accessor, minv, maxv, limit)
    else:
        return _longkeysortreverse_optimized(accessor, maxv, limit)


def _longkeysortreverse_direct(accessor, minv, maxv, limit):
    """minv or limit is None: do not optimize"""
    i = 0
    keys = sorted(accessor(min=minv, max=maxv), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return  # reached limit
    return  # reached end of keyset


def _longkeysortreverse_optimized(accessor, maxv, limit):
    """not minv and limit is not None:
    Optimize by winding backward until limit is reached.
    This is the normal scenario: walking back 15 at a time.
    """
    i = 0

    # first auto-chunk: last hour
    if maxv:
        # no use searching for more recent updates than maxv
        tmin = long(maxv - 3600 * 1e6)
    else:
        tmin = long((time.time() - 3600) * 1e6)
    keys = sorted(accessor(min=tmin, max=maxv), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return  # no need to sort 2nd and 3rd chunks

    # second auto-chunk: last day until last hour
    tmax = tmin - 1  # avoid off-by-one error
    tmin = long(tmax - 23 * 3600 * 1e6)
    keys = sorted(accessor(min=tmin, max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return  # no need to sort 3rd chunk

    # final auto-chunk: everything else
    tmax = tmin - 1  # avoid off-by-one error
    keys = sorted(accessor(max=tmax), reverse=True)
    for key in keys:
        yield key
        i += 1
        if i == limit:
            return
