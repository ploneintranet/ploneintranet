# coding=utf-8
"""
Utilities for general purposes. Meant to be imported from other packages
and have no dependencies of other packages
"""

from Products.CMFPlone.utils import safe_unicode
from plone import api
from logging import getLogger


logger = getLogger(__name__)


def shorten(text, length=20, ellipsis=u'\u2026'):
    text = text.replace('_', ' ').replace('-', ' ')
    if len(text) <= length:
        return text
    if ' ' not in text:
        return u'%s %s' % (safe_unicode(text[:length - 4]), ellipsis)
    return u" ".join(safe_unicode(text)[:length].split(" ")[:-1] + [ellipsis])


def get_record_from_registry(record, fallback=[]):
        ''' Returns a record from the registry

        If we do not have the record in the registry return the fallback tiles
        '''
        try:
            return api.portal.get_registry_record(record)
        except api.exc.InvalidParameterError:
            logger.warning(
                (
                    'Cannot find registry record: %s. '
                    'Check that ploneintranet.layout has been upgraded'
                ),
                record,
            )
            return fallback
