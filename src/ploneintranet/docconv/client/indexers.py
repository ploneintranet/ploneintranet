from Products.CMFCore.interfaces import IContentish
from plone.indexer import indexer
from ploneintranet.docconv.client.interfaces import IDocconv


@indexer(IContentish)
def has_thumbs(obj):
    """
    Does this item have preview thumbnails?
    """
    return IDocconv(obj).has_thumbs()
