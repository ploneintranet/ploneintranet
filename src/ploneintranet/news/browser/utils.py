# -*- coding: utf-8 -*-


def obj2dict(obj, *keys, **keyvalues):
    _dict = dict(obj=obj)
    for k in keys:
        attr = getattr(obj, k)
        if callable(attr):
            # e.g. absolute_url
            _dict[k] = attr()
        else:
            _dict[k] = attr
    for (key, value) in keyvalues.items():
        _dict[key] = value
    _dict['obj'] = obj
    return _dict
