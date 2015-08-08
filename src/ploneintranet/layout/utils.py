"""
Utilities for general purposes. Meant to be imported from other packages
and have no dependencies of other packages
"""

from Products.CMFPlone.utils import safe_unicode


def shorten(text, length=20, ellipse=u'\u2026'):
    text = text.replace('_', ' ').replace('-', ' ')
    if len(text) <= length:
        return text
    if ' ' not in text:
        return u'%s %s' % (safe_unicode(text[:length - 4]), ellipse)
    return u" ".join(safe_unicode(text)[:length].split(" ")[:-1] + [ellipse])
