from Products.CMFCore.interfaces import IContentish
from plone.indexer import indexer

from ploneintranet import api as pi_api


@indexer(IContentish)
def has_thumbs(obj):
    """
    Does this item have preview thumbnails?
    """
    return pi_api.previews.has_previews(obj)
